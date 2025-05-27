from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import json
import uuid
from anthropic import Anthropic
import os
from services.eka_service import EkaService
from config import get_settings

app = FastAPI()
settings = get_settings()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Questions database (in memory for demo)
questions = {
    "first": {
        "id": "first",
        "text": "Hello! I'm your health assistant. How are you feeling today?",
        "type": "open",
        "next": "symptoms"
    },
    "symptoms": {
        "id": "symptoms",
        "text": "Can you describe any symptoms you're experiencing?",
        "type": "open",
        "next": "duration"
    },
    "duration": {
        "id": "duration",
        "text": "How long have you been experiencing these symptoms?",
        "type": "open",
        "next": "severity"
    },
    "severity": {
        "id": "severity",
        "text": "On a scale of 1 to 10, how severe is your discomfort?",
        "type": "scale",
        "next": "medication"
    },
    "medication": {
        "id": "medication",
        "text": "Are you currently taking any medications?",
        "type": "boolean",
        "next": {
            "yes": "medication_details",
            "no": "previous_conditions"
        }
    },
    "medication_details": {
        "id": "medication_details",
        "text": "Please list the medications you're taking.",
        "type": "open",
        "next": "previous_conditions"
    },
    "previous_conditions": {
        "id": "previous_conditions",
        "text": "Do you have any pre-existing medical conditions?",
        "type": "boolean",
        "next": None
    }
}

# Store conversations
conversations: Dict[str, List[Dict]] = {}

class Answer(BaseModel):
    question_id: str
    answer: str

class Assessment(BaseModel):
    answers: List[Answer]

class AppointmentRequest(BaseModel):
    doctor_id: str
    date: str
    time_slot: str
    consultation_type: str  # "in_person" or "tele"
    symptoms: str

class Message(BaseModel):
    role: str
    text: str

class GenerateQuestionRequest(BaseModel):
    conversation_history: List[Message]
    last_response: str

def get_eka_service():
    return EkaService()

@app.get("/")
def read_root():
    return {"status": "healthy"}

@app.get("/questions/{question_id}")
async def get_question(question_id: str):
    if question_id not in questions:
        raise HTTPException(status_code=404, detail="Question not found")
    return questions[question_id]

@app.post("/assessment")
async def submit_assessment(assessment: Assessment):
    # Generate a unique conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Store the conversation
    conversation = []
    for answer in assessment.answers:
        q = questions[answer.question_id]
        conversation.append({
            "role": "assistant",
            "text": q["text"]
        })
        conversation.append({
            "role": "user",
            "text": answer.answer
        })
    
    conversations[conversation_id] = conversation
    
    # Generate a recommendation based on the answers
    recommendation = "Based on your symptoms, I recommend scheduling a consultation with a healthcare provider. Would you like me to help you book an appointment?"
    
    return {
        "conversation_id": conversation_id,
        "recommendation": recommendation,
        "conversation": conversation
    }

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation": conversations[conversation_id]}

@app.post("/appointments")
async def book_appointment(
    appointment: AppointmentRequest,
    eka_service: EkaService = Depends(get_eka_service)
):
    try:
        if appointment.consultation_type == "tele":
            result = await eka_service.request_teleconsultation({
                "doctor_id": appointment.doctor_id,
                "date": appointment.date,
                "time_slot": appointment.time_slot,
                "symptoms": appointment.symptoms
            })
        else:
            result = await eka_service.schedule_appointment({
                "doctor_id": appointment.doctor_id,
                "date": appointment.date,
                "time_slot": appointment.time_slot,
                "symptoms": appointment.symptoms
            })

        return {
            "status": "success",
            "appointment_id": result["id"],
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-question")
async def generate_question(request: GenerateQuestionRequest):
    try:
        # Initialize Anthropic client
        anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Format conversation history for Claude
        messages = []
        for msg in request.conversation_history:
            messages.append({
                "role": "assistant" if msg.role == "assistant" else "user",
                "content": msg.text
            })
        
        # Add the latest response
        messages.append({
            "role": "user",
            "content": request.last_response
        })
        
        # Generate next question using Claude
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            temperature=0.7,
            system="You are a professional healthcare assistant conducting a patient assessment. Generate relevant follow-up questions based on the patient's responses. Focus on gathering important health information while being empathetic and professional. Ask one question at a time.",
            messages=messages
        )
        
        # Extract the generated question
        question = response.content[0].text
        
        return {"question": question}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 