import os

# API URL - wird nach Deploy angepasst
# Lokal: leer lassen
# Nach Render Deploy: https://vitalcoach-api.onrender.com
API_URL = os.environ.get("VITE_API_URL", "")

def get_api_url():
    return API_URL
