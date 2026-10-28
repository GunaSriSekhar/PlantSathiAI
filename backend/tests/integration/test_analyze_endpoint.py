"""
Integration tests for the combined analysis endpoint.
"""
import io
import pytest
from PIL import Image
from unittest.mock import patch, AsyncMock, MagicMock


def make_test_image_bytes(width=100, height=100):
    img = Image.new("RGB", (width, height), color=(34, 100, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_analyze_with_mocked_models(async_client):
    """
    Integration test with mocked ML inference.
    Tests the full /api/analyze workflow.
    """
    img_bytes = make_test_image_bytes()

    with patch("app.services.plant_identifier.PlantIdentifier.identify", new_callable=AsyncMock) as mock_id, \
         patch("app.services.disease_classifier.DiseaseClassifier.classify", new_callable=AsyncMock) as mock_dis:

        mock_id.return_value = MagicMock(
            predictions=[{"label": "Tomato", "score": 0.82}],
            model_name="mock-plant-id",
            device="cpu",
            error=None,
        )
        mock_dis.return_value = MagicMock(
            label="Tomato___Early_blight",
            confidence=0.78,
            status="identified",
            error=None,
            supported=True,
            model_name="mock-disease-model",
        )

        response = await async_client.post(
            "/api/analyze?save=false",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["plant"]["common_name"] == "Tomato"
    assert data["disease"]["disease_name"] == "Early Blight"
    assert len(data["recommendations"]) > 0


def test_analyze_no_file(client):
    """Analyze endpoint requires a file parameter."""
    response = client.post("/api/analyze")
    assert response.status_code == 422


def test_analyze_invalid_file(client):
    """Non-image file should be rejected with 400 Bad Request."""
    fake_file = io.BytesIO(b"this is plain text not an image")
    response = client.post(
        "/api/analyze",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code in [400, 422]


def test_health_check_integration(client):
    """Health check works end to end."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
