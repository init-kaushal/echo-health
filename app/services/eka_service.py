import os
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta

class EkaService:
    def __init__(self):
        self.base_url = "https://api.eka.care/"
        self.client_id = os.getenv("EKA_CLIENT_ID")
        self.client_secret = os.getenv("EKA_CLIENT_SECRET")
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

    async def create_prescription(self, voice_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a prescription using Eka's AI service
        
        Args:
            voice_text: The voice message content
            metadata: Additional information about the request (customer name, doctor name, etc.)
        """
        headers = await self.get_auth_headers()
        
        request_data = {
            "text": voice_text
        }
        
        if metadata:
            request_data.update({
                "customer_name": metadata.get("customer_name"),
                "doctor_name": metadata.get("doctor_name"),
                "phone_number": metadata.get("phone_number")
            })
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}ai/ekascribe",
                    headers=headers,
                    json=request_data
                )
                
                if response.status_code == 401:
                    # Token expired during request, refresh and retry once
                    await self._refresh_token()
                    headers = await self.get_auth_headers()
                    response = await client.post(
                        f"{self.base_url}ai/ekascribe",
                        headers=headers,
                        json=request_data
                    )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                raise Exception(f"Prescription creation failed: {e.response.text}")
            except Exception as e:
                raise Exception(f"Prescription creation failed: {str(e)}") 
