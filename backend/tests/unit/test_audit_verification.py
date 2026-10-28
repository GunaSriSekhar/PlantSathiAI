"""
PlantSathi AI - Verification Audit Test Suite
Tests ML configuration, class label mappings, crop support rules,
uncertainty thresholds, and failure handling without fabricating outputs.
"""
try:
    import pytest
except ImportError:
    pytest = None

from app.services.disease_classifier import (
    DiseaseClassifier,
    DiseaseClassificationResult,
    is_crop_supported,
    _parse_label,
    SUPPORTED_CROPS,
    PLANT_VILLAGE_LABELS,
    _DISEASE_MODEL,
)
from app.services.plant_identifier import (
    PlantIdentifier,
    PlantIdentificationResult,
    _PRIMARY_MODEL,
    _FALLBACK_MODEL,
)
from app.services.confidence import ConfidenceEvaluator
from app.services.recommendations import recommendation_service
from app.ml.model_registry import (
    DISEASE_MODEL_ID,
    PLANT_ID_MODEL_ID,
    SUPPORTED_PLANTS,
    LABEL_TO_INDEX,
)


def test_model_identifiers_consistency():
    """Verify primary and fallback models match documented configurations."""
    assert _DISEASE_MODEL == "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    assert DISEASE_MODEL_ID == _DISEASE_MODEL
    assert _PRIMARY_MODEL == "umutbozdag/plant-identity"
    assert _FALLBACK_MODEL == "google/vit-base-patch16-224"
    assert PLANT_ID_MODEL_ID == _PRIMARY_MODEL


def test_plantvillage_38_classes_integrity():
    """Verify exact count, ordering, and bidirectional index mapping."""
    assert len(PLANT_VILLAGE_LABELS) == 38
    assert len(LABEL_TO_INDEX) == 38

    # Verify first, middle, and last indices
    assert PLANT_VILLAGE_LABELS[0] == "Apple___Apple_scab"
    assert LABEL_TO_INDEX["Apple___Apple_scab"] == 0

    assert PLANT_VILLAGE_LABELS[20] == "Potato___Early_blight"
    assert LABEL_TO_INDEX["Potato___Early_blight"] == 20

    assert PLANT_VILLAGE_LABELS[37] == "Tomato___healthy"
    assert LABEL_TO_INDEX["Tomato___healthy"] == 37


def test_supported_crops_detection():
    """Verify 14 agricultural crops are recognized and non-supported plants rejected."""
    # Check 14 crops are recognized
    test_cases_supported = [
        "Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange",
        "Peach", "Bell Pepper", "Potato", "Raspberry", "Soybean",
        "Squash", "Strawberry", "Tomato", "tomato vine", "sweet pepper"
    ]
    for crop in test_cases_supported:
        assert is_crop_supported(crop) is True, f"Expected {crop} to be supported"

    # Check non-supported species are rejected
    test_cases_unsupported = [
        "Rose", "Orchid", "Sunflower", "Oak tree", "Mango",
        "Neem", "Tulsi", "Ficus", "Monstera", "Bamboo", "Carnation"
    ]
    for non_crop in test_cases_unsupported:
        assert is_crop_supported(non_crop) is False, f"Expected {non_crop} to be unsupported"


def test_disease_label_parsing():
    """Verify parsing of PlantVillage label strings."""
    crop, disease, is_healthy = _parse_label("Tomato___Early_blight")
    assert crop.lower() == "tomato"
    assert "early blight" in disease.lower()
    assert is_healthy is False

    crop, disease, is_healthy = _parse_label("Apple___healthy")
    assert crop.lower() == "apple"
    assert is_healthy is True


def test_confidence_calibration():
    """Verify confidence evaluator prevents false certainty."""
    evaluator = ConfidenceEvaluator()

    # Disease confidence bands
    assert evaluator.assess_disease_confidence(0.95)["level"] == "high"
    assert evaluator.assess_disease_confidence(0.95)["reliable"] is True

    med = evaluator.assess_disease_confidence(0.50)
    assert med["level"] == "medium"
    assert med["warning"] is not None

    low = evaluator.assess_disease_confidence(0.25)
    assert low["level"] == "low"
    assert low["reliable"] is False

    insufficient = evaluator.assess_disease_confidence(0.08)
    assert insufficient["level"] == "insufficient"
    assert insufficient["reliable"] is False


def test_error_handling_no_fabrication():
    """Ensure that failed model execution produces error attributes, not fake predictions."""
    id_res = PlantIdentificationResult(
        predictions=[],
        model_name="test-model",
        device="cpu",
        error="Model weights not found",
    )
    assert len(id_res.predictions) == 0
    assert id_res.top_prediction is None
    assert id_res.is_reliable is False

    dis_res = DiseaseClassificationResult(
        label="unknown",
        crop="unknown",
        disease_name="unknown",
        is_healthy=False,
        confidence=0.0,
        model_name="test-model",
        device="cpu",
        error="Dependencies missing",
    )
    assert dis_res.confidence == 0.0
    assert dis_res.status == "error"
