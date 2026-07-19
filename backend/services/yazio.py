import httpx
import time

BASE_URL = "https://yzapi.yazio.com/v15"
CLIENT_ID = "1_4hiybetvfksgw40o0sog4s884kwc840wwso8go4k8c04goo4c"
CLIENT_SECRET = "6rok2m65xuskgkgogw40wkkk8sw0osg84s8cggsc4woos4s8o"


class YazioClient:
    def __init__(self, access_token: str = None, refresh_token: str = None,
                 token_expiry: float = 0, user_id: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.user_id = user_id
        self.client = httpx.Client(timeout=30.0)

    def login(self, email: str, password: str) -> bool:
        try:
            resp = self.client.post(
                f"{BASE_URL}/oauth/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "username": email,
                    "password": password,
                    "grant_type": "password",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.token_expiry = time.time() + data.get("expires_in", 172800) - 300
                return True
            return False
        except Exception:
            return False

    def _refresh(self) -> bool:
        if not self.refresh_token:
            return False
        try:
            resp = self.client.post(
                f"{BASE_URL}/oauth/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.token_expiry = time.time() + data.get("expires_in", 172800) - 300
                return True
            return False
        except Exception:
            return False

    def _ensure_token(self) -> bool:
        if not self.access_token:
            return self._refresh() if self.refresh_token else False
        if time.time() > self.token_expiry:
            return self._refresh()
        return True

    def _get(self, path: str, params: dict = None) -> dict | list | None:
        if not self._ensure_token():
            return None
        try:
            resp = self.client.get(
                f"{BASE_URL}{path}",
                params=params,
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 401:
                if self._refresh():
                    resp = self.client.get(
                        f"{BASE_URL}{path}",
                        params=params,
                        headers={"Authorization": f"Bearer {self.access_token}"},
                    )
                    if resp.status_code == 200:
                        return resp.json()
            return None
        except Exception:
            return None

    def is_connected(self) -> bool:
        return self._ensure_token()

    def get_daily_summary(self, date: str) -> dict | None:
        return self._get("/user/widgets/daily-summary", {"date": date})

    def get_consumed_items(self, date: str) -> list | None:
        return self._get("/user/consumed-items", {"date": date})

    def get_user_info(self) -> dict | None:
        return self._get("/user")

    def get_goals(self, date: str) -> dict | None:
        return self._get("/user/goals/unmodified", {"date": date})

    def get_water_intake(self, date: str) -> list | None:
        return self._get("/user/water-intake", {"date": date})
