"""
PlantSathi AI - Saved Plants Route
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.entities import SavedPlant
from app.schemas.plant import SavedPlantCreate, SavedPlantResponse

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.plants")


@router.get("/plants", response_model=List[SavedPlantResponse], summary="List user saved plants")
async def list_saved_plants(
    db: AsyncSession = Depends(get_db),
) -> List[SavedPlantResponse]:
    """
    Returns user bookmarked plants.
    """
    result = await db.execute(select(SavedPlant).order_by(SavedPlant.created_at.desc()))
    records = result.scalars().all()
    return [
        SavedPlantResponse(
            id=r.id,
            created_at=r.created_at,
            common_name=r.common_name,
            scientific_name=r.scientific_name,
            notes=r.notes,
            scan_id=r.scan_id,
        )
        for r in records
    ]


@router.post("/plants", response_model=SavedPlantResponse, summary="Save a plant to your collection")
async def save_plant(
    data: SavedPlantCreate,
    db: AsyncSession = Depends(get_db),
) -> SavedPlantResponse:
    """
    Save a plant with optional notes and scan association.
    """
    new_plant = SavedPlant(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        common_name=data.common_name,
        scientific_name=data.scientific_name,
        notes=data.notes,
        scan_id=data.scan_id,
    )
    db.add(new_plant)
    await db.flush()
    await db.refresh(new_plant)
    return SavedPlantResponse(
        id=new_plant.id,
        created_at=new_plant.created_at,
        common_name=new_plant.common_name,
        scientific_name=new_plant.scientific_name,
        notes=new_plant.notes,
        scan_id=new_plant.scan_id,
    )


@router.delete("/plants/{plant_id}", summary="Delete a saved plant")
async def remove_saved_plant(
    plant_id: str = Path(..., description="UUID of saved plant"),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a plant from saved collection.
    """
    result = await db.execute(select(SavedPlant).where(SavedPlant.id == plant_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Saved plant not found.")

    await db.delete(record)
    await db.flush()
    return {"status": "success", "message": f"Plant {plant_id} removed."}
