from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import json
import time
import os

from config import GOOGLE_REDIRECT_URI, YAZIO_EMAIL
from services.storage import (
    get_or_create_profile, save_profile, get_chat_history, save_chat_message,
    list_users, get_user, create_user, update_user, delete_user,
)
from services.manager import (
    get_renpho_client, get_google_fit_client, save_gf_tokens_for_user,
    get_yazio_client, save_yazio_tokens_for_user,
    get_google_health_client,
    get_gemini_coach,
)
from services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="VitalCoach", version="3.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "3.1.0",
    }


@app.post("/api/refresh")
async def manual_refresh():
    from services.scheduler import refresh_all_users
    await refresh_all_users()
    return {"success": True}


class UserCreate(BaseModel):
    id: str
    name: str
    renpho_email: Optional[str] = ""
    renpho_password: Optional[str] = ""
    yazio_email: Optional[str] = ""
    yazio_password: Optional[str] = ""


class UserUpdate(BaseModel):
    name: Optional[str] = None
    renpho_email: Optional[str] = None
    renpho_password: Optional[str] = None
    yazio_email: Optional[str] = None
    yazio_password: Optional[str] = None


@app.get("/api/users")
async def api_list_users():
    return {"users": list_users()}


@app.get("/api/users/{user_id}")
async def api_get_user(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/users")
async def api_create_user(data: UserCreate):
    user = create_user(
        data.id, data.name,
        data.renpho_email, data.renpho_password,
        data.yazio_email, data.yazio_password,
    )
    return user


@app.put("/api/users/{user_id}")
async def api_update_user(user_id: str, data: UserUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    user = update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/api/users/{user_id}")
async def api_delete_user(user_id: str):
    if delete_user(user_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    return get_or_create_profile(user_id)


class UserProfileUpdate(BaseModel):
    user_id: str = "default"
    name: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    goals: Optional[List[str]] = None
    fitness_level: Optional[str] = None
    activity_level: Optional[str] = None


@app.post("/api/profile")
async def update_profile(update: UserProfileUpdate):
    profile = get_or_create_profile(update.user_id)
    update_dict = update.dict(exclude_none=True)
    del update_dict["user_id"]
    profile.update(update_dict)
    save_profile(update.user_id, profile)
    return {"success": True, "profile": profile}


class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"


@app.post("/api/chat")
async def chat(message: ChatMessage):
    gemini_coach = get_gemini_coach()
    if not gemini_coach:
        return {"response": "Der AI Coach ist noch nicht konfiguriert. Bitte trage einen gültigen Gemini API-Key in den Render Environment Variables ein (GEMINI_API_KEY). Du bekommst ihn unter https://aistudio.google.com/apikey"}

    try:
        profile = get_or_create_profile(message.user_id)
        health_data = {"profile": profile}

        renpho = get_renpho_client(message.user_id)
        if renpho:
            try:
                if renpho.login():
                    rd = renpho.get_latest_measurement()
                    if rd:
                        health_data["renpho"] = rd
            except:
                pass

        gf = get_google_fit_client(message.user_id)
        if gf and gf.is_connected():
            try:
                health_data["google_fit"] = gf.get_all_vital_data()
            except:
                pass

        response = gemini_coach.chat_with_health_data(message.message, health_data)
        save_chat_message(message.user_id, "user", message.message, time.time())
        save_chat_message(message.user_id, "assistant", response, time.time())
        return {"response": response}
    except Exception as e:
        return {"response": f"Fehler: {str(e)}. Bitte Gemini API-Key prüfen."}


@app.get("/api/chat/history/{user_id}")
async def chat_history(user_id: str):
    return {"messages": get_chat_history(user_id)}


@app.get("/api/renpho/status")
async def renpho_status(user_id: str = "default"):
    renpho = get_renpho_client(user_id)
    if not renpho:
        return {"connected": False, "error": "Keine Renpho-Zugangsdaten für diesen User"}
    try:
        success = renpho.login()
        return {"connected": success}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/api/renpho/latest")
async def renpho_latest(user_id: str = "default"):
    renpho = get_renpho_client(user_id)
    if not renpho:
        return {"measurement": None, "error": "Keine Renpho-Zugangsdaten"}
    try:
        if not renpho.user_id:
            renpho.login()
        return {"measurement": renpho.get_latest_measurement()}
    except Exception as e:
        return {"measurement": None, "error": str(e)}


@app.post("/api/nutrition/plan")
async def generate_nutrition_plan(user_id: str = "default"):
    gemini_coach = get_gemini_coach()
    if not gemini_coach:
        return {"plan": "Der AI Coach ist noch nicht konfiguriert."}
    try:
        profile = get_or_create_profile(user_id)
        plan = gemini_coach.generate_nutrition_plan(
            weight=profile.get("weight", 80),
            height=profile.get("height", 180),
            age=profile.get("age", 28),
            gender=profile.get("gender", "männlich"),
            goal=", ".join(profile.get("goals", ["Abnehmen"])),
            activity_level=profile.get("activity_level", "Moderat")
        )
        return {"plan": plan}
    except Exception as e:
        return {"plan": f"Fehler: {str(e)}"}


@app.post("/api/workout/plan")
async def generate_workout_plan(user_id: str = "default"):
    gemini_coach = get_gemini_coach()
    if not gemini_coach:
        return {"plan": "Der AI Coach ist noch nicht konfiguriert."}
    try:
        profile = get_or_create_profile(user_id)
        plan = gemini_coach.generate_workout_plan(
            fitness_level=profile.get("fitness_level", "Anfänger"),
            goal=", ".join(profile.get("goals", ["Abnehmen"])),
            days_per_week=4
        )
        return {"plan": plan}
    except Exception as e:
        return {"plan": f"Fehler: {str(e)}"}


@app.get("/api/google-fit/url")
async def google_fit_auth_url(user_id: str = "default"):
    gf = get_google_fit_client(user_id)
    if not gf:
        return {"url": None, "error": "Google Fit nicht initialisiert"}
    url = gf.get_auth_url()
    return {"url": url, "user_id": user_id}


class GoogleFitCallback(BaseModel):
    code: str
    user_id: str = "default"


@app.post("/api/google-fit/callback")
async def google_fit_callback(cb: GoogleFitCallback):
    gf = get_google_fit_client(cb.user_id)
    if not gf:
        return {"success": False, "error": "Google Fit nicht initialisiert"}
    result = gf.exchange_code(cb.code)
    if result.get("success"):
        save_gf_tokens_for_user(cb.user_id, gf)
    return result


@app.get("/api/google-fit/status")
async def google_fit_status(user_id: str = "default"):
    gf = get_google_fit_client(user_id)
    if not gf:
        return {"connected": False}
    return {"connected": gf.is_connected()}


@app.get("/api/google-fit/history")
async def google_fit_history(user_id: str = "default", days: int = 30):
    data = None

    gf = get_google_fit_client(user_id)
    if gf and gf.access_token:
        try:
            data = gf.get_health_history(days)
        except:
            pass

    gh = get_google_health_client(user_id)
    if gh and gh.is_connected():
        try:
            gh_data = gh.get_health_history(days)
            if not data:
                data = gh_data
            else:
                for key in ["resting_heart_rate", "hrv", "spo2", "active_zone_minutes"]:
                    if key in gh_data:
                        gh_has_values = any(d.get("value", 0) > 0 for d in gh_data[key])
                        if gh_has_values:
                            gf_has_values = any(d.get("value", 0) > 0 for d in data.get(key, []))
                            if not gf_has_values:
                                data[key] = gh_data[key]
        except:
            pass

    if not data:
        return {"data": None}
    return {"data": data}


@app.get("/api/yazio/status")
async def yazio_status(user_id: str = "default"):
    user = get_user(user_id)
    has_yazio_creds = False
    if user:
        has_yazio_creds = bool(user.get("yazio_email")) or bool(YAZIO_EMAIL)
    yazio = get_yazio_client(user_id)
    if not yazio:
        return {"connected": False, "has_credentials": has_yazio_creds}
    return {"connected": yazio.is_connected(), "has_credentials": has_yazio_creds}


@app.get("/api/yazio/daily")
async def yazio_daily(user_id: str = "default", date: str = None):
    yazio = get_yazio_client(user_id)
    if not yazio:
        return {"data": None, "error": "Yazio nicht verbunden. Bitte Yazio-Zugangsdaten im Profil eintragen oder YAZIO_EMAIL/YAZIO_PASSWORD in Render ENV setzen."}
    if not date:
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=2))
        date = datetime.now(tz).strftime("%Y-%m-%d")
    try:
        data = yazio.get_daily_summary(date)
        return {"data": data}
    except Exception as e:
        return {"data": None, "error": str(e)}


@app.get("/api/yazio/diary")
async def yazio_diary(user_id: str = "default", date: str = None):
    yazio = get_yazio_client(user_id)
    if not yazio:
        return {"data": None, "error": "Yazio nicht verbunden"}
    if not date:
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=2))
        date = datetime.now(tz).strftime("%Y-%m-%d")
    try:
        data = yazio.get_consumed_items(date)
        return {"data": data}
    except Exception as e:
        return {"data": None, "error": str(e)}


@app.get("/api/fitbit/url")
async def fitbit_auth_url(user_id: str = "default"):
    return {"url": None, "error": "Fitbit wird jetzt über Google Health API abgerufen. Bitte Google Fit neu verbinden."}


@app.post("/api/fitbit/callback")
async def fitbit_callback(code: str = "", user_id: str = "default"):
    return {"success": False, "error": "Fitbit wird jetzt über Google Health API abgerufen."}


@app.get("/api/fitbit/status")
async def fitbit_status(user_id: str = "default"):
    gh = get_google_health_client(user_id)
    if not gh:
        return {"connected": False, "has_config": False}
    return {"connected": gh.is_connected(), "has_config": True}


@app.get("/api/fitbit/vitals")
async def fitbit_vitals(user_id: str = "default"):
    gh = get_google_health_client(user_id)
    if not gh or not gh.is_connected():
        return {"data": None}
    try:
        data = gh.get_all_vital_data()
        return {"data": data}
    except Exception as e:
        return {"data": None, "error": str(e)}


@app.get("/api/fitbit/history")
async def fitbit_history(user_id: str = "default", days: int = 30):
    gh = get_google_health_client(user_id)
    if not gh or not gh.is_connected():
        return {"data": None}
    try:
        data = gh.get_health_history(days)
        return {"data": data}
    except Exception as e:
        return {"data": None, "error": str(e)}


@app.get("/api/debug/health")
async def debug_health(user_id: str = "default"):
    gh = get_google_health_client(user_id)
    if not gh:
        return {"error": "Google Health Client nicht vorhanden", "has_config": bool(GOOGLE_CLIENT_ID)}
    if not gh._ensure_token():
        return {"error": "Token fehlt oder Refresh fehlgeschlagen", "has_refresh_token": bool(gh.refresh_token)}

    headers = gh._get_headers()
    base = gh.BASE_URL
    wearable_family = "users/me/dataSourceFamilies/google-wearables"

    debug = {"token_ok": True, "raw_responses": {}}

    import httpx as _hx
    c = _hx.Client(timeout=15.0)

    from datetime import datetime as _dt, timezone as _tz, timedelta as _td
    tz = _tz(_td(hours=2))
    today = _dt.now(tz).strftime("%Y-%m-%d")

    list_resp = c.get(f"{base}/users/me/dataTypes", headers=headers)
    debug["raw_responses"]["_dataTypes_list"] = {
        "status": list_resp.status_code,
        "body": list_resp.text[:3000],
    }

    data_types_to_try = [
        ("daily-resting-heart-rate", f'daily_resting_heart_rate.civil_start_time >= "{today}"'),
        ("heart-rate", f'heart_rate.observation_time.physical_time >= "{today}T00:00:00Z"'),
        ("daily-heart-rate-variability", f'daily_heart_rate_variability.civil_start_time >= "{today}"'),
        ("daily-oxygen-saturation", f'daily_oxygen_saturation.civil_start_time >= "{today}"'),
        ("sleep", f'sleep.interval.civil_end_time >= "{today}"'),
        ("active-zone-minutes", f'active_zone_minutes.interval.civil_start_time >= "{today}"'),
        ("steps", f'steps.interval.civil_start_time >= "{today}"'),
        ("active-energy-burned", f'active_energy_burned.interval.civil_start_time >= "{today}"'),
    ]

    for dt, filt in data_types_to_try:
        list_url = f"{base}/users/me/dataTypes/{dt}/dataPoints"
        list_resp = c.get(list_url, params={"filter": filt} if filt else None, headers=headers)

        reconcile_url = f"{base}/users/me/dataTypes/{dt}/dataPoints:reconcile"
        reconcile_resp = c.get(reconcile_url, params={"dataSourceFamily": wearable_family, "filter": filt} if filt else {"dataSourceFamily": wearable_family}, headers=headers)

        debug["raw_responses"][dt] = {
            "list": {"status": list_resp.status_code, "count": len(list_resp.json().get("dataPoints", [])) if list_resp.status_code == 200 else None, "error": list_resp.text[:500] if list_resp.status_code != 200 else None},
            "reconcile": {"status": reconcile_resp.status_code, "count": len(reconcile_resp.json().get("dataPoints", [])) if reconcile_resp.status_code == 200 else None, "error": reconcile_resp.text[:500] if reconcile_resp.status_code != 200 else None},
        }

    return debug


@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    profile = get_or_create_profile(user_id)
    dashboard = {"profile": profile, "renpho": {"connected": False, "latest": None}, "google_fit": None, "yazio": None}

    renpho = get_renpho_client(user_id)
    if renpho:
        try:
            if renpho.login():
                dashboard["renpho"]["connected"] = True
                dashboard["renpho"]["latest"] = renpho.get_latest_measurement()
        except:
            pass

    gf = get_google_fit_client(user_id)
    if gf and gf.access_token:
        try:
            dashboard["google_fit"] = gf.get_all_vital_data()
        except:
            pass

    gh = get_google_health_client(user_id)
    if gh and gh.is_connected():
        try:
            gh_data = gh.get_all_vital_data()
            if not dashboard["google_fit"]:
                dashboard["google_fit"] = gh_data
            else:
                gf_data = dashboard["google_fit"]
                if not gf_data.get("heart_rate"):
                    gf_data["heart_rate"] = gh_data.get("resting_heart_rate", 0)
                if not gf_data.get("sleep_hours"):
                    gf_data["sleep_hours"] = gh_data.get("sleep_hours", 0)
                if not gf_data.get("resting_heart_rate"):
                    gf_data["resting_heart_rate"] = gh_data.get("resting_heart_rate", 0)
                if not gf_data.get("hrv"):
                    gf_data["hrv"] = gh_data.get("hrv", 0)
                if not gf_data.get("spo2"):
                    gf_data["spo2"] = gh_data.get("spo2", 0)
                if not gf_data.get("active_zone_minutes"):
                    gf_data["active_zone_minutes"] = gh_data.get("active_zone_minutes", 0)
        except:
            pass

    yazio = get_yazio_client(user_id)
    if yazio and yazio.is_connected():
        try:
            from datetime import datetime, timezone, timedelta
            tz = timezone(timedelta(hours=2))
            today = datetime.now(tz).strftime("%Y-%m-%d")
            dashboard["yazio"] = yazio.get_daily_summary(today)
        except:
            pass

    return dashboard


static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
