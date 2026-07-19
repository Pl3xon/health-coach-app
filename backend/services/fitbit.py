import httpx
import time
import base64
from datetime import datetime, timezone, timedelta


class FitbitClient:
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
    BASE_URL = "https://api.fitbit.com"
    SCOPES = "activity heartrate nutrition oxygen_saturation profile respiratory_rate sleep temperature"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "",
                 access_token: str = None, refresh_token: str = None,
                 token_expiry: float = 0, user_id: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.user_id = user_id
        self.client = httpx.Client(timeout=30.0)

    def get_auth_url(self) -> str:
        return (
            f"{self.AUTH_URL}"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={self.SCOPES}"
            f"&expires_in=604800"
        )

    def _basic_auth(self) -> str:
        creds = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        return f"Basic {creds}"

    def exchange_code(self, auth_code: str) -> dict:
        try:
            resp = self.client.post(
                self.TOKEN_URL,
                data={
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Authorization": self._basic_auth()},
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                expires_in = data.get("expires_in", 28800)
                self.token_expiry = time.time() + expires_in - 300
                return {"success": True}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False
        try:
            resp = self.client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                headers={"Authorization": self._basic_auth()},
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token", self.refresh_token)
                expires_in = data.get("expires_in", 28800)
                self.token_expiry = time.time() + expires_in - 300
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

    def _get(self, path: str) -> dict | None:
        if not self._ensure_token():
            return None
        try:
            resp = self.client.get(
                f"{self.BASE_URL}{path}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def is_connected(self) -> bool:
        return self._ensure_token()

    def get_profile(self) -> dict | None:
        return self._get("/1/user/-/profile.json")

    def get_steps_today(self) -> int:
        data = self._get("/1/user/-/activities/steps/date/today.json")
        if data:
            try:
                return data["activities-steps"][0]["value"]
            except (KeyError, IndexError):
                pass
        return 0

    def get_calories_today(self) -> int:
        data = self._get("/1/user/-/activities/calories/date/today.json")
        if data:
            try:
                return int(data["activities-calories"][0]["value"])
            except (KeyError, IndexError):
                pass
        return 0

    def get_heart_rate_today(self) -> dict:
        data = self._get("/1/user/-/activities/heart/date/today.json")
        if not data:
            return {"resting": 0, "latest": 0, "zones": []}
        try:
            hr = data["activities-heart"][0]["value"]
            resting = hr.get("restingHeartRate", 0)
            zones = []
            for z in hr.get("heartRateZones", []):
                zones.append({
                    "name": z.get("name", ""),
                    "min": z.get("min", 0),
                    "max": z.get("max", 0),
                    "minutes": z.get("minutes", 0),
                })
            return {"resting": resting, "latest": resting, "zones": zones}
        except (KeyError, IndexError):
            return {"resting": 0, "latest": 0, "zones": []}

    def get_heart_rate_series(self) -> list:
        data = self._get("/1/user/-/activities/heart/date/today/1d/1min.json")
        if not data:
            return []
        try:
            points = data["activities-heart-intraday"]["dataset"]
            result = []
            for p in points:
                result.append({"time": p["time"], "value": p["value"]})
            return result
        except (KeyError, IndexError):
            return []

    def get_spo2_today(self) -> float:
        data = self._get("/1/user/-/spo2/date/today.json")
        if data:
            try:
                return round(data.get("value", 0), 1)
            except (KeyError, TypeError):
                pass
        return 0.0

    def get_hrv_today(self) -> dict:
        data = self._get("/1/user/-/hrv/date/today.json")
        if data:
            try:
                hrv = data.get("daily", {}).get("hrv", [])
                if hrv:
                    val = hrv[0].get("value", {})
                    return {
                        "rmssd": round(val.get("rmssd", 0), 1),
                        "coverage": val.get("coverage", 0),
                    }
            except (KeyError, IndexError, TypeError):
                pass
        return {"rmssd": 0, "coverage": 0}

    def get_sleep_today(self) -> dict:
        tz = timezone(timedelta(hours=2))
        today = datetime.now(tz).strftime("%Y-%m-%d")
        data = self._get(f"/1.2/user/-/sleep/date/{today}.json")
        if not data:
            return {"total_minutes": 0, "total_hours": 0, "stages": {}}
        try:
            sleep_logs = data.get("sleep", [])
            if not sleep_logs:
                return {"total_minutes": 0, "total_hours": 0, "stages": {}}
            main_sleep = sleep_logs[0]
            total_minutes = main_sleep.get("minutesAsleep", 0)
            stages = main_sleep.get("levels", {}).get("summary", {})
            return {
                "total_minutes": total_minutes,
                "total_hours": round(total_minutes / 60, 1),
                "stages": {
                    "deep": stages.get("deep", {}).get("minutes", 0),
                    "light": stages.get("light", {}).get("minutes", 0),
                    "rem": stages.get("rem", {}).get("minutes", 0),
                    "awake": stages.get("wake", {}).get("minutes", 0),
                },
            }
        except (KeyError, IndexError, TypeError):
            return {"total_minutes": 0, "total_hours": 0, "stages": {}}

    def get_active_zone_minutes(self) -> int:
        data = self._get("/1/user/-/activities/date/today.json")
        if data:
            try:
                return data["summary"]["activeZoneMinutes"]
            except (KeyError, TypeError):
                pass
        return 0

    def get_activities_summary(self) -> dict:
        data = self._get("/1/user/-/activities/date/today.json")
        if not data:
            return {}
        try:
            return data.get("summary", {})
        except (KeyError, TypeError):
            return {}

    def get_all_vital_data(self) -> dict:
        hr = self.get_heart_rate_today()
        hrv = self.get_hrv_today()
        sleep = self.get_sleep_today()
        return {
            "steps_today": self.get_steps_today(),
            "calories_today": self.get_calories_today(),
            "heart_rate": hr.get("resting", 0),
            "latest_heart_rate": hr.get("latest", 0),
            "heart_rate_zones": hr.get("zones", []),
            "sleep_hours": sleep.get("total_hours", 0),
            "sleep_stages": sleep.get("stages", {}),
            "resting_heart_rate": hr.get("resting", 0),
            "hrv": hrv.get("rmssd", 0),
            "spo2": self.get_spo2_today(),
            "active_zone_minutes": self.get_active_zone_minutes(),
        }

    def get_health_history(self, days: int = 30) -> dict:
        tz = timezone(timedelta(hours=2))
        now = datetime.now(tz)

        steps_history = []
        calories_history = []
        hr_history = []
        resting_hr_history = []
        hrv_history = []
        spo2_history = []
        azm_history = []

        for i in range(days - 1, -1, -1):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")

            steps_data = self._get(f"/1/user/-/activities/steps/date/{d}.json")
            if steps_data:
                try:
                    steps_history.append({"date": d, "value": int(steps_data["activities-steps"][0]["value"])})
                except (KeyError, IndexError):
                    steps_history.append({"date": d, "value": 0})
            else:
                steps_history.append({"date": d, "value": 0})

            cal_data = self._get(f"/1/user/-/activities/calories/date/{d}.json")
            if cal_data:
                try:
                    calories_history.append({"date": d, "value": round(float(cal_data["activities-calories"][0]["value"]))})
                except (KeyError, IndexError):
                    calories_history.append({"date": d, "value": 0})
            else:
                calories_history.append({"date": d, "value": 0})

            hr_data = self._get(f"/1/user/-/activities/heart/date/{d}.json")
            if hr_data:
                try:
                    hr_val = hr_data["activities-heart"][0]["value"]
                    resting = hr_val.get("restingHeartRate", 0)
                    resting_hr_history.append({"date": d, "value": float(resting) if resting else 0})
                except (KeyError, IndexError):
                    resting_hr_history.append({"date": d, "value": 0})
            else:
                resting_hr_history.append({"date": d, "value": 0})

            hrv_data = self._get(f"/1/user/-/hrv/date/{d}.json")
            if hrv_data:
                try:
                    hrv_list = hrv_data.get("daily", {}).get("hrv", [])
                    if hrv_list:
                        val = hrv_list[0].get("value", {}).get("rmssd", 0)
                        hrv_history.append({"date": d, "value": round(float(val), 1)})
                    else:
                        hrv_history.append({"date": d, "value": 0})
                except (KeyError, IndexError, TypeError):
                    hrv_history.append({"date": d, "value": 0})
            else:
                hrv_history.append({"date": d, "value": 0})

            spo2_data = self._get(f"/1/user/-/spo2/date/{d}.json")
            if spo2_data:
                try:
                    val = spo2_data.get("value", 0)
                    spo2_history.append({"date": d, "value": round(float(val), 1) if val else 0})
                except (KeyError, TypeError):
                    spo2_history.append({"date": d, "value": 0})
            else:
                spo2_history.append({"date": d, "value": 0})

            azm_data = self._get(f"/1/user/-/activities/date/{d}.json")
            if azm_data:
                try:
                    azm_history.append({"date": d, "value": azm_data["summary"]["activeZoneMinutes"]})
                except (KeyError, TypeError):
                    azm_history.append({"date": d, "value": 0})
            else:
                azm_history.append({"date": d, "value": 0})

        return {
            "steps": steps_history,
            "calories": calories_history,
            "heart_rate": hr_history,
            "resting_heart_rate": resting_hr_history,
            "hrv": hrv_history,
            "spo2": spo2_history,
            "active_zone_minutes": azm_history,
        }
