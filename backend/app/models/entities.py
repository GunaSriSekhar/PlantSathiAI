"""
PlantSathi AI Backend - ORM Entity Models
SQLAlchemy ORM models for ScanRecord and SavedPlant.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# ScanRecord
# ---------------------------------------------------------------------------


class ScanRecord(Base):
    """
    Represents a single plant-scan analysis request and its results.

    Stores both the raw model responses and the processed, human-readable
    outputs so the frontend can display rich diagnostic information without
    re-running inference.
    """

    __tablename__ = "scan_records"

    # ------------------------------------------------------------------
    # Identity / timestamps
    # ------------------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_new_uuid,
        doc="UUID primary key for this scan record.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=_utcnow,
        nullable=False,
        doc="UTC timestamp when the scan was created.",
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=_utcnow,
        nullable=True,
        doc="UTC timestamp of the last update to this record.",
    )

    # ------------------------------------------------------------------
    # Plant identification results
    # ------------------------------------------------------------------
    plant_common_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Common name of the identified plant (e.g. 'Tomato').",
    )
    plant_scientific_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Scientific/latin name of the identified plant.",
    )
    plant_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Confidence score [0, 1] from the plant-identification model.",
    )
    plant_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the plant-identification model used.",
    )
    plant_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the identified plant is supported by the disease model.",
    )

    # ------------------------------------------------------------------
    # Disease detection results
    # ------------------------------------------------------------------
    disease_label: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Raw PlantVillage class label returned by the disease model.",
    )
    disease_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Confidence score [0, 1] from the disease-detection model.",
    )
    disease_status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc=(
            "High-level disease status.  One of: "
            "'identified', 'healthy', 'unsupported', 'uncertain', 'error'."
        ),
    )
    disease_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the disease-detection model used.",
    )
    disease_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether disease detection was attempted (plant is in training set).",
    )

    # ------------------------------------------------------------------
    # Advisory outputs
    # ------------------------------------------------------------------
    warnings: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        doc="List of warning strings generated during analysis.",
    )
    recommendations: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        doc="Structured list of recommendation dictionaries for the user.",
    )

    # ------------------------------------------------------------------
    # Image metadata
    # ------------------------------------------------------------------
    image_filename: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="Filename of the uploaded image as stored on disk.",
    )
    image_stored: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the image was successfully persisted to the upload directory.",
    )

    # ------------------------------------------------------------------
    # Performance metrics
    # ------------------------------------------------------------------
    analysis_duration_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="End-to-end inference time in milliseconds.",
    )

    # ------------------------------------------------------------------
    # Raw model responses (stored for debugging / re-processing)
    # ------------------------------------------------------------------
    raw_plant_response: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        doc="Full, unprocessed JSON response from the plant-identification model.",
    )
    raw_disease_response: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        doc="Full, unprocessed JSON response from the disease-detection model.",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    saved_plant: Mapped["SavedPlant | None"] = relationship(
        "SavedPlant",
        back_populates="scan",
        uselist=False,
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ScanRecord id={self.id!r} "
            f"plant={self.plant_common_name!r} "
            f"status={self.disease_status!r}>"
        )


# ---------------------------------------------------------------------------
# SavedPlant
# ---------------------------------------------------------------------------


class SavedPlant(Base):
    """
    A plant that the user has explicitly saved to their collection.

    Links back to the originating ``ScanRecord`` when available.
    """

    __tablename__ = "saved_plants"

    # ------------------------------------------------------------------
    # Identity / timestamps
    # ------------------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_new_uuid,
        doc="UUID primary key for this saved plant.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
        doc="UTC timestamp when the plant was saved.",
    )

    # ------------------------------------------------------------------
    # Plant info
    # ------------------------------------------------------------------
    common_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Common name of the saved plant.",
    )
    scientific_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Scientific name of the saved plant.",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Free-text notes entered by the user about this plant.",
    )

    # ------------------------------------------------------------------
    # Foreign key to the originating scan
    # ------------------------------------------------------------------
    scan_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("scan_records.id", ondelete="SET NULL"),
        nullable=True,
        doc="ID of the ScanRecord that identified this plant (optional).",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    scan: Mapped["ScanRecord | None"] = relationship(
        "ScanRecord",
        back_populates="saved_plant",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SavedPlant id={self.id!r} "
            f"name={self.common_name!r} "
            f"scan_id={self.scan_id!r}>"
        )
