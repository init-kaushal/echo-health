from typing import Dict, Any
import httpx
from config import get_settings

settings = get_settings()

class EkaService:
    def __init__(self):
        self.base_url = settings.eka_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.eka_api_key}",
            "Content-Type": "application/json"
        }

    async def create_self_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a self assessment using Eka Care API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/self-assessment",
                json=assessment_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_prescription(self, assessment_id: str) -> Dict[str, Any]:
        """Get prescription using v2rx API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2rx/{assessment_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_doc_assist_summary(self, assessment_id: str) -> Dict[str, Any]:
        """Get DocAssist summary"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/docassist/{assessment_id}/summary",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def schedule_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an appointment"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/appointments",
                json=appointment_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def request_teleconsultation(self, consultation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request a teleconsultation"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/teleconsultation",
                json=consultation_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json() 