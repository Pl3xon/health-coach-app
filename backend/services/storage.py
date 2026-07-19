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


def list_users() -> list:
    users = load("users.json", [])
    if not users:
        users = [{"id": "default", "name": "Kevin"}]
        save("users.json", users)
    return users


def get_user(user_id: str) -> dict | None:
    users = list_users()
    for u in users:
        if u["id"] == user_id:
            return u
    return None


def create_user(user_id: str, name: str, renpho_email: str = "", renpho_password: str = "", yazio_email: str = "", yazio_password: str = "") -> dict:
    users = list_users()
    for u in users:
        if u["id"] == user_id:
            return u
    user = {
        "id": user_id,
        "name": name,
        "renpho_email": renpho_email,
        "renpho_password": renpho_password,
        "yazio_email": yazio_email,
        "yazio_password": yazio_password,
    }
    users.append(user)
    save("users.json", users)
    save_profile(user_id, DEFAULT_PROFILE.copy())
    return user


def update_user(user_id: str, data: dict) -> dict | None:
    users = list_users()
    for u in users:
        if u["id"] == user_id:
            u.update(data)
            save("users.json", users)
            return u
    return None


def delete_user(user_id: str) -> bool:
    users = list_users()
    new_users = [u for u in users if u["id"] != user_id]
    if len(new_users) < len(users):
        save("users.json", new_users)
        return True
    return False


def get_google_fit_tokens(user_id: str) -> dict | None:
    tokens = load("google_fit_tokens.json", {})
    return tokens.get(user_id)


def save_google_fit_tokens(user_id: str, tokens: dict):
    all_tokens = load("google_fit_tokens.json", {})
    all_tokens[user_id] = tokens
    save("google_fit_tokens.json", all_tokens)


def get_yazio_tokens(user_id: str) -> dict | None:
    tokens = load("yazio_tokens.json", {})
    return tokens.get(user_id)


def save_yazio_tokens(user_id: str, tokens: dict):
    all_tokens = load("yazio_tokens.json", {})
    all_tokens[user_id] = tokens
    save("yazio_tokens.json", all_tokens)


def get_fitbit_tokens(user_id: str) -> dict | None:
    tokens = load("fitbit_tokens.json", {})
    return tokens.get(user_id)


def save_fitbit_tokens(user_id: str, tokens: dict):
    all_tokens = load("fitbit_tokens.json", {})
    all_tokens[user_id] = tokens
    save("fitbit_tokens.json", all_tokens)


def get_google_health_tokens(user_id: str) -> dict | None:
    tokens = load("google_health_tokens.json", {})
    return tokens.get(user_id)


def save_google_health_tokens(user_id: str, tokens: dict):
    all_tokens = load("google_health_tokens.json", {})
    all_tokens[user_id] = tokens
    save("google_health_tokens.json", all_tokens)

