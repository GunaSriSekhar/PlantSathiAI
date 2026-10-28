"""
Tests for scan CRUD operations using in-memory test database.
"""
import uuid
import pytest

from app.repositories.scan_repository import ScanRepository


@pytest.mark.asyncio
async def test_create_scan(test_db):
    repo = ScanRepository()
    scan_data = {
        "id": str(uuid.uuid4()),
        "plant_common_name": "Tomato",
        "plant_scientific_name": "Solanum lycopersicum",
        "plant_confidence": 0.82,
        "disease_label": "Tomato___Early_blight",
        "disease_status": "identified",
        "disease_confidence": 0.75,
        "warnings": [],
        "recommendations": [],
    }
    scan = await repo.create_scan(test_db, scan_data)
    assert scan.id == scan_data["id"]
    assert scan.plant_common_name == "Tomato"


@pytest.mark.asyncio
async def test_get_scan(test_db):
    repo = ScanRepository()
    scan_id = str(uuid.uuid4())
    await repo.create_scan(test_db, {"id": scan_id, "plant_common_name": "Rose", "disease_status": "healthy"})
    scan = await repo.get_scan(test_db, scan_id)
    assert scan is not None
    assert scan.plant_common_name == "Rose"


@pytest.mark.asyncio
async def test_get_nonexistent_scan(test_db):
    repo = ScanRepository()
    scan = await repo.get_scan(test_db, "nonexistent-id")
    assert scan is None


@pytest.mark.asyncio
async def test_delete_scan(test_db):
    repo = ScanRepository()
    scan_id = str(uuid.uuid4())
    await repo.create_scan(test_db, {"id": scan_id, "plant_common_name": "Basil", "disease_status": "healthy"})
    deleted = await repo.delete_scan(test_db, scan_id)
    assert deleted is True
    scan = await repo.get_scan(test_db, scan_id)
    assert scan is None


@pytest.mark.asyncio
async def test_list_scans(test_db):
    repo = ScanRepository()
    for i in range(3):
        await repo.create_scan(test_db, {
            "id": str(uuid.uuid4()),
            "plant_common_name": f"Plant {i}",
            "disease_status": "healthy"
        })
    scans = await repo.get_all_scans(test_db, limit=10, offset=0)
    assert len(scans) >= 3
