"""
PlantSathi AI Backend - Model Registry
Defines the canonical model identifiers, PlantVillage class labels, and
lightweight metadata structures used throughout the ML layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# ---------------------------------------------------------------------------
# Model identifiers
# ---------------------------------------------------------------------------

DISEASE_MODEL_ID: str = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
"""HuggingFace model hub ID for the MobileNetV2 plant-disease classifier."""

PLANT_ID_MODEL_ID: str = "umutbozdag/plant-identity"
"""HuggingFace model hub ID for the ViT-based plant-identification classifier."""

# ---------------------------------------------------------------------------
# PlantVillage class labels (38 classes, indices 0-37)
# ---------------------------------------------------------------------------

PLANT_VILLAGE_LABELS: list[str] = [
    "Apple___Apple_scab",                                          # 0
    "Apple___Black_rot",                                           # 1
    "Apple___Cedar_apple_rust",                                    # 2
    "Apple___healthy",                                             # 3
    "Blueberry___healthy",                                         # 4
    "Cherry_(including_sour)___Powdery_mildew",                    # 5
    "Cherry_(including_sour)___healthy",                           # 6
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",          # 7
    "Corn_(maize)___Common_rust_",                                 # 8
    "Corn_(maize)___Northern_Leaf_Blight",                         # 9
    "Corn_(maize)___healthy",                                      # 10
    "Grape___Black_rot",                                           # 11
    "Grape___Esca_(Black_Measles)",                                # 12
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",                  # 13
    "Grape___healthy",                                             # 14
    "Orange___Haunglongbing_(Citrus_greening)",                    # 15
    "Peach___Bacterial_spot",                                      # 16
    "Peach___healthy",                                             # 17
    "Pepper,_bell___Bacterial_spot",                               # 18
    "Pepper,_bell___healthy",                                      # 19
    "Potato___Early_blight",                                       # 20
    "Potato___Late_blight",                                        # 21
    "Potato___healthy",                                            # 22
    "Raspberry___healthy",                                         # 23
    "Soybean___healthy",                                           # 24
    "Squash___Powdery_mildew",                                     # 25
    "Strawberry___Leaf_scorch",                                    # 26
    "Strawberry___healthy",                                        # 27
    "Tomato___Bacterial_spot",                                     # 28
    "Tomato___Early_blight",                                       # 29
    "Tomato___Late_blight",                                        # 30
    "Tomato___Leaf_Mold",                                          # 31
    "Tomato___Septoria_leaf_spot",                                 # 32
    "Tomato___Spider_mites Two-spotted_spider_mite",               # 33
    "Tomato___Target_Spot",                                        # 34
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",                      # 35
    "Tomato___Tomato_mosaic_virus",                                # 36
    "Tomato___healthy",                                            # 37
]

# Reverse-lookup: label → class index
LABEL_TO_INDEX: dict[str, int] = {label: idx for idx, label in enumerate(PLANT_VILLAGE_LABELS)}

# Set of plant genera/species present in PlantVillage (used for 'supported' check)
SUPPORTED_PLANTS: frozenset[str] = frozenset(
    label.split("___")[0].lower() for label in PLANT_VILLAGE_LABELS
)

SUPPORTED_CROPS: list[str] = [
    "apple", "blueberry", "cherry", "corn", "maize", "grape", "orange",
    "peach", "pepper", "potato", "raspberry", "soybean", "squash",
    "strawberry", "tomato"
]

"""
Lower-cased plant names that the disease model was trained on.

Examples: ``'apple'``, ``'tomato'``, ``'corn_(maize)'``, ``'pepper,_bell'``.
"""

# ---------------------------------------------------------------------------
# Model status enum
# ---------------------------------------------------------------------------


class ModelStatus(str, Enum):
    """Lifecycle states for a loaded model."""

    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"  # dependency missing at import time


# ---------------------------------------------------------------------------
# Model metadata dataclass
# ---------------------------------------------------------------------------


@dataclass
class ModelMetadata:
    """Tracks runtime metadata for a single loaded model."""

    name: str
    """Human-readable model name (e.g. 'Disease Detector')."""

    model_id: str
    """HuggingFace hub identifier."""

    task: str
    """Pipeline task string (e.g. 'image-classification')."""

    device: str = "cpu"
    """Device the model is loaded on ('cpu' or 'cuda')."""

    status: ModelStatus = ModelStatus.NOT_LOADED
    """Current load status of this model."""

    loaded_at: Optional[datetime] = None
    """UTC timestamp when the model finished loading."""

    error_message: Optional[str] = None
    """Error description if ``status == ModelStatus.FAILED``."""

    extra: dict = field(default_factory=dict)
    """Arbitrary additional metadata (e.g. number of parameters, revision)."""

    def to_dict(self) -> dict:
        """Serialise metadata to a plain dictionary (safe for JSON encoding)."""
        return {
            "name": self.name,
            "model_id": self.model_id,
            "task": self.task,
            "device": self.device,
            "status": self.status.value,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "error_message": self.error_message,
            **self.extra,
        }


# ---------------------------------------------------------------------------
# Registry of all models used by PlantSathi
# ---------------------------------------------------------------------------

MODEL_REGISTRY: dict[str, ModelMetadata] = {
    "disease": ModelMetadata(
        name="Plant Disease Detector",
        model_id=DISEASE_MODEL_ID,
        task="image-classification",
        device="cpu",
        status=ModelStatus.NOT_LOADED,
    ),
    "plant_id": ModelMetadata(
        name="Plant Identifier",
        model_id=PLANT_ID_MODEL_ID,
        task="image-classification",
        device="cpu",
        status=ModelStatus.NOT_LOADED,
    ),
}
"""
Global mutable registry of model metadata.

``ModelLoader`` updates entries in this dict as models are loaded or fail.
The registry is the single source of truth for model status reporting via
the health/status API endpoints.
"""
