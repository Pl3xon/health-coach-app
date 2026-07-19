import httpx
import time
from datetime import datetime, timezone, timedelta


class GoogleFitClient:
    BASE_URL = "https://www.googleapis.com/fitness/v1"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
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
                 access_token: str = None, refresh_token: str = None, token_expiry: float = 0,
                 user_id: str = None):
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
            "Content-Type": "application/json",
        }

    def _tz(self):
        return timezone(timedelta(hours=2))

    def _today_range_ms(self):
        tz = self._tz()
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(start.timestamp() * 1000), int(now.timestamp() * 1000)

    def _days_range_ms(self, days: int):
        tz = self._tz()
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        return int(start.timestamp() * 1000), int(now.timestamp() * 1000)

    def _aggregate(self, data_type: str, start_ms: int, end_ms: int, bucket_ms: int = 86400000) -> list:
        if not self._ensure_token():
            return []
        try:
            body = {
                "aggregateBy": [{"dataTypeName": data_type}],
                "bucketByTime": {"durationMillis": bucket_ms},
                "startTimeMillis": start_ms,
                "endTimeMillis": end_ms,
            }
            resp = self.client.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                json=body,
                headers=self._get_headers(),
            )
            if resp.status_code == 200:
                return resp.json().get("bucket", [])
            return []
        except Exception:
            return []

    def _sum_fp(self, buckets: list) -> float:
        total = 0.0
        for bucket in buckets:
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for val in pt.get("value", []):
                        if "fpVal" in val:
                            total += val["fpVal"]
        return total

    def _sum_int(self, buckets: list) -> int:
        total = 0
        for bucket in buckets:
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for val in pt.get("value", []):
                        if "intVal" in val:
                            total += val["intVal"]
        return total

    def _last_fp(self, buckets: list) -> float:
        for bucket in reversed(buckets):
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for val in pt.get("value", []):
                        if "fpVal" in val and val["fpVal"] > 0:
                            return val["fpVal"]
        return 0.0

    def _last_int(self, buckets: list) -> int:
        for bucket in reversed(buckets):
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for val in pt.get("value", []):
                        if "intVal" in val and val["intVal"] > 0:
                            return val["intVal"]
        return 0

    def _daily_values(self, data_type: str, days: int, as_float: bool = True) -> list:
        start_ms, end_ms = self._days_range_ms(days)
        buckets = self._aggregate(data_type, start_ms, end_ms)
        result = []
        tz = self._tz()
        for bucket in buckets:
            ts = bucket.get("startTimeMillis", 0)
            dt = datetime.fromtimestamp(ts / 1000, tz=tz)
            val = 0.0
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for v in pt.get("value", []):
                        if as_float and "fpVal" in v:
                            val += v["fpVal"]
                        elif not as_float and "intVal" in v:
                            val += v["intVal"]
            result.append({"date": dt.strftime("%Y-%m-%d"), "value": round(val, 1)})
        return result

    def get_today_steps(self) -> int:
        start_ms, end_ms = self._today_range_ms()
        return self._sum_int(self._aggregate("com.google.step_count.delta", start_ms, end_ms))

    def get_today_calories(self) -> int:
        start_ms, end_ms = self._today_range_ms()
        return max(0, round(self._sum_fp(self._aggregate("com.google.calories.expended", start_ms, end_ms))))

    def get_latest_heart_rate(self) -> int:
        now_ms = int(time.time() * 1000)
        day_ago_ms = now_ms - (24 * 60 * 60 * 1000)
        buckets = self._aggregate("com.google.heart_rate.bpm", day_ago_ms, now_ms, 60000)
        return round(self._last_fp(buckets))

    def get_today_sleep_hours(self) -> float:
        now_ms = int(time.time() * 1000)
        week_ago_ms = now_ms - (7 * 24 * 60 * 60 * 1000)
        buckets = self._aggregate("com.google.sleep.segment", week_ago_ms, now_ms)
        total_ms = 0
        for bucket in buckets:
            for ds in bucket.get("dataset", []):
                for pt in ds.get("point", []):
                    for val in pt.get("value", []):
                        if "intVal" in val:
                            total_ms += val["intVal"]
        return round(total_ms / 3600000, 1) if total_ms > 0 else 0

    def get_resting_heart_rate(self) -> int:
        start_ms, end_ms = self._today_range_ms()
        return round(self._last_fp(self._aggregate("com.google.resting_heart_rate", start_ms, end_ms)))

    def get_hrv(self) -> float:
        start_ms, end_ms = self._today_range_ms()
        return round(self._last_fp(self._aggregate("com.google.heart_rate_variability.daily", start_ms, end_ms)), 1)

    def get_spo2(self) -> float:
        start_ms, end_ms = self._today_range_ms()
        val = self._last_fp(self._aggregate("com.google.oxygen_saturation", start_ms, end_ms))
        return round(val * 100, 1) if val > 0 else 0

    def get_active_zone_minutes(self) -> int:
        start_ms, end_ms = self._today_range_ms()
        return self._sum_int(self._aggregate("com.google.active_zone_minutes", start_ms, end_ms))

    def get_all_vital_data(self) -> dict:
        return {
            "steps_today": self.get_today_steps(),
            "calories_today": self.get_today_calories(),
            "heart_rate": self.get_latest_heart_rate(),
            "sleep_hours": self.get_today_sleep_hours(),
            "resting_heart_rate": self.get_resting_heart_rate(),
            "hrv": self.get_hrv(),
            "spo2": self.get_spo2(),
            "active_zone_minutes": self.get_active_zone_minutes(),
        }

    def get_health_history(self, days: int = 30) -> dict:
        return {
            "steps": self._daily_values("com.google.step_count.delta", days, as_float=False),
            "calories": self._daily_values("com.google.calories.expended", days, as_float=True),
            "heart_rate": self._daily_values("com.google.heart_rate.bpm", days, as_float=True),
            "resting_heart_rate": self._daily_values("com.google.resting_heart_rate", days, as_float=True),
            "hrv": self._daily_values("com.google.heart_rate_variability.daily", days, as_float=True),
            "spo2": self._daily_values("com.google.oxygen_saturation", days, as_float=True),
            "active_zone_minutes": self._daily_values("com.google.active_zone_minutes", days, as_float=False),
        }

    def is_connected(self) -> bool:
        return self._ensure_token()
