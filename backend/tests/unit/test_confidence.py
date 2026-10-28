"""
Tests for confidence evaluation logic and label parsing.
"""
try:
    import pytest
except ImportError:
    pytest = None

from app.services.confidence import ConfidenceEvaluator


def test_high_confidence():
    evaluator = ConfidenceEvaluator()
    result = evaluator.assess_disease_confidence(0.85, threshold=0.40)
    assert result["level"] == "high"
    assert result["reliable"] is True
    assert result["warning"] is None


def test_medium_confidence():
    evaluator = ConfidenceEvaluator()
    result = evaluator.assess_disease_confidence(0.55, threshold=0.40)
    assert result["level"] == "medium"
    assert result["reliable"] is True


def test_low_confidence():
    evaluator = ConfidenceEvaluator()
    result = evaluator.assess_disease_confidence(0.30, threshold=0.40)
    assert result["level"] == "low"
    assert result["reliable"] is False
    assert result["warning"] is not None


def test_insufficient_confidence():
    evaluator = ConfidenceEvaluator()
    result = evaluator.assess_disease_confidence(0.05, threshold=0.40)
    assert result["level"] == "insufficient"
    assert result["reliable"] is False


def test_healthy_class_detection():
    evaluator = ConfidenceEvaluator()
    assert evaluator.is_healthy_class("Tomato___healthy") is True
    assert evaluator.is_healthy_class("Tomato___Early_blight") is False
    assert evaluator.is_healthy_class("Apple___healthy") is True


def test_disease_label_parsing():
    evaluator = ConfidenceEvaluator()
    result = evaluator.parse_disease_label("Tomato___Early_blight")
    assert result["crop"] == "Tomato"
    assert result["healthy"] is False
    assert "Early Blight" in result["disease"]

    result2 = evaluator.parse_disease_label("Apple___healthy")
    assert result2["crop"] == "Apple"
    assert result2["healthy"] is True
