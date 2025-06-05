from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Response
import os
from dotenv import load_dotenv
from app.services.interakt_service import InteraktService
from app.services.eka_service import EkaService
from typing import Dict
import time

load_dotenv()
for key, value in os.environ.items():
    print(f"{key}={value}")

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
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for receiving WhatsApp voice messages from Interakt
    """
    try:
        payload = await request.json()
        
        # Extract voice message URL and phone number
        # Note: Adjust these based on actual Interakt webhook format
        if payload.get("type") != "voice":
            return {"status": "ignored", "message": "Not a voice message"}
        
        media_url = payload["media"]["url"]
        phone_number = payload["from"]["phone_number"]
        
        # Download voice message
        voice_content = await interakt_service.download_voice_message(media_url)
        
        # Send to Eka Care for prescription generation
        prescription_request = await eka_service.create_prescription(voice_content)
        
        # Store phone number for callback matching
        request_id = prescription_request["requestId"]
        phone_number_store[request_id] = phone_number
        
        return {"status": "success", "message": "Processing voice message"}
    
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
