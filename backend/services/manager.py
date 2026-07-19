from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, RENPHO_EMAIL, RENPHO_PASSWORD, YAZIO_EMAIL, YAZIO_PASSWORD
from services.storage import get_user, get_google_fit_tokens, save_google_fit_tokens, get_yazio_tokens, save_yazio_tokens


_repho_clients = {}
_google_fit_clients = {}
_yazio_clients = {}


def get_renpho_client(user_id: str):
    user = get_user(user_id)
    if not user:
        return None
    email = user.get("renpho_email", "") or RENPHO_EMAIL
    password = user.get("renpho_password", "") or RENPHO_PASSWORD
    if not email or not password:
        return None

    cached = _repho_clients.get(user_id)
    if cached:
        return cached

    from services.renpho import RenphoClient
    client = RenphoClient(email, password)
    _repho_clients[user_id] = client
    return client


def get_google_fit_client(user_id: str):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None

    cached = _google_fit_clients.get(user_id)
    if cached:
        if cached._ensure_token():
            save_google_fit_tokens(user_id, {
                "access_token": cached.access_token,
                "refresh_token": cached.refresh_token,
                "token_expiry": cached.token_expiry,
            })
            return cached
        del _google_fit_clients[user_id]

    tokens = get_google_fit_tokens(user_id)
    access_token = tokens.get("access_token") if tokens else None
    refresh_token = tokens.get("refresh_token") if tokens else None
    token_expiry = tokens.get("token_expiry", 0) if tokens else 0

    from services.google_fit import GoogleFitClient
    client = GoogleFitClient(
        GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
        access_token=access_token, refresh_token=refresh_token,
        token_expiry=token_expiry, user_id=user_id,
    )
    _google_fit_clients[user_id] = client
    return client


def save_gf_tokens_for_user(user_id: str, client):
    save_google_fit_tokens(user_id, {
        "access_token": client.access_token,
        "refresh_token": client.refresh_token,
        "token_expiry": client.token_expiry,
    })


def get_yazio_client(user_id: str):
    user = get_user(user_id)
    if not user:
        return None

    cached = _yazio_clients.get(user_id)
    if cached:
        if cached._ensure_token():
            save_yazio_tokens(user_id, {
                "access_token": cached.access_token,
                "refresh_token": cached.refresh_token,
                "token_expiry": cached.token_expiry,
            })
            return cached
        del _yazio_clients[user_id]

    tokens = get_yazio_tokens(user_id)
    access_token = tokens.get("access_token") if tokens else None
    refresh_token = tokens.get("refresh_token") if tokens else None
    token_expiry = tokens.get("token_expiry", 0) if tokens else 0

    from services.yazio import YazioClient
    client = YazioClient(
        access_token=access_token, refresh_token=refresh_token,
        token_expiry=token_expiry, user_id=user_id,
    )

    if not client._ensure_token():
        yazio_email = user.get("yazio_email", "") or YAZIO_EMAIL
        yazio_password = user.get("yazio_password", "") or YAZIO_PASSWORD
        if yazio_email and yazio_password:
            if client.login(yazio_email, yazio_password):
                save_yazio_tokens(user_id, {
                    "access_token": client.access_token,
                    "refresh_token": client.refresh_token,
                    "token_expiry": client.token_expiry,
                })
                _yazio_clients[user_id] = client
                return client
        return None

    _yazio_clients[user_id] = client
    return client


def save_yazio_tokens_for_user(user_id: str, client):
    save_yazio_tokens(user_id, {
        "access_token": client.access_token,
        "refresh_token": client.refresh_token,
        "token_expiry": client.token_expiry,
    })


_gemini_coach = None


def get_gemini_coach():
    global _gemini_coach
    if _gemini_coach:
        return _gemini_coach
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        return None
    from services.gemini_coach import GeminiCoach
    _gemini_coach = GeminiCoach(GEMINI_API_KEY)
    return _gemini_coach
