import httpx
import time
from typing import Optional


class GoogleFitClient:
    BASE_URL = "https://www.googleapis.com/fitness/v1"
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.client = httpx.Client(timeout=30.0)
    
    def exchange_code(self, auth_code: str) -> dict:
        try:
            resp = self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": auth_code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:3000/callback"
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                return {"success": True, "tokens": data}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh_access_token(self) -> bool:
        try:
            resp = self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                return True
            return False
        except Exception:
            return False
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_data_sources(self) -> list:
        try:
            resp = self.client.get(
                f"{self.BASE_URL}/users/me/dataSources",
                headers=self._get_headers()
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("dataSource", [])
            return []
        except Exception:
            return []
    
    def aggregate_data(self, data_type: str, start_ms: int, end_ms: int) -> list:
        try:
            body = {
                "aggregateBy": [{"dataTypeName": data_type}],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms
            }
            
            resp = self.client.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                json=body,
                headers=self._get_headers()
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return data.get("bucket", [])
            return []
        except Exception:
            return []
    
    def get_steps(self, days: int = 30) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.step_count.delta", start_ms, end_ms)
    
    def get_heart_rate(self, days: int = 30) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.heart_rate.bpm", start_ms, end_ms)
    
    def get_weight(self, days: int = 90) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.weight", start_ms, end_ms)
    
    def get_sleep(self, days: int = 30) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.sleep.segment", start_ms, end_ms)
    
    def get_calories(self, days: int = 30) -> list:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - (days * 24 * 60 * 60 * 1000)
        return self.aggregate_data("com.google.calories.expended", start_ms, end_ms)
    
    def get_all_vital_data(self) -> dict:
        return {
            "steps": self.get_steps(),
            "heart_rate": self.get_heart_rate(),
            "weight": self.get_weight(),
            "sleep": self.get_sleep(),
            "calories": self.get_calories()
        }
