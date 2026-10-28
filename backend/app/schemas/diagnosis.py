"""
PlantSathi AI Backend - Disease Diagnosis Pydantic v2 Schemas
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DiseaseResponse(BaseModel):
    """Response returned by the /api/diagnose endpoint."""

    scan_id: Optional[str] = Field(
        None,
        description="Unique scan identifier when the result is persisted.",
    )
    status: str = Field(
        ...,
        description="Overall diagnosis status: 'healthy', 'diseased', 'uncertain', or 'error'.",
    )
    label: Optional[str] = Field(
        None,
        description="Raw PlantVillage class label (e.g. 'Tomato___Early_blight').",
    )
    crop: Optional[str] = Field(
        None,
        description="Human-readable crop name extracted from the disease label.",
    )
    disease_name: Optional[str] = Field(
        None,
        description="Human-readable disease name extracted from the disease label.",
    )
    is_healthy: bool = Field(
        ...,
        description="True when the model predicted the plant is healthy.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence for the top disease prediction.",
    )
    confidence_level: str = Field(
        ...,
        description="Human-readable confidence band: 'high', 'medium', 'low', or 'uncertain'.",
    )
    supported: bool = Field(
        ...,
        description=(
            "True when the identified plant species belongs to one of the "
            "38 PlantVillage crop classes the disease model was trained on."
        ),
    )
    model_name: str = Field(
        ...,
        description="HuggingFace model identifier used for disease classification.",
    )
    warning: Optional[str] = Field(
        None,
        description="Non-null when the result may be unreliable or crop is not supported.",
    )
    error: Optional[str] = Field(
        None,
        description="Non-null when classification failed or the model is unavailable.",
    )
