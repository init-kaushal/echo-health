import os
import httpx
from typing import Dict, Any

class InteraktService:
    def __init__(self):
        self.base_url = "https://api.interakt.ai"
        self.api_key = os.getenv("INTERAKT_API_KEY")

    async def download_voice_message(self, media_url: str) -> bytes:
        """
        Download voice message from WhatsApp/Interakt
        """
        async with httpx.AsyncClient() as client:


            response = await client.get(
                media_url,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.content

    async def send_prescription(self, phone_number: str, prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send prescription back to the user via WhatsApp
        """
        message = self._format_prescription_message(prescription_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "countryCode": "91",  # Adjust based on your needs
                    "phoneNumber": phone_number,
                    "type": "text",
                    "message": message
                }
            )
            return response.json()

    def _format_prescription_message(self, prescription_data: Dict[str, Any]) -> str:
        """
        Format prescription data into a readable WhatsApp message
        """
        # This is a basic template - adjust based on the actual prescription data structure
        message = "🏥 *Your Prescription*\n\n"
        
        if "medications" in prescription_data:
            message += "*Medications:*\n"
            for med in prescription_data["medications"]:
                message += f"- {med['name']}: {med['dosage']}\n"
        
        if "instructions" in prescription_data:
            message += "\n*Instructions:*\n"
            message += prescription_data["instructions"]
        
        return message 
