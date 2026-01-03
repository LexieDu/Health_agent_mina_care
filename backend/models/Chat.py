from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    timestamp: str