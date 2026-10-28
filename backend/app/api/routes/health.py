"""
PlantSathi AI - Health and Model Status Routes
"""
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

from fastapi import APIRouter
from app.core.config import get_settings
from app.ml.model_loader import get_model_loader

router = APIRouter()
settings = get_settings()
logger = logging.getLogger("plantsathi.health")


@router.get("/health", summary="Health check endpoint")
async def health_check() -> Dict[str, Any]:
    """
    Returns API health status, version, and server timestamp.
    """
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/models/status", summary="Model registry and inference status")
async def models_status() -> List[Dict[str, Any]]:
    """
    Returns availability, loaded device, and status for all integrated ML models.
    """
    loader = get_model_loader()
    status_info = loader.get_status()
    return status_info.get("all", [])
