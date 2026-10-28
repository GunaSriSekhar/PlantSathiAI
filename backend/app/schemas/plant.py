"""
PlantSathi AI - Saved Plant Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SavedPlantCreate(BaseModel):
    common_name: str = Field(..., min_length=1)
    scientific_name: Optional[str] = None
    notes: Optional[str] = None
    scan_id: Optional[str] = None

class SavedPlantResponse(BaseModel):
    id: str
    created_at: datetime
    common_name: str
    scientific_name: Optional[str] = None
    notes: Optional[str] = None
    scan_id: Optional[str] = None
