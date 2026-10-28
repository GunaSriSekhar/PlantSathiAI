"""
PlantSathi AI - Chat Schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    scan_id: Optional[str] = None
    conversation_history: List[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    message: str
    suggestions: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    is_llm: bool = False
    disclaimer: str
