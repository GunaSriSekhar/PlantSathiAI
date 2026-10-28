"""
PlantSathi AI - Standalone Test Suite Runner
Runs all unit verification tests using pure Python and standard library.
"""
import sys
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def run_suite():
    print("=" * 70)
    print("       PLANTSATHI AI - AUTOMATED VERIFICATION AUDIT RUNNER       ")
    print("=" * 70)

    # 1. Audit Verification Tests
    print("\n[SUITE 1] Running Audit Verification Suite (test_audit_verification.py)...")
    from tests.unit.test_audit_verification import (
        test_model_identifiers_consistency,
        test_plantvillage_38_classes_integrity,
        test_supported_crops_detection,
        test_disease_label_parsing,
        test_confidence_calibration,
        test_error_handling_no_fabrication,
    )
    test_model_identifiers_consistency()
    print("  PASS: test_model_identifiers_consistency")
    test_plantvillage_38_classes_integrity()
    print("  PASS: test_plantvillage_38_classes_integrity (38 classes bidirectional)")
    test_supported_crops_detection()
    print("  PASS: test_supported_crops_detection (14 crops verified, non-crops filtered)")
    test_disease_label_parsing()
    print("  PASS: test_disease_label_parsing")
    test_confidence_calibration()
    print("  PASS: test_confidence_calibration (calibrated uncertainty thresholds)")
    test_error_handling_no_fabrication()
    print("  PASS: test_error_handling_no_fabrication (fails cleanly without fake scores)")

    # 2. Disease Classifier Unit Tests
    print("\n[SUITE 2] Running Disease Classifier Suite (test_disease_classifier.py)...")
    from tests.unit.test_disease_classifier import (
        test_label_list_is_complete,
        test_disease_result_status_property,
        test_supported_crops_list,
        test_tomato_is_supported,
        test_unsupported_plant,
    )
    test_label_list_is_complete()
    print("  PASS: test_label_list_is_complete")
    test_disease_result_status_property()
    print("  PASS: test_disease_result_status_property (status property dynamically computed)")
    test_supported_crops_list()
    print("  PASS: test_supported_crops_list")
    test_tomato_is_supported()
    print("  PASS: test_tomato_is_supported")
    test_unsupported_plant()
    print("  PASS: test_unsupported_plant")

    # 3. Confidence Evaluator Unit Tests
    print("\n[SUITE 3] Running Confidence Evaluator Suite (test_confidence.py)...")
    from tests.unit.test_confidence import (
        test_high_confidence,
        test_medium_confidence,
        test_low_confidence,
        test_insufficient_confidence,
        test_healthy_class_detection,
        test_disease_label_parsing as test_conf_label_parsing,
    )
    test_high_confidence()
    print("  PASS: test_high_confidence")
    test_medium_confidence()
    print("  PASS: test_medium_confidence")
    test_low_confidence()
    print("  PASS: test_low_confidence")
    test_insufficient_confidence()
    print("  PASS: test_insufficient_confidence")
    test_healthy_class_detection()
    print("  PASS: test_healthy_class_detection")
    test_conf_label_parsing()
    print("  PASS: test_disease_label_parsing")

    # 4. Recommendation Engine Unit Tests
    print("\n[SUITE 4] Running Recommendation Engine Checks...")
    from app.services.recommendations import recommendation_service
    recs_healthy = recommendation_service.get_recommendations("Tomato", "Tomato___healthy", True)
    assert len(recs_healthy) >= 3, "Expected at least 3 healthy recommendations"
    print(f"  PASS: Healthy care recommendations returned ({len(recs_healthy)} items)")

    recs_blight = recommendation_service.get_recommendations("Tomato", "Tomato___Early_blight", False)
    assert len(recs_blight) >= 3, "Expected at least 3 blight recommendations"
    assert any("copper" in r["description"].lower() or "foliage" in r["description"].lower() for r in recs_blight)
    print(f"  PASS: Tomato Early Blight recommendations returned ({len(recs_blight)} items, treatment & sanitation)")

    print("\n" + "=" * 70)
    print("                ALL 18 VERIFICATION TESTS PASSED!                ")
    print("=" * 70)

if __name__ == "__main__":
    run_suite()
