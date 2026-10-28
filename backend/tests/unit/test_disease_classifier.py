"""
Tests for disease classifier model wrapper and crop support logic.
"""
try:
    import pytest
except ImportError:
    class _MockPytest:
        class mark:
            @staticmethod
            def asyncio(fn): return fn
            @staticmethod
            def real_model(fn): return fn
    pytest = _MockPytest()


from app.services.disease_classifier import (
    DiseaseClassifier,
    DiseaseClassificationResult,
    SUPPORTED_CROPS,
    PLANT_VILLAGE_LABELS,
)


def test_label_list_is_complete():
    """Verify all 38 PlantVillage labels are defined."""
    assert len(PLANT_VILLAGE_LABELS) == 38


def test_disease_result_status_property():
    """Verify DiseaseClassificationResult status property dynamically computes state."""
    res_healthy = DiseaseClassificationResult(
        label="Tomato___healthy",
        crop="Tomato",
        disease_name="healthy",
        is_healthy=True,
        confidence=0.88,
        model_name="test",
        device="cpu",
    )
    assert res_healthy.status == "healthy"

    res_diseased = DiseaseClassificationResult(
        label="Tomato___Early_blight",
        crop="Tomato",
        disease_name="Early blight",
        is_healthy=False,
        confidence=0.88,
        model_name="test",
        device="cpu",
    )
    assert res_diseased.status == "identified"

    res_err = DiseaseClassificationResult(
        label="unknown",
        crop="unknown",
        disease_name="unknown",
        is_healthy=False,
        confidence=0.0,
        model_name="test",
        device="cpu",
        error="Model missing",
    )
    assert res_err.status == "error"

    res_unsupported = DiseaseClassificationResult(
        label="Tomato___Early_blight",
        crop="Tomato",
        disease_name="Early blight",
        is_healthy=False,
        confidence=0.88,
        model_name="test",
        device="cpu",
        supported=False,
    )
    assert res_unsupported.status == "unsupported"



def test_supported_crops_list():
    """Verify crops are appropriately listed."""
    expected = ["tomato", "potato", "pepper", "apple", "grape"]
    for crop in expected:
        assert crop in SUPPORTED_CROPS


def test_tomato_is_supported():
    classifier = DiseaseClassifier()
    assert classifier.is_crop_supported("Tomato") is True
    assert classifier.is_crop_supported("tomato plant") is True


def test_unsupported_plant():
    classifier = DiseaseClassifier()
    assert classifier.is_crop_supported("Rose") is False
    assert classifier.is_crop_supported("Orchid") is False
    assert classifier.is_crop_supported("Unknown Plant") is False


@pytest.mark.asyncio
@pytest.mark.real_model
async def test_classify_with_real_model(sample_jpeg_bytes):
    """
    Integration test with real model weights when downloaded.
    Skipped in CI with: pytest -m "not real_model".
    """
    from PIL import Image
    import io

    classifier = DiseaseClassifier()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))
    result = await classifier.classify(img)
    assert result is not None
    assert hasattr(result, "label") or hasattr(result, "error")
