"""
PlantSathi AI - Combined Plant Analysis Route (POST /api/analyze)
Orchestrates plant identification, disease diagnosis, and care recommendations.
"""
from datetime import datetime, timezone
import logging
import time
import uuid
from typing import Optional, List

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.database import get_db
from app.repositories.scan_repository import create_scan
from app.schemas.identification import PlantCandidate
from app.schemas.scan import (
    AnalysisResponse,
    PlantResult,
    DiseaseResult,
    RecommendationItem,
    ModelsUsed,
)
from app.services.image_processing import ImageValidator, ImageValidationError
from app.services.plant_identifier import PlantIdentifier
from app.services.disease_classifier import DiseaseClassifier
from app.services.confidence import ConfidenceEvaluator
from app.services.recommendations import recommendation_service

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.analyze")
settings = get_settings()

validator = ImageValidator()
identifier = PlantIdentifier()
classifier = DiseaseClassifier()
evaluator = ConfidenceEvaluator()


@router.post("/analyze", response_model=AnalysisResponse, summary="Perform end-to-end plant identification and disease diagnosis")
async def analyze_plant(
    file: UploadFile = File(..., description="Photograph of plant or affected leaf"),
    save: bool = Query(True, description="Whether to persist this scan record in history"),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """
    Primary user workflow:
    1. Validates and preprocesses the uploaded image.
    2. Runs plant identification computer vision model.
    3. Evaluates if the plant species is supported by the disease classifier.
    4. Runs disease classification model on the leaf.
    5. Computes calibrated confidence and uncertainty warnings.
    6. Generates tailored, evidence-based agronomic recommendations.
    7. Optionally persists scan history in SQLite database.
    """
    start_time = time.perf_counter()
    scan_id = str(uuid.uuid4())
    warnings: List[str] = []

    # 1. Image Validation
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
        logger.error(f"Image validation exception: {e}")
        raise HTTPException(status_code=400, detail={"error": "invalid_image", "message": str(e)})

    # Optionally save image file
    saved_filename: Optional[str] = None
    try:
        saved_filename = validator.save_upload(pil_image, settings.upload_path)
    except Exception as e:
        logger.warning(f"Could not save uploaded image to disk: {e}")

    # 2. Plant Identification
    raw_plant_data = None
    plant_candidates: List[PlantCandidate] = []
    top_plant_name: Optional[str] = None
    top_plant_score: Optional[float] = None
    plant_model_name = settings.PLANT_ID_MODEL

    try:
        id_result = await identifier.identify(pil_image)
        plant_model_name = id_result.model_name
        raw_plant_data = {"predictions": id_result.predictions, "model": id_result.model_name}
        plant_candidates = [
            PlantCandidate(
                label=p.get("label", "Unknown"),
                score=round(float(p.get("score", 0.0)), 4),
                rank=i + 1,
            )
            for i, p in enumerate(id_result.predictions)
        ]
        if plant_candidates:
            top_plant_name = plant_candidates[0].label
            top_plant_score = plant_candidates[0].score

        if id_result.error:
            warnings.append(f"Plant identification warning: {id_result.error}")
    except Exception as e:
        logger.error(f"Plant identification inference failure: {e}")
        warnings.append("Plant identification model unavailable or encountered an error.")

    plant_conf = evaluator.assess_plant_confidence(top_plant_score, settings.PLANT_ID_CONFIDENCE_THRESHOLD)
    if plant_conf["warning"]:
        warnings.append(plant_conf["warning"])

    # 3. Check Crop Compatibility for Disease Classifier
    is_supported_crop = False
    if top_plant_name:
        is_supported_crop = classifier.is_crop_supported(top_plant_name)

    # 4. Disease Classification
    raw_disease_data = None
    disease_status = "unknown"
    disease_label = None
    disease_crop = None
    disease_name = None
    disease_conf_score = None
    disease_is_healthy = None
    disease_supported = is_supported_crop
    disease_model_name = settings.DISEASE_MODEL

    try:
        dis_result = await classifier.classify(pil_image)
        disease_model_name = dis_result.model_name
        raw_disease_data = {
            "status": dis_result.status,
            "label": dis_result.label,
            "confidence": dis_result.confidence,
            "model": dis_result.model_name,
        }
        disease_status = dis_result.status
        disease_label = dis_result.label
        disease_conf_score = round(dis_result.confidence or 0.0, 4)

        if dis_result.error:
            warnings.append(f"Disease classification notice: {dis_result.error}")
    except Exception as e:
        logger.error(f"Disease classification inference failure: {e}")
        disease_status = "error"
        warnings.append("Disease classification model unavailable or encountered an error.")

    if disease_label:
        parsed_dis = evaluator.parse_disease_label(disease_label)
        disease_crop = parsed_dis["crop"]
        disease_name = parsed_dis["disease"]
        disease_is_healthy = parsed_dis["healthy"] or (disease_status == "healthy")

    dis_conf = evaluator.assess_disease_confidence(disease_conf_score, settings.DISEASE_CONFIDENCE_THRESHOLD)
    if dis_conf["warning"] and disease_status != "healthy":
        warnings.append(dis_conf["warning"])

    if top_plant_name and not is_supported_crop:
        warnings.append(
            f"The identified plant '{top_plant_name}' is not one of the 14 crops supported by the disease classifier. "
            "Disease prediction is tentative and may reflect generalized leaf stress rather than a verified pathogen."
        )

    # 5. Generate Evidence-Based Recommendations
    raw_recs = recommendation_service.get_recommendations(
        plant_name=top_plant_name or "plant",
        disease_label=disease_label or "",
        is_healthy=bool(disease_is_healthy),
    )
    recommendations = [
        RecommendationItem(
            category=r.get("category", "General"),
            title=r.get("title", "Care Step"),
            description=r.get("description", ""),
            urgency=r.get("urgency", "medium"),
        )
        for r in raw_recs
    ]

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    created_at = datetime.now(timezone.utc)

    # 6. Database Persistence (when save is requested)
    if save:
        try:
            scan_payload = {
                "id": scan_id,
                "created_at": created_at,
                "plant_common_name": top_plant_name,
                "plant_scientific_name": None,
                "plant_confidence": top_plant_score,
                "plant_confidence_level": plant_conf["level"],
                "plant_model": plant_model_name,
                "plant_supported": True if top_plant_name else False,
                "plant_top_candidates": [c.model_dump() for c in plant_candidates],
                "disease_label": disease_label,
                "disease_crop": disease_crop,
                "disease_name": disease_name,
                "disease_confidence": disease_conf_score,
                "disease_confidence_level": dis_conf["level"],
                "disease_status": disease_status,
                "disease_model": disease_model_name,
                "disease_supported": is_supported_crop,
                "disease_is_healthy": disease_is_healthy,
                "warnings": warnings,
                "recommendations": [r.model_dump() for r in recommendations],
                "analysis_duration_ms": duration_ms,
                "image_filename": saved_filename,
                "image_stored": bool(saved_filename),
                "raw_plant_response": raw_plant_data,
                "raw_disease_response": raw_disease_data,
            }
            await create_scan(db, scan_payload)
            logger.info(f"Scan {scan_id} persisted to database successfully")
        except Exception as e:
            logger.error(f"Failed to persist scan record: {e}", exc_info=True)
            warnings.append("Note: Failed to save scan into local history.")

    # 7. Formulate structured response
    plant_result = PlantResult(
        common_name=top_plant_name,
        scientific_name=None,
        confidence=top_plant_score,
        confidence_level=plant_conf["level"],
        reliable=plant_conf["reliable"],
        supported=bool(top_plant_name),
        candidates=plant_candidates,
        warning=plant_conf["warning"],
    )

    disease_result = DiseaseResult(
        status=disease_status,
        label=disease_label,
        crop=disease_crop,
        disease_name=disease_name,
        is_healthy=disease_is_healthy,
        confidence=disease_conf_score,
        confidence_level=dis_conf["level"],
        supported=is_supported_crop,
        warning=dis_conf["warning"],
    )

    return AnalysisResponse(
        scan_id=scan_id,
        created_at=created_at,
        plant=plant_result,
        disease=disease_result,
        recommendations=recommendations,
        warnings=warnings,
        models=ModelsUsed(
            identification=plant_model_name,
            diagnosis=disease_model_name,
        ),
        analysis_duration_ms=duration_ms,
        image_filename=saved_filename,
    )

