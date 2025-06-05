from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Response
import os
from dotenv import load_dotenv
from app.services.interakt_service import InteraktService
from app.services.eka_service import EkaService
from typing import Dict
import time
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

load_dotenv()

# Pydantic models for request validation
class CustomerTraits(BaseModel):
    name: Optional[str] = None
    row_number: Optional[int] = None
    whatsapp_opted_in: Optional[bool] = None
    doctor_name: Optional[str] = Field(None, alias="Doctor Name")

class Customer(BaseModel):
    id: str
    channel_phone_number: str
    phone_number: str
    country_code: str
    traits: CustomerTraits

class Message(BaseModel):
    id: str
    chat_message_type: str
    message_status: str
    received_at_utc: str
    message_content_type: str
    media_url: Optional[str] = None
    message: Optional[str] = None
    meta_data: Dict[str, Any] = {}

class WebhookData(BaseModel):
    customer: Customer
    message: Message

class WebhookRequest(BaseModel):
    version: str
    timestamp: str
    type: str
    data: WebhookData

app = FastAPI(
    title="WhatsApp Voice to Prescription Service",
    description="A service that converts WhatsApp voice messages to prescriptions using Eka Care's API",
    version="1.0.0"
)
interakt_service = InteraktService()
eka_service = EkaService()

# Store phone numbers temporarily to match callbacks with requests
# In production, use a proper database
phone_number_store: Dict[str, str] = {}

@app.get("/")
async def root():
    """
    Root endpoint that returns basic service information
    """
    return {
        "Hello": "World"
    }

@app.get("/health")
async def healthcheck():
    """
    Healthcheck endpoint that returns service health status
    """
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler that initializes service state
    """
    app.start_time = time.time()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(webhook: WebhookRequest, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for receiving WhatsApp voice messages from Interakt
    """
    try:
        # Validate message type
        if webhook.data.message.message_content_type != "Audio":
            return {
                "status": "ignored",
                "message": f"Not an audio message. Got: {webhook.data.message.message_content_type}"
            }

        if not webhook.data.message.media_url:
            raise HTTPException(status_code=400, detail="No media URL provided for audio message")

        # Extract relevant information
        media_url = webhook.data.message.media_url
        phone_number = webhook.data.customer.phone_number
        customer_name = webhook.data.customer.traits.name or "Unknown"
        doctor_name = webhook.data.customer.traits.doctor_name or "Unknown"

        # Download voice message
        voice_content = await interakt_service.download_voice_message(media_url)
        
        # Send to Eka Care for prescription generation
        prescription_request = await eka_service.create_prescription(
            voice_content,
            metadata={
                "customer_name": customer_name,
                "doctor_name": doctor_name,
                "phone_number": phone_number
            }
        )
        
        # Store phone number for callback matching
        request_id = prescription_request["requestId"]
        phone_number_store[request_id] = phone_number
        
        return {
            "status": "success",
            "message": "Processing voice message",
            "details": {
                "customer_name": customer_name,
                "doctor_name": doctor_name,
                "message_id": webhook.data.message.id
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/prescription")
async def prescription_webhook(request: Request):
    """
    Webhook endpoint for receiving prescription generation callbacks from Eka
    """
    try:
        payload = await request.json()
        request_id = payload["requestId"]
        prescription_data = payload["prescription"]
        
        # Get the phone number from our store
        phone_number = phone_number_store.pop(request_id, None)
        if not phone_number:
            raise HTTPException(status_code=404, detail="Request ID not found")
        
        # Send prescription back via WhatsApp
        await interakt_service.send_prescription(phone_number, prescription_data)
        
        return {"status": "success", "message": "Prescription sent to WhatsApp"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8000"))
    ) 
