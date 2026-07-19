import httpx
import time
from datetime import datetime, timezone, timedelta


class GoogleHealthClient:
    BASE_URL = "https://health.googleapis.com/v4"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    WEARABLE_FAMILY = "users/me/dataSourceFamilies/google-wearables"
    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.nutrition.read",
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
        "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
        "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
        "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    ]

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
            "Accept": "application/json",
        }

    def _tz(self):
        return timezone(timedelta(hours=2))

    def is_connected(self) -> bool:
        return self._ensure_token()

    def _reconcile(self, data_type: str, filter_str: str = "") -> list:
        path = f"/users/me/dataTypes/{data_type}/dataPoints:reconcile"
        params = {"dataSourceFamily": self.WEARABLE_FAMILY}
        if filter_str:
            params["filter"] = filter_str
        if not self._ensure_token():
            return []
        try:
            url = f"{self.BASE_URL}{path}"
            resp = self.client.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                return resp.json().get("dataPoints", [])
            return []
        except Exception:
            return []

    def _list_data_points(self, data_type: str, filter_str: str = "") -> list:
        path = f"/users/me/dataTypes/{data_type}/dataPoints"
        params = {}
        if filter_str:
            params["filter"] = filter_str
        if not self._ensure_token():
            return []
        try:
            url = f"{self.BASE_URL}{path}"
            resp = self.client.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                return resp.json().get("dataPoints", [])
            return []
        except Exception:
            return []

    def _get_data(self, data_type: str, filter_str: str = "") -> list:
        points = self._reconcile(data_type, filter_str)
        if not points:
            points = self._list_data_points(data_type, filter_str)
        return points

    def get_steps_today(self) -> int:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("steps", f'steps.interval.civil_start_time >= "{today}"')
        total = 0
        for p in points:
            steps = p.get("steps", {})
            total += int(steps.get("count", 0))
        return total

    def get_calories_today(self) -> int:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("active-energy-burned", f'active_energy_burned.interval.civil_start_time >= "{today}"')
        total = 0.0
        for p in points:
            cal = p.get("activeEnergyBurned", {})
            total += float(cal.get("kcal", 0))
        return max(0, round(total))

    def get_resting_heart_rate_today(self) -> int:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("daily-resting-heart-rate", f'daily_resting_heart_rate.civil_start_time >= "{today}"')
        for p in reversed(points):
            rhr = p.get("dailyRestingHeartRate", {})
            val = rhr.get("bpm", 0)
            if val > 0:
                return val
        return 0

    def get_hrv_today(self) -> float:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("daily-heart-rate-variability", f'daily_heart_rate_variability.civil_start_time >= "{today}"')
        for p in reversed(points):
            hrv = p.get("dailyHeartRateVariability", {})
            rmssd = hrv.get("rmssdMilliseconds", 0)
            if rmssd > 0:
                return round(rmssd, 1)
        return 0.0

    def get_spo2_today(self) -> float:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("daily-oxygen-saturation", f'daily_oxygen_saturation.civil_start_time >= "{today}"')
        for p in reversed(points):
            spo2 = p.get("dailyOxygenSaturation", {})
            val = spo2.get("percentage", 0)
            if val > 0:
                return round(val, 1)
        return 0.0

    def get_sleep_today(self) -> dict:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("sleep", f'sleep.interval.civil_end_time >= "{today}"')
        for p in points:
            sleep_data = p.get("sleep", {})
            summary = sleep_data.get("summary", {})
            total_min = int(summary.get("minutesAsleep", 0))
            stages_summary = summary.get("stagesSummary", [])
            stages = {}
            for s in stages_summary:
                stages[s.get("type", "").lower()] = int(s.get("minutes", 0))
            if total_min > 0:
                return {
                    "total_minutes": total_min,
                    "total_hours": round(total_min / 60, 1),
                    "stages": stages,
                }
        return {"total_minutes": 0, "total_hours": 0, "stages": {}}

    def get_active_zone_minutes_today(self) -> int:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("active-zone-minutes", f'active_zone_minutes.interval.civil_start_time >= "{today}"')
        total = 0
        for p in points:
            azm = p.get("activeZoneMinutes", {})
            total += int(azm.get("minutes", 0))
        return total

    def get_heart_rate_today(self) -> int:
        tz = self._tz()
        today = datetime.now(tz).strftime("%Y-%m-%d")
        points = self._get_data("heart-rate", f'heart_rate.observation_time.physical_time >= "{today}T00:00:00Z"')
        latest = 0
        for p in points:
            hr = p.get("heartRate", {})
            val = hr.get("bpm", 0)
            if val > 0:
                latest = val
        return latest

    def get_all_vital_data(self) -> dict:
        return {
            "steps_today": self.get_steps_today(),
            "calories_today": self.get_calories_today(),
            "heart_rate": self.get_resting_heart_rate_today(),
            "resting_heart_rate": self.get_resting_heart_rate_today(),
            "hrv": self.get_hrv_today(),
            "spo2": self.get_spo2_today(),
            "sleep_hours": self.get_sleep_today().get("total_hours", 0),
            "sleep_stages": self.get_sleep_today().get("stages", {}),
            "active_zone_minutes": self.get_active_zone_minutes_today(),
        }

    def get_health_history(self, days: int = 30) -> dict:
        tz = self._tz()
        now = datetime.now(tz)
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=days - 1)).strftime("%Y-%m-%d")

        steps_points = self._get_data("steps", f'steps.interval.civil_start_time >= "{start_date}"')
        steps_by_date = {}
        for p in steps_points:
            interval = p.get("steps", {}).get("interval", p.get("interval", {}))
            civil = interval.get("civilStartTime", {})
            dt = civil.get("date", {})
            date_str = f"{dt.get('year', 0)}-{dt.get('month', 0):02d}-{dt.get('day', 0):02d}"
            val = int(p.get("steps", {}).get("count", 0))
            steps_by_date[date_str] = steps_by_date.get(date_str, 0) + val
        steps_history = []
        for i in range(days):
            d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            steps_history.append({"date": d, "value": steps_by_date.get(d, 0)})

        cal_points = self._get_data("active-energy-burned", f'active_energy_burned.interval.civil_start_time >= "{start_date}"')
        cal_by_date = {}
        for p in cal_points:
            interval = p.get("activeEnergyBurned", {}).get("interval", p.get("interval", {}))
            civil = interval.get("civilStartTime", {})
            dt = civil.get("date", {})
            date_str = f"{dt.get('year', 0)}-{dt.get('month', 0):02d}-{dt.get('day', 0):02d}"
            val = float(p.get("activeEnergyBurned", {}).get("kcal", 0))
            cal_by_date[date_str] = cal_by_date.get(date_str, 0) + val
        calories_history = []
        for i in range(days):
            d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            calories_history.append({"date": d, "value": round(cal_by_date.get(d, 0))})

        rhr_points = self._get_data("daily-resting-heart-rate",
            f'daily_resting_heart_rate.civil_start_time >= "{start_date}"')
        resting_hr_history = self._build_daily_from_points(rhr_points, "dailyRestingHeartRate", "bpm", days, start_date)

        hrv_points = self._get_data("daily-heart-rate-variability",
            f'daily_heart_rate_variability.civil_start_time >= "{start_date}"')
        hrv_history = self._build_daily_from_points(hrv_points, "dailyHeartRateVariability", "rmssdMilliseconds", days, start_date)

        spo2_points = self._get_data("daily-oxygen-saturation",
            f'daily_oxygen_saturation.civil_start_time >= "{start_date}"')
        spo2_history = self._build_daily_from_points(spo2_points, "dailyOxygenSaturation", "percentage", days, start_date)

        azm_points = self._get_data("active-zone-minutes",
            f'active_zone_minutes.interval.civil_start_time >= "{start_date}"')
        azm_history = []
        azm_by_date = {}
        for p in azm_points:
            interval = p.get("activeZoneMinutes", {}).get("interval", p.get("interval", {}))
            civil = interval.get("civilStartTime", interval.get("civilTime", {}))
            dt = civil.get("date", {})
            date_str = f"{dt.get('year', 0)}-{dt.get('month', 0):02d}-{dt.get('day', 0):02d}"
            val = int(p.get("activeZoneMinutes", {}).get("minutes", 0))
            azm_by_date[date_str] = azm_by_date.get(date_str, 0) + val
        for i in range(days):
            d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            azm_history.append({"date": d, "value": azm_by_date.get(d, 0)})

        return {
            "steps": steps_history,
            "calories": calories_history,
            "heart_rate": [],
            "resting_heart_rate": resting_hr_history,
            "hrv": hrv_history,
            "spo2": spo2_history,
            "active_zone_minutes": azm_history,
        }

    def _build_daily_from_points(self, points: list, data_key: str, value_key: str, days: int, start_date: str) -> list:
        tz = self._tz()
        now = datetime.now(tz)
        by_date = {}
        for p in points:
            obj = p.get(data_key, {})
            civil_time = obj.get("civilStartTime", {})
            if not civil_time:
                interval = p.get("interval", {})
                civil_time = interval.get("civilStartTime", {})
            dt = civil_time.get("date", {})
            date_str = f"{dt.get('year', 0)}-{dt.get('month', 0):02d}-{dt.get('day', 0):02d}"
            val = obj.get(value_key, 0)
            by_date[date_str] = float(val) if val else 0

        result = []
        for i in range(days):
            d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            result.append({"date": d, "value": by_date.get(d, 0)})
        return result
