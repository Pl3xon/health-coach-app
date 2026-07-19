import json
import os
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_lock = threading.Lock()


def _path(filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)


def load(filename: str, default=None):
    with _lock:
        p = _path(filename)
        if not os.path.exists(p):
            return default if default is not None else {}
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)


def save(filename: str, data):
    with _lock:
        p = _path(filename)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_profile(user_id: str) -> dict:
    profiles = load("profiles.json", {})
    return profiles.get(user_id)


def save_profile(user_id: str, profile: dict):
    profiles = load("profiles.json", {})
    profiles[user_id] = profile
    save("profiles.json", profiles)


def get_chat_history(user_id: str) -> list:
    history = load("chat_history.json", {})
    return history.get(user_id, [])


def save_chat_message(user_id: str, role: str, content: str, timestamp: float):
    history = load("chat_history.json", {})
    if user_id not in history:
        history[user_id] = []
    history[user_id].append({
        "role": role,
        "content": content,
        "timestamp": timestamp,
    })
    history[user_id] = history[user_id][-50:]
    save("chat_history.json", history)


DEFAULT_PROFILE = {
    "name": "Kevin",
    "weight": 80,
    "height": 180,
    "age": 28,
    "gender": "männlich",
    "goals": ["Abnehmen", "Muskelaufbau", "Bauch weg"],
    "fitness_level": "Anfänger",
    "activity_level": "Moderat",
}


def get_or_create_profile(user_id: str) -> dict:
    profile = get_profile(user_id)
    if not profile:
        profile = DEFAULT_PROFILE.copy()
        save_profile(user_id, profile)
    return profile
