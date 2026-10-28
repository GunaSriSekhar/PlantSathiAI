"""
PlantSathi AI Backend - Scan Repository
Repository pattern for ScanRecord CRUD operations using SQLAlchemy async sessions.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import ScanRecord

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Repository functions
# ---------------------------------------------------------------------------


async def create_scan(db: AsyncSession, scan_data: dict) -> ScanRecord:
    """
    Persist a new ``ScanRecord`` to the database.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    scan_data:
        Dictionary of field values to populate on the new record.
        An ``id`` key will be generated if not supplied.

    Returns
    -------
    ScanRecord
        The newly created, database-persisted entity.
    """
    scan_data.setdefault("id", str(uuid.uuid4()))
    scan_data.setdefault("created_at", _utcnow())

    record = ScanRecord(**scan_data)
    db.add(record)
    await db.flush()  # populate server-side defaults (e.g. created_at)
    await db.refresh(record)

    logger.debug("Created ScanRecord id=%s", record.id)
    return record


async def get_scan(db: AsyncSession, scan_id: str) -> Optional[ScanRecord]:
    """
    Retrieve a single ``ScanRecord`` by its primary key.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    scan_id:
        UUID string of the scan to retrieve.

    Returns
    -------
    ScanRecord | None
        The matching entity or ``None`` if not found.
    """
    result = await db.execute(
        select(ScanRecord).where(ScanRecord.id == scan_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        logger.debug("ScanRecord id=%s not found.", scan_id)
    return record


async def get_all_scans(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[ScanRecord]:
    """
    Return a paginated list of all scan records, newest first.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    limit:
        Maximum number of records to return (default 50).
    offset:
        Number of records to skip from the start (default 0).

    Returns
    -------
    list[ScanRecord]
        Ordered list of scan records.
    """
    result = await db.execute(
        select(ScanRecord)
        .order_by(ScanRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    records = list(result.scalars().all())
    logger.debug("get_all_scans: returned %d records (limit=%d offset=%d)", len(records), limit, offset)
    return records


async def delete_scan(db: AsyncSession, scan_id: str) -> bool:
    """
    Delete a ``ScanRecord`` by its primary key.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    scan_id:
        UUID string of the scan to delete.

    Returns
    -------
    bool
        ``True`` if a record was deleted, ``False`` if not found.
    """
    record = await get_scan(db, scan_id)
    if record is None:
        return False

    await db.delete(record)
    await db.flush()
    logger.debug("Deleted ScanRecord id=%s", scan_id)
    return True


async def get_recent_scans(db: AsyncSession, n: int = 5) -> list[ScanRecord]:
    """
    Return the *n* most recent scan records.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    n:
        Number of recent scans to retrieve (default 5).

    Returns
    -------
    list[ScanRecord]
        The *n* most recently created scan records, newest first.
    """
    result = await db.execute(
        select(ScanRecord)
        .order_by(ScanRecord.created_at.desc())
        .limit(n)
    )
    records = list(result.scalars().all())
    logger.debug("get_recent_scans: returned %d records (n=%d)", len(records), n)
    return records


async def update_scan(db: AsyncSession, scan_id: str, update_data: dict) -> Optional[ScanRecord]:
    """
    Partially update a ``ScanRecord``.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.
    scan_id:
        UUID string of the scan to update.
    update_data:
        Dictionary of field names → new values to apply.

    Returns
    -------
    ScanRecord | None
        The updated entity, or ``None`` if not found.
    """
    record = await get_scan(db, scan_id)
    if record is None:
        return None

    update_data["updated_at"] = _utcnow()
    for field, value in update_data.items():
        if hasattr(record, field):
            setattr(record, field, value)

    await db.flush()
    await db.refresh(record)
    logger.debug("Updated ScanRecord id=%s fields=%s", scan_id, list(update_data.keys()))
    return record


class ScanRepository:
    """Class interface for Scan repository operations."""
    async def create_scan(self, db: AsyncSession, scan_data: dict) -> ScanRecord:
        return await create_scan(db, scan_data)

    async def get_scan(self, db: AsyncSession, scan_id: str) -> Optional[ScanRecord]:
        return await get_scan(db, scan_id)

    async def get_all_scans(self, db: AsyncSession, limit: int = 50, offset: int = 0) -> list[ScanRecord]:
        return await get_all_scans(db, limit, offset)

    async def delete_scan(self, db: AsyncSession, scan_id: str) -> bool:
        return await delete_scan(db, scan_id)

    async def get_recent_scans(self, db: AsyncSession, n: int = 5) -> list[ScanRecord]:
        return await get_recent_scans(db, n)

