"""
PlantSathi AI - Scan and Analysis Schemas
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.identification import PlantCandidate

class RecommendationItem(BaseModel):
    category: str = Field(..., description="e.g. 'immediate_action', 'watering', 'sunlight', 'disease_control'")
    title: str
    description: str
    urgency: str = Field("medium", description="'high', 'medium', or 'low'")


class PlantResult(BaseModel):
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    confidence: Optional[float] = None
    confidence_level: Optional[str] = "unknown"
    reliable: bool = False
    supported: bool = True
    candidates: List[PlantCandidate] = Field(default_factory=list)
    warning: Optional[str] = None


class DiseaseResult(BaseModel):
    status: str = Field("unknown", description="'identified', 'healthy', 'unsupported', 'uncertain', 'error'")
    label: Optional[str] = None
    crop: Optional[str] = None
    disease_name: Optional[str] = None
    is_healthy: Optional[bool] = None
    confidence: Optional[float] = None
    confidence_level: Optional[str] = "unknown"
    supported: bool = True
    warning: Optional[str] = None


class ModelsUsed(BaseModel):
    identification: Optional[str] = None
    diagnosis: Optional[str] = None


class AnalysisResponse(BaseModel):
    scan_id: str
    created_at: datetime
    plant: PlantResult
    disease: DiseaseResult
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    models: ModelsUsed
    analysis_duration_ms: Optional[float] = None
    image_filename: Optional[str] = None


class ScanSummary(BaseModel):
    id: str
    created_at: datetime
    plant_common_name: Optional[str] = None
    plant_scientific_name: Optional[str] = None
    disease_label: Optional[str] = None
    disease_status: str
    plant_confidence: Optional[float] = None
    disease_confidence: Optional[float] = None
    image_filename: Optional[str] = None


class ScanDetail(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    plant_common_name: Optional[str] = None
    plant_scientific_name: Optional[str] = None
    plant_confidence: Optional[float] = None
    plant_confidence_level: Optional[str] = None
    plant_model: Optional[str] = None
    plant_supported: bool = False
    plant_top_candidates: Optional[List[Any]] = None

    disease_label: Optional[str] = None
    disease_crop: Optional[str] = None
    disease_name: Optional[str] = None
    disease_confidence: Optional[float] = None
    disease_confidence_level: Optional[str] = None
    disease_status: str
    disease_model: Optional[str] = None
    disease_supported: bool = False
    disease_is_healthy: Optional[bool] = None

    warnings: List[str] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    analysis_duration_ms: Optional[float] = None
    image_filename: Optional[str] = None
    image_stored: bool = False
