"""
PlantSathi AI Backend - Plant Identification Pydantic v2 Schemas
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PlantCandidate(BaseModel):
    """A single plant identification prediction."""

    label: str = Field(..., description="Plant species / common name as returned by the model.")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1.")
    rank: int = Field(..., ge=1, description="Rank of this prediction (1 = highest confidence).")


class IdentificationResponse(BaseModel):
    """Response returned by the /api/identify endpoint."""

    scan_id: Optional[str] = Field(
        None,
        description="Unique scan identifier, present when the result was saved to the database.",
    )
    candidates: List[PlantCandidate] = Field(
        default_factory=list,
        description="Top-5 plant candidates ordered by descending confidence.",
    )
    top_prediction: Optional[str] = Field(
        None,
        description="Label of the highest-confidence candidate, or null if unavailable.",
    )
    confidence_level: str = Field(
        ...,
        description="Human-readable confidence band: 'high', 'medium', 'low', or 'uncertain'.",
    )
    reliable: bool = Field(
        ...,
        description="True when top confidence exceeds the minimum reliability threshold (15 %).",
    )
    model_name: str = Field(
        ...,
        description="HuggingFace model identifier used for this identification.",
    )
    warning: Optional[str] = Field(
        None,
        description="Non-null when the result may be unreliable (e.g. low confidence).",
    )
    error: Optional[str] = Field(
        None,
        description="Non-null when identification failed or the model is unavailable.",
    )
