from typing import Optional
from renpho import RenphoClient as _RenphoClient


class RenphoClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.user_id = None
        self.token = None
        self._client = None

    def login(self) -> bool:
        try:
            self._client = _RenphoClient(self.email, self.password)
            self._client.login()
            self.user_id = self._client.user_id
            self.token = self._client.token
            return True
        except Exception as e:
            print(f"Renpho login error: {e}")
            return False

    def _ensure_logged_in(self) -> bool:
        if self._client and self.token:
            return True
        return self.login()

    def get_latest_measurement(self) -> Optional[dict]:
        if not self._ensure_logged_in():
            return None
        try:
            measurements = self._client.get_all_measurements()
            if measurements:
                m = measurements[0]
                return {
                    "weight": m.get("weight"),
                    "bodyFat": m.get("bodyfat"),
                    "muscleMass": m.get("sinew"),
                    "bmr": m.get("bmr"),
                    "bmi": m.get("bmi"),
                    "water": m.get("water"),
                    "bone": m.get("bone"),
                    "visceralFat": m.get("visfat"),
                    "bodyAge": m.get("bodyage"),
                    "heartRate": m.get("heartRate"),
                    "date": m.get("localCreatedAt", ""),
                }
        except Exception as e:
            print(f"Renpho measurements error: {e}")
        return None

    def get_measurements(self, days: int = 30) -> list:
        if not self._ensure_logged_in():
            return []
        try:
            return self._client.get_all_measurements()
        except Exception as e:
            print(f"Renpho measurements error: {e}")
            return []
