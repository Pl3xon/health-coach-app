import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_AUTH_CODE = os.environ.get("GOOGLE_AUTH_CODE", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "https://health-coach-app-sable.vercel.app/auth/google-fit")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
RENPHO_EMAIL = os.environ.get("RENPHO_EMAIL", "")
RENPHO_PASSWORD = os.environ.get("RENPHO_PASSWORD", "")
YAZIO_EMAIL = os.environ.get("YAZIO_EMAIL", "")
YAZIO_PASSWORD = os.environ.get("YAZIO_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "health-coach-secret-key-2026")
