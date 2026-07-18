from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import time
import os

from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_AUTH_CODE,
    GEMINI_API_KEY, RENPHO_EMAIL, RENPHO_PASSWORD
)

app = FastAPI(title="VitalCoach", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

local_db = {
    "profiles": {},
    "chat_history": {}
}

# Services lazy initialisieren
renpho_client = None
google_fit_client = None
gemini_coach = None


GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "https://health-coach-app-sable.vercel.app/auth/google-fit")


def init_services():
    global renpho_client, google_fit_client, gemini_coach
    try:
        from services.renpho import RenphoClient
        renpho_client = RenphoClient(RENPHO_EMAIL, RENPHO_PASSWORD)
    except Exception as e:
        print(f"Renpho init error: {e}")

    try:
        from services.google_fit import GoogleFitClient
        google_fit_client = GoogleFitClient(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)
    except Exception as e:
        print(f"Google Fit init error: {e}")

    try:
        from services.gemini_coach import GeminiCoach
        gemini_coach = GeminiCoach(GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini init error: {e}")


init_services()


class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"


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


DEFAULT_PROFILE = {
    "name": "Kevin",
    "weight": 80,
    "height": 180,
    "age": 28,
    "gender": "männlich",
    "goals": ["Abnehmen", "Muskelaufbau", "Bauch weg"],
    "fitness_level": "Anfänger",
    "activity_level": "Moderat"
}


def get_user_profile(user_id: str) -> dict:
    if user_id not in local_db["profiles"]:
        local_db["profiles"][user_id] = DEFAULT_PROFILE.copy()
    return local_db["profiles"][user_id]


def save_user_profile(user_id: str, profile: dict):
    local_db["profiles"][user_id] = profile


def save_chat_message(user_id: str, role: str, content: str):
    if user_id not in local_db["chat_history"]:
        local_db["chat_history"][user_id] = []
    local_db["chat_history"][user_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })
    local_db["chat_history"][user_id] = local_db["chat_history"][user_id][-50:]


def get_chat_history(user_id: str) -> list:
    return local_db["chat_history"].get(user_id, [])


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "gemini": gemini_coach is not None,
        "renpho": renpho_client is not None,
        "google_fit": google_fit_client is not None,
        "gemini_key_set": bool(GEMINI_API_KEY),
    }


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    return get_user_profile(user_id)


@app.post("/api/profile")
async def update_profile(update: UserProfileUpdate):
    profile = get_user_profile(update.user_id)
    update_dict = update.dict(exclude_none=True)
    del update_dict["user_id"]
    profile.update(update_dict)
    save_user_profile(update.user_id, profile)
    return {"success": True, "profile": profile}


@app.post("/api/chat")
async def chat(message: ChatMessage):
    if not gemini_coach:
        return {"response": "Der AI Coach ist noch nicht konfiguriert. Bitte trage einen gültigen Gemini API-Key in den Render Environment Variables ein (GEMINI_API_KEY). Du bekommst ihn unter https://aistudio.google.com/apikey"}

    try:
        profile = get_user_profile(message.user_id)
        health_data = {"profile": profile}

        try:
            if renpho_client and not renpho_client.user_id:
                renpho_client.login()
            if renpho_client:
                renpho_data = renpho_client.get_latest_measurement()
                if renpho_data:
                    health_data["renpho"] = renpho_data
        except:
            pass

        response = gemini_coach.chat_with_health_data(message.message, health_data)
        save_chat_message(message.user_id, "user", message.message)
        save_chat_message(message.user_id, "assistant", response)
        return {"response": response}
    except Exception as e:
        return {"response": f"Fehler: {str(e)}. Bitte Gemini API-Key prüfen."}


@app.get("/api/chat/history/{user_id}")
async def chat_history(user_id: str):
    return {"messages": get_chat_history(user_id)}


@app.get("/api/renpho/status")
async def renpho_status():
    if not renpho_client:
        return {"connected": False, "error": "Renpho Service nicht initialisiert"}
    try:
        success = renpho_client.login()
        return {"connected": success}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/api/renpho/latest")
async def renpho_latest():
    if not renpho_client:
        return {"measurement": None, "error": "Renpho Service nicht initialisiert"}
    try:
        if not renpho_client.user_id:
            renpho_client.login()
        return {"measurement": renpho_client.get_latest_measurement()}
    except Exception as e:
        return {"measurement": None, "error": str(e)}


@app.post("/api/nutrition/plan")
async def generate_nutrition_plan(user_id: str = "default"):
    if not gemini_coach:
        return {"plan": "Der AI Coach ist noch nicht konfiguriert. Bitte trage einen gültigen Gemini API-Key in den Render Environment Variables ein (GEMINI_API_KEY). Du bekommst ihn unter https://aistudio.google.com/apikey"}
    try:
        profile = get_user_profile(user_id)
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
    if not gemini_coach:
        return {"plan": "Der AI Coach ist noch nicht konfiguriert. Bitte trage einen gültigen Gemini API-Key in den Render Environment Variables ein (GEMINI_API_KEY). Du bekommst ihn unter https://aistudio.google.com/apikey"}
    try:
        profile = get_user_profile(user_id)
        plan = gemini_coach.generate_workout_plan(
            fitness_level=profile.get("fitness_level", "Anfänger"),
            goal=", ".join(profile.get("goals", ["Abnehmen"])),
            days_per_week=4
        )
        return {"plan": plan}
    except Exception as e:
        return {"plan": f"Fehler: {str(e)}"}


@app.get("/api/google-fit/url")
async def google_fit_auth_url():
    if not google_fit_client:
        return {"url": None, "error": "Google Fit nicht initialisiert"}
    url = google_fit_client.get_auth_url()
    return {"url": url}


class GoogleFitCallback(BaseModel):
    code: str


@app.post("/api/google-fit/callback")
async def google_fit_callback(cb: GoogleFitCallback):
    if not google_fit_client:
        return {"success": False, "error": "Google Fit nicht initialisiert"}
    result = google_fit_client.exchange_code(cb.code)
    return result


@app.get("/api/google-fit/status")
async def google_fit_status():
    if not google_fit_client:
        return {"connected": False}
    return {"connected": google_fit_client.is_connected()}


@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    profile = get_user_profile(user_id)
    dashboard = {"profile": profile, "renpho": {"connected": False, "latest": None}, "google_fit": None}

    if renpho_client:
        try:
            if renpho_client.login():
                dashboard["renpho"]["connected"] = True
                dashboard["renpho"]["latest"] = renpho_client.get_latest_measurement()
        except:
            pass

    if google_fit_client and google_fit_client.access_token:
        try:
            gf_data = google_fit_client.get_all_vital_data()
            dashboard["google_fit"] = gf_data
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
