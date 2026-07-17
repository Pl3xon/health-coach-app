import httpx
import json
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from typing import Optional


class RenphoClient:
    BASE_URL = "https://cloud.renpho.com"
    
    # AES encryption key for Renpho API (reverse-engineered from app)
    AES_KEY = b"renpho@123456789"
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.user_id = None
        self.token = None
        self.client = httpx.Client(timeout=30.0)
    
    def _encrypt(self, data: str) -> str:
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        padded = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def _decrypt(self, data: str) -> str:
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(data))
        return unpad(decrypted, AES.block_size).decode('utf-8')
    
    def login(self) -> bool:
        try:
            payload = {
                "email": self.email,
                "password": self.password,
                "countryCode": "DE"
            }
            
            encrypted_payload = self._encrypt(json.dumps(payload))
            
            resp = self.client.post(
                f"{self.BASE_URL}/user/login",
                json={"data": encrypted_payload},
                headers={"Content-Type": "application/json"}
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 or data.get("success"):
                    result = data.get("data", data.get("result", {}))
                    if isinstance(result, str):
                        result = json.loads(self._decrypt(result))
                    self.user_id = str(result.get("userId", result.get("id", "")))
                    self.token = result.get("token", result.get("accessToken", ""))
                    return True
            return False
        except Exception as e:
            print(f"Renpho login error: {e}")
            return False
    
    def get_devices(self) -> list:
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            resp = self.client.get(
                f"{self.BASE_URL}/device/list",
                params={"userId": self.user_id},
                headers=headers
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", data.get("result", []))
            return []
        except Exception as e:
            print(f"Renpho devices error: {e}")
            return []
    
    def get_measurements(self, days: int = 30) -> list:
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            resp = self.client.get(
                f"{self.BASE_URL}/healthData/getHealthData",
                params={
                    "userId": self.user_id,
                    "startTime": start_time,
                    "endTime": end_time
                },
                headers=headers
            )
            
            if resp.status_code == 200:
                data = resp.json()
                measurements = data.get("data", data.get("result", []))
                if isinstance(measurements, str):
                    measurements = json.loads(self._decrypt(measurements))
                return measurements if isinstance(measurements, list) else []
            return []
        except Exception as e:
            print(f"Renpho measurements error: {e}")
            return []
    
    def get_latest_measurement(self) -> Optional[dict]:
        measurements = self.get_measurements(days=7)
        if measurements:
            return measurements[0] if isinstance(measurements[0], dict) else None
        return None
