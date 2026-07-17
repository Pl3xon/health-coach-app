import os

# API Keys werden als Environment Variables geladen
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_AUTH_CODE = os.environ.get("GOOGLE_AUTH_CODE", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
RENPHO_EMAIL = os.environ.get("RENPHO_EMAIL", "")
RENPHO_PASSWORD = os.environ.get("RENPHO_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "health-coach-secret-key-2026")
