"""
PlantSathi AI - Plant Disease Diagnosis Route
"""
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.database import get_db
from app.schemas.diagnosis import DiseaseResponse
from app.services.image_processing import ImageValidator, ImageValidationError
from app.services.disease_classifier import DiseaseClassifier
from app.services.confidence import ConfidenceEvaluator

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.diagnosis")
settings = get_settings()

validator = ImageValidator()
classifier = DiseaseClassifier()
evaluator = ConfidenceEvaluator()


@router.post("/diagnose", response_model=DiseaseResponse, summary="Diagnose plant leaf disease from photograph")
async def diagnose_disease(
    file: UploadFile = File(..., description="Leaf photograph (JPEG, PNG, WebP)"),
    db: AsyncSession = Depends(get_db),
) -> DiseaseResponse:
    """
    Accepts an uploaded leaf photograph, validates image format and dimensions,
    and runs the PlantVillage-trained disease classification model.
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
        result = await classifier.classify(pil_image)
    except Exception as e:
        logger.error(f"Inference error in disease diagnosis: {e}")
        return DiseaseResponse(
            scan_id=None,
            status="error",
            label=None,
            crop=None,
            disease_name=None,
            is_healthy=False,
            confidence=0.0,
            confidence_level="uncertain",
            supported=False,
            model_name="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
            warning="Disease classification failed. Please ensure the model weights are loaded.",
            error=str(e),
        )

    parsed = evaluator.parse_disease_label(result.label or "")
    is_healthy = parsed["healthy"] or (result.status == "healthy")
    conf_assessment = evaluator.assess_disease_confidence(result.confidence, settings.DISEASE_CONFIDENCE_THRESHOLD)

    return DiseaseResponse(
        scan_id=None,
        status=result.status,
        label=result.label,
        crop=parsed["crop"],
        disease_name=parsed["disease"],
        is_healthy=is_healthy,
        confidence=round(result.confidence or 0.0, 4),
        confidence_level=conf_assessment["level"],
        supported=result.supported,
        model_name=result.model_name,
        warning=conf_assessment["warning"],
        error=result.error,
    )
