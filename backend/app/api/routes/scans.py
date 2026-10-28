"""
PlantSathi AI - Scan History Routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.repositories.scan_repository import (
    get_all_scans,
    get_scan,
    delete_scan,
)
from app.schemas.scan import ScanSummary, ScanDetail

router = APIRouter()
logger = logging.getLogger("plantsathi.routes.scans")


@router.get("/scans", response_model=List[ScanSummary], summary="Retrieve recent scan history")
async def list_scans(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> List[ScanSummary]:
    """
    Returns real scan history stored in the SQLite database, newest first.
    Never returns fabricated or hardcoded placeholder items.
    """
    records = await get_all_scans(db, limit=limit, offset=offset)
    return [
        ScanSummary(
            id=r.id,
            created_at=r.created_at,
            plant_common_name=r.plant_common_name,
            plant_scientific_name=r.plant_scientific_name,
            disease_label=r.disease_label,
            disease_status=r.disease_status,
            plant_confidence=r.plant_confidence,
            disease_confidence=r.disease_confidence,
            image_filename=r.image_filename,
        )
        for r in records
    ]


@router.get("/scans/{scan_id}", response_model=ScanDetail, summary="Retrieve a full scan record by ID")
async def retrieve_scan(
    scan_id: str = Path(..., description="UUID of the scan"),
    db: AsyncSession = Depends(get_db),
) -> ScanDetail:
    """
    Fetch comprehensive details, recommendations, warnings, and model telemetry
    for a specific saved scan.
    """
    record = await get_scan(db, scan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scan record not found.")

    return ScanDetail(
        id=record.id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        plant_common_name=record.plant_common_name,
        plant_scientific_name=record.plant_scientific_name,
        plant_confidence=record.plant_confidence,
        plant_confidence_level=record.plant_confidence_level,
        plant_model=record.plant_model,
        plant_supported=record.plant_supported,
        plant_top_candidates=record.plant_top_candidates,
        disease_label=record.disease_label,
        disease_crop=record.disease_crop,
        disease_name=record.disease_name,
        disease_confidence=record.disease_confidence,
        disease_confidence_level=record.disease_confidence_level,
        disease_status=record.disease_status,
        disease_model=record.disease_model,
        disease_supported=record.disease_supported,
        disease_is_healthy=record.disease_is_healthy,
        warnings=record.warnings or [],
        recommendations=record.recommendations or [],
        analysis_duration_ms=record.analysis_duration_ms,
        image_filename=record.image_filename,
        image_stored=record.image_stored,
    )


@router.delete("/scans/{scan_id}", summary="Delete a scan record")
async def remove_scan(
    scan_id: str = Path(..., description="UUID of the scan to delete"),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete a scan record from the database.
    """
    success = await delete_scan(db, scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan record not found or already deleted.")
    return {"status": "success", "message": f"Scan {scan_id} deleted successfully."}
