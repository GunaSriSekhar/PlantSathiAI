"""
PlantSathi AI - Plant Species Identification Route
"""
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.database import get_db
from app.schemas.identification import IdentificationResponse, PlantCandidate
from app.services.image_processing import ImageValidator, ImageValidationError
from app.services.plant_identifier import PlantIdentifier
from app.services.confidence import ConfidenceEvaluator

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.identification")
settings = get_settings()

validator = ImageValidator()
identifier = PlantIdentifier()
evaluator = ConfidenceEvaluator()


@router.post("/identify", response_model=IdentificationResponse, summary="Identify plant species from an uploaded photo")
async def identify_plant(
    file: UploadFile = File(..., description="Plant photograph (JPEG, PNG, WebP)"),
    db: AsyncSession = Depends(get_db),
) -> IdentificationResponse:
    """
    Accepts an uploaded plant photograph, validates image integrity,
    and runs genuine computer vision classification to identify the species.
    """
    try:
        content = await file.read()
        pil_image = await validator.validate_and_load(
            file_bytes=content,
            filename=file.filename or "upload.jpg",
            content_type=file.content_type or "image/jpeg",
            max_size_bytes=settings.max_file_size_bytes,
        )
    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail={"error": e.code, "message": e.message})
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise HTTPException(status_code=400, detail={"error": "invalid_image", "message": str(e)})

    try:
        result = await identifier.identify(pil_image)
    except Exception as e:
        logger.error(f"Inference error in plant identification: {e}")
        return IdentificationResponse(
            scan_id=None,
            candidates=[],
            top_prediction=None,
            confidence_level="uncertain",
            reliable=False,
            model_name="umutbozdag/plant-identity",
            warning="Plant identification inference failed. The model might still be downloading.",
            error=str(e),
        )

    candidates = [
        PlantCandidate(
            label=p.get("label", "Unknown"),
            score=round(float(p.get("score", 0.0)), 4),
            rank=i + 1,
        )
        for i, p in enumerate(result.predictions)
    ]

    top_pred = candidates[0] if candidates else None
    top_score = top_pred.score if top_pred else 0.0
    conf_assessment = evaluator.assess_plant_confidence(top_score, settings.PLANT_ID_CONFIDENCE_THRESHOLD)

    return IdentificationResponse(
        scan_id=None,
        candidates=candidates,
        top_prediction=top_pred.label if top_pred else None,
        confidence_level=conf_assessment["level"],
        reliable=conf_assessment["reliable"],
        model_name=result.model_name,
        warning=conf_assessment["warning"],
        error=result.error,
    )
