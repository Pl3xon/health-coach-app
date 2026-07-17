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
from services.renpho import RenphoClient
from services.google_fit import GoogleFitClient
from services.gemini_coach import GeminiCoach

app = FastAPI(title="VitalCoach", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lokaler Storage (Dictionary statt Datenbank)
local_db = {
    "profiles": {},
    "chat_history": {}
}

# Services
renpho_client = RenphoClient(RENPHO_EMAIL, RENPHO_PASSWORD)
google_fit_client = GoogleFitClient(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
gemini_coach = GeminiCoach(GEMINI_API_KEY)


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
    # Nur letzte 50 Nachrichten behalten
    local_db["chat_history"][user_id] = local_db["chat_history"][user_id][-50:]


def get_chat_history(user_id: str) -> list:
    return local_db["chat_history"].get(user_id, [])


# ============ API ROUTES ============

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


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
    try:
        profile = get_user_profile(message.user_id)
        health_data = {"profile": profile}

        try:
            if not renpho_client.user_id:
                renpho_client.login()
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{user_id}")
async def chat_history(user_id: str):
    return {"messages": get_chat_history(user_id)}


@app.get("/api/renpho/status")
async def renpho_status():
    try:
        success = renpho_client.login()
        return {"connected": success}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/api/renpho/latest")
async def renpho_latest():
    try:
        if not renpho_client.user_id:
            renpho_client.login()
        return {"measurement": renpho_client.get_latest_measurement()}
    except Exception as e:
        return {"measurement": None, "error": str(e)}


@app.post("/api/nutrition/plan")
async def generate_nutrition_plan(user_id: str = "default"):
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workout/plan")
async def generate_workout_plan(user_id: str = "default"):
    try:
        profile = get_user_profile(user_id)
        plan = gemini_coach.generate_workout_plan(
            fitness_level=profile.get("fitness_level", "Anfänger"),
            goal=", ".join(profile.get("goals", ["Abnehmen"])),
            days_per_week=4
        )
        return {"plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    profile = get_user_profile(user_id)
    dashboard = {"profile": profile, "renpho": {"connected": False, "latest": None}}
    try:
        if renpho_client.login():
            dashboard["renpho"]["connected"] = True
            dashboard["renpho"]["latest"] = renpho_client.get_latest_measurement()
    except:
        pass
    return dashboard


# ============ SERVE FRONTEND ============

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
