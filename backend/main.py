from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

from models.Medicine import *
from models.Chat import *
from db.db import medicines_db
from agents.mina_agent import MinaAgent

app = FastAPI(
    title="MinaCare API",
    description="AI-Powered Medicine Management System",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mina = MinaAgent()

@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "message": "MinaCare API is running",
        "version": "1.0.0",
        "ai_agent": "Mina (LangGraph + HuggingFace)" if mina.llm else "Mina (Not configured)",
        "endpoints": {
            "medicines": {
                "GET /medicines": "List all medicines",
                "POST /medicines": "Add new medicine"
            },
            "chat": {
                "POST /chat": "Chat with Mina AI Agent"
            },
            "health": {
                "GET /health": "Health check"
            }
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MinaCare API",
        "ai_agent": "online" if mina.llm else "offline",
        "timestamp": datetime.now().isoformat()
    }


# Function 1: List all medicines
@app.get("/medicines", response_model=List[MedicineResponse])
def list_medicines():
    '''Get all medicines'''
    return medicines_db

# Function 2: Add medicine
@app.post("/medicines", response_model=MedicineResponse)
def add_medicine(medicine: Medicine):
    '''Add a new medicine'''
    new_medicine_data = {
        "id": len(medicines_db) + 1,
        "name": medicine.name,
        "dosage": medicine.dosage,
        "count": medicine.count,
        "expiration_date": medicine.expiration_date,
        "created_at": datetime.now().isoformat()
    }
    new_medicine = MedicineResponse(**new_medicine_data)
    medicines_db.append(new_medicine)
    return new_medicine


# Function 3: Start a chat
@app.post("/chat", response_model=ChatResponse)
async def chat_with_mina(chat: ChatMessage):
    """
    Chat with Mina AI Agent
    
    Mina analyzes user symptoms and provides:
    - Empathetic response
    - Medicine recommendations from user's inventory
    - General health advice
    - Doctor consultation recommendations
    
    Args:
        chat: ChatMessage with user's message
        
    Returns:
        ChatResponse with Mina's reply, timestamp, and sources
    """
    
    # Check if AI agent is available
    if not mina.llm:
        return ChatResponse(
            reply="⚠️ AI Agent is not configured. Please set HF_TOKEN or ANTHROPIC_API_KEY in .env file.",
            timestamp=datetime.now().isoformat(),
            sources=[]
        )
    
    try:
        # Log the chat request
        print(f"\n💬 Chat request: {chat.message}")
        
        # Process message through Mina agent
        print(medicines_db)
        result = await mina.chat(chat.message, medicines_db)
        
        # Log the response
        print(f"✅ Response generated ({len(result['reply'])} chars)\n")
        
        return ChatResponse(
            reply=result["reply"],
            timestamp=result["timestamp"],
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        # Log error
        print(f"❌ Chat error: {str(e)}\n")
        
        # Return friendly error message
        return ChatResponse(
            reply="I'm having trouble connecting right now. Please try again in a moment. 💙",
            timestamp=datetime.now().isoformat(),
            sources=[]
        )