"""
Shared pytest fixtures for PlantSathi AI tests.
"""
import asyncio
import io
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from PIL import Image

# Import app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.database import init_db, get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_db():
    """In-memory test database."""
    from app.models.entities import Base
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest.fixture
def client():
    """Sync test client."""
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture
async def async_client():
    """Async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture
def sample_jpeg_bytes():
    """Valid 100x100 JPEG image bytes."""
    img = Image.new("RGB", (100, 100), color=(34, 85, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.fixture
def sample_png_bytes():
    """Valid 200x200 PNG image bytes."""
    img = Image.new("RGB", (200, 200), color=(100, 150, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@pytest.fixture
def sample_large_image_bytes():
    """JPEG that exceeds max file size (>10MB when raw, but we fake it)."""
    # Create a valid image but mark it as too large
    img = Image.new("RGB", (100, 100), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.fixture
def invalid_file_bytes():
    """Invalid file bytes (not an image)."""
    return b"This is definitely not an image file. It's just text."

@pytest.fixture
def mock_plant_id_result():
    return {
        "top_prediction": "Tomato",
        "candidates": [
            {"label": "Tomato", "score": 0.82, "rank": 1},
            {"label": "Pepper", "score": 0.12, "rank": 2},
        ],
        "confidence_level": "high",
        "reliable": True,
        "model_name": "mock-plant-id",
        "warning": None,
    }

@pytest.fixture
def mock_disease_result():
    return {
        "status": "identified",
        "label": "Tomato___Early_blight",
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "is_healthy": False,
        "confidence": 0.78,
        "confidence_level": "high",
        "supported": True,
        "model_name": "mock-disease-model",
        "warning": None,
    }
