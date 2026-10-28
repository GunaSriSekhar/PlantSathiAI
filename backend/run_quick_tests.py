import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.confidence import ConfidenceEvaluator
from app.services.recommendations import recommendation_service
from app.services.ai_doctor import ai_doctor
from app.ml.model_registry import PLANT_VILLAGE_LABELS, SUPPORTED_CROPS

def test_confidence():
    evaluator = ConfidenceEvaluator()
    assert evaluator.assess_disease_confidence(0.85)['level'] == 'high'
    assert evaluator.assess_disease_confidence(0.55)['level'] == 'medium'
    assert evaluator.assess_disease_confidence(0.10)['level'] == 'insufficient'
    assert evaluator.is_healthy_class('Tomato___healthy') == True
    assert evaluator.is_healthy_class('Tomato___Early_blight') == False
    parsed = evaluator.parse_disease_label('Tomato___Early_blight')
    assert parsed['crop'] == 'Tomato'
    assert 'Early Blight' in parsed['disease']
    print("[OK] ConfidenceEvaluator unit tests passed.")

def test_recommendations():
    recs_healthy = recommendation_service.get_recommendations('Tomato', 'Tomato___healthy', True)
    assert len(recs_healthy) > 0

    recs_blight = recommendation_service.get_recommendations('Tomato', 'Tomato___Early_blight', False)
    assert len(recs_blight) > 0
    assert any('copper' in r['description'].lower() or 'foliage' in r['description'].lower() for r in recs_blight)
    print(f"[OK] RecommendationService unit tests passed ({len(recs_blight)} blight recommendations verified).")

def test_labels():
    assert len(PLANT_VILLAGE_LABELS) == 38
    assert "tomato" in SUPPORTED_CROPS
    assert "potato" in SUPPORTED_CROPS
    print(f"[OK] Model registry verified: {len(PLANT_VILLAGE_LABELS)} PlantVillage classes, {len(SUPPORTED_CROPS)} crops.")

async def test_doctor():
    resp = await ai_doctor.get_response("How do I water my tomato plant?")
    assert len(resp.message) > 50
    assert resp.is_llm is False
    assert len(resp.suggestions) > 0
    print("[OK] AI Plant Doctor unit tests passed (rule-based expert response validated).")

if __name__ == "__main__":
    import asyncio
    test_confidence()
    test_recommendations()
    test_labels()
    asyncio.run(test_doctor())
    print("\nALL BACKEND UNIT CHECKS PASSED SUCCESSFULLY!")
