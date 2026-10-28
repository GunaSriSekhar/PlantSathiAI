"""
PlantSathi AI - Confidence Evaluator Service
Assesses model prediction scores, parses disease labels, and provides uncertainty metrics.
"""
from typing import Dict, Any, Optional
import re

class ConfidenceEvaluator:
    """
    Evaluates confidence scores for plant identification and disease diagnosis.
    Prevents false certainty and handles out-of-distribution or uncertain cases.
    """

    def assess_plant_confidence(self, score: Optional[float], threshold: float = 0.15) -> Dict[str, Any]:
        """
        Assess confidence level for plant identification.
        """
        if score is None:
            return {
                "level": "unknown",
                "reliable": False,
                "warning": "No confidence score available from model."
            }

        if score >= 0.70:
            return {
                "level": "high",
                "reliable": True,
                "warning": None
            }
        elif score >= 0.40:
            return {
                "level": "medium",
                "reliable": True,
                "warning": "Moderate confidence. Visual confirmation recommended."
            }
        elif score >= threshold:
            return {
                "level": "low",
                "reliable": False,
                "warning": "Low confidence prediction. Multiple species may appear similar."
            }
        else:
            return {
                "level": "insufficient",
                "reliable": False,
                "warning": "Confidence below threshold. The photograph may be blurry, dark, or not contain a recognized plant."
            }

    def assess_disease_confidence(self, score: Optional[float], threshold: float = 0.40) -> Dict[str, Any]:
        """
        Assess confidence level for plant disease diagnosis.
        """
        if score is None:
            return {
                "level": "unknown",
                "reliable": False,
                "warning": "No confidence score returned by disease model."
            }

        if score >= 0.80:
            return {
                "level": "high",
                "reliable": True,
                "warning": None
            }
        elif score >= threshold:
            return {
                "level": "medium",
                "reliable": True,
                "warning": "Diagnosis is plausible but symptom overlap exists with other conditions or environmental stress."
            }
        elif score >= 0.20:
            return {
                "level": "low",
                "reliable": False,
                "warning": "Low confidence diagnosis. Symptoms are ambiguous or affected leaf area is unclear."
            }
        else:
            return {
                "level": "insufficient",
                "reliable": False,
                "warning": "Insufficient evidence to determine plant condition. Please provide a close-up photo in clear natural lighting."
            }

    def is_healthy_class(self, label: str) -> bool:
        """
        Returns True if the label denotes a healthy plant.
        """
        if not label:
            return False
        return "healthy" in label.lower()

    def parse_disease_label(self, label: str) -> Dict[str, Any]:
        """
        Parses PlantVillage style labels: 'Tomato___Early_blight' or 'Corn_(maize)___Common_rust_'
        into structured dictionary: {crop: str, disease: str, healthy: bool}
        """
        if not label:
            return {"crop": "Unknown", "disease": "Unknown", "healthy": False}

        parts = label.split("___")
        if len(parts) == 2:
            crop_raw, disease_raw = parts[0], parts[1]
        else:
            crop_raw = parts[0]
            disease_raw = parts[0]

        # Clean crop
        crop = crop_raw.replace("_", " ").strip()
        crop = re.sub(r"\(.*?\)", "", crop).strip()
        crop = crop.title()

        # Clean disease
        is_healthy = "healthy" in disease_raw.lower()
        if is_healthy:
            disease_name = "Healthy Leaf (No Visible Pathogen)"
        else:
            disease_clean = disease_raw.replace("_", " ").strip()
            disease_clean = re.sub(r"\s+", " ", disease_clean)
            disease_name = disease_clean.title()

        return {
            "crop": crop,
            "disease": disease_name,
            "healthy": is_healthy
        }
