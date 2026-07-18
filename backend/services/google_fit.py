import httpx
import time
import json
import os
from typing import Optional


class GoogleFitClient:
    BASE_URL = "https://www.googleapis.com/fitness/v1"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.nutrition.read",
    ]

    TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "google_fit_tokens.json")

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        self.client = httpx.Client(timeout=30.0)
        self._load_tokens()

    def _load_tokens(self):
        try:
            if os.path.exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, "r") as f:
                    data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.token_expiry = data.get("token_expiry", 0)
                if self.refresh_token:
                    print("Google Fit tokens loaded from file")
        except Exception as e:
            print(f"Error loading Google Fit tokens: {e}")

    def _save_tokens(self):
        try:
            with open(self.TOKEN_FILE, "w") as f:
                json.dump({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "token_expiry": self.token_expiry,
                }, f)
            print("Google Fit tokens saved to file")
        except Exception as e:
            print(f"Error saving Google Fit tokens: {e}")

    def get_auth_url(self) -> str:
        scopes = "+".join(self.SCOPES)
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&access_type=offline"
            f"&prompt=consent"
        )

    def exchange_code(self, auth_code: str) -> dict:
        try:
            resp = self.client.post(
                self.TOKEN_URL,
                data={
                    "code": auth_code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                expires_in = data.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in - 300
                self._save_tokens()
                return {"success": True}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_tokens(self, access_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = time.time() + 3600
        self._save_tokens()

    def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False
        try:
            resp = self.client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in - 300
                self._save_tokens()
                return True
            return False
        except Exception:
            return False

    def _ensure_token(self) -> bool:
        if not self.access_token:
            if self.refresh_token:
                return self.refresh_access_token()
            return False
        if time.time() > self.token_expiry and self.refresh_token:
            return self.refresh_access_token()
        return True

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def aggregate_data(self, data_type: str, start_ms: int, end_ms: int) -> list:
        if not self._ensure_token():
            return []
        try:
            body = {
                "aggregateBy": [{"dataTypeName": data_type}],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms,
            }
            resp = self.client.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                json=body,
                headers=self._get_headers(),
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("bucket", [])
            return []
        except Exception:
            return []

    def get_steps(self, days: int = 1) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.step_count.delta", start_ms, end_ms)

    def get_heart_rate(self, days: int = 7) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.heart_rate.bpm", start_ms, end_ms)

    def get_weight(self, days: int = 90) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.weight", start_ms, end_ms)

    def get_sleep(self, days: int = 7) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.sleep.segment", start_ms, end_ms)

    def get_calories(self, days: int = 1) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.calories.expended", start_ms, end_ms)

    def get_all_vital_data(self) -> dict:
        return {
            "steps": self.get_steps(),
            "heart_rate": self.get_heart_rate(),
            "weight": self.get_weight(),
            "sleep": self.get_sleep(),
            "calories": self.get_calories(),
        }

    def is_connected(self) -> bool:
        return self._ensure_token()
