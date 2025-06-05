import os
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta

class EkaService:
    def __init__(self):
        self.base_url = "https://api.eka.care/"
        self.client_id = os.getenv("EKA_CLIENT_ID")  # Replace with actual client ID
        self.client_secret = os.getenv("17a252a7-6ea9-4171-af23-583b5d0b6c77")
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    async def _login(self) -> None:
        """
        Authenticate with Eka Care API using client credentials
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}connect/login",
                json={
                    "clientId": self.client_id,
                    "clientSecret": self.client_secret
                }
            )
            if response.status_code != 200:
                raise Exception(f"Login failed: {response.text}")
            
            data = response.json()
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            self.token_expiry = datetime.now() + timedelta(minutes=29)

    async def _refresh_token(self) -> None:
        """
        Refresh the access token using the refresh token
        """
        if not self.refresh_token:
            await self._login()
            return

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}connect/refresh",
                json={
                    "refreshToken": self.refresh_token
                }
            )
            if response.status_code != 200:
                await self._login()
                return
            
            data = response.json()
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            self.token_expiry = datetime.now() + timedelta(minutes=29)

    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers, refreshing token if necessary
        """
        if not self.access_token or not self.token_expiry or datetime.now() >= self.token_expiry:
            if self.refresh_token:
                await self._refresh_token()
            else:
                await self._login()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def create_prescription(self, voice_text: str) -> Dict[str, Any]:
        """
        Create a prescription using Eka's AI service
        """
        headers = await self.get_auth_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}ai/ekascribe",
                    headers=headers,
                    json={"text": voice_text}
                )
                
                if response.status_code == 401:
                    # Token expired during request, refresh and retry once
                    await self._refresh_token()
                    headers = await self.get_auth_headers()
                    response = await client.post(
                        f"{self.base_url}ai/ekascribe",
                        headers=headers,
                        json={"text": voice_text}
                    )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                raise Exception(f"Prescription creation failed: {e.response.text}")
            except Exception as e:
                raise Exception(f"Prescription creation failed: {str(e)}") 
