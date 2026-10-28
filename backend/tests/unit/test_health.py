"""
Tests for health and model status endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client):
    """Health endpoint returns 200 with status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


def test_models_status_endpoint(client):
    """Model status endpoint returns list of models."""
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_root_endpoint(client):
    """Root endpoint returns metadata and links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "PlantSathi" in data.get("name", "")
