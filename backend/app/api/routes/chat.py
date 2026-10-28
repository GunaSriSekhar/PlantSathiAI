"""
PlantSathi AI - Conversational AI Plant Doctor Route
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.scan_repository import get_scan
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_doctor import ai_doctor

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.chat")


@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI Plant Doctor")
async def chat_with_doctor(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Provides context-aware agronomic guidance.
    If a scan_id is provided, incorporates actual model predictions into the advice.
    Clearly discloses that it is a rule-based expert system without pretending to be an LLM.
    """
    scan_context: Optional[Dict[str, Any]] = None

    if request.scan_id:
        try:
            record = await get_scan(db, request.scan_id)
            if record:
                scan_context = {
                    "plant_name": record.plant_common_name,
                    "disease_name": record.disease_name or record.disease_label,
                    "disease_status": record.disease_status,
                    "is_healthy": record.disease_is_healthy,
                    "disease_confidence": record.disease_confidence,
                }
        except Exception as e:
            logger.warning(f"Could not load scan context for chat: {e}")

    try:
        response = await ai_doctor.get_response(
            message=request.message,
            scan_context=scan_context,
        )
        return ChatResponse(
            message=response.message,
            suggestions=response.suggestions,
            related_topics=response.related_topics,
            is_llm=response.is_llm,
            disclaimer=response.disclaimer,
        )
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error generating care response.")
