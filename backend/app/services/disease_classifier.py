"""
PlantSathi AI Backend - Disease Classifier Service
MobileNetV2 image classifier trained on 38 PlantVillage classes.
Loads existing Hugging Face model weights without the legacy pipeline.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DISEASE_MODEL = (
    "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
)

_MODEL_CACHE = (
    "models--linkanjarad--mobilenet_v2_1.0_224-plant-disease-identification"
)

PLANT_VILLAGE_LABELS: List[str] = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

SUPPORTED_CROPS: List[str] = [
    "apple", "blueberry", "cherry", "corn", "maize",
    "grape", "orange", "peach", "pepper", "potato",
    "raspberry", "soybean", "squash", "strawberry", "tomato",
]


def is_crop_supported(plant_name: str) -> bool:
    if not plant_name:
        return False
    plant_lower = plant_name.lower()
    return any(crop in plant_lower for crop in SUPPORTED_CROPS)


def _parse_label(label: str) -> tuple[str, str, bool]:
    parts = label.split("___", 1)
    crop = (
        parts[0]
        .replace("_", " ")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )
    disease_raw = parts[1] if len(parts) > 1 else "unknown"
    is_healthy = disease_raw.lower().strip("_ ") == "healthy"
    disease_name = disease_raw.replace("_", " ").strip()
    return crop, disease_name, is_healthy


@dataclass
class DiseaseClassificationResult:
    label: str
    crop: str
    disease_name: str
    is_healthy: bool
    confidence: float
    model_name: str
    device: str
    supported: bool = True
    error: Optional[str] = None

    @property
    def status(self) -> str:
        if self.error:
            return "error"
        if not self.supported:
            return "unsupported"
        if self.is_healthy:
            return "healthy"
        if self.confidence < 0.20:
            return "uncertain"
        return "identified"


class DiseaseClassifier:
    """Lazy-loaded MobileNetV2 disease classifier."""

    def __init__(self) -> None:
        self._model: Optional[Any] = None
        self._torch: Optional[Any] = None
        self._device_obj: Optional[Any] = None
        self._model_name: Optional[str] = None
        self._device: Optional[str] = None
        self._load_error: Optional[str] = None
        self._lock = asyncio.Lock()

    def is_crop_supported(self, plant_name: str) -> bool:
        return is_crop_supported(plant_name)

    async def classify(
        self,
        pil_image: Any,
        plant_name: Optional[str] = None,
    ) -> DiseaseClassificationResult:
        supported = (
            is_crop_supported(plant_name)
            if plant_name is not None
            else True
        )

        model = await self._get_model()

        if model is None:
            return DiseaseClassificationResult(
                label="unknown",
                crop="unknown",
                disease_name="unknown",
                is_healthy=False,
                confidence=0.0,
                model_name=self._model_name or _DISEASE_MODEL,
                device=self._device or "cpu",
                supported=supported,
                error=self._load_error or "Model could not be loaded.",
            )

        try:
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(
                None, self._run_inference, pil_image
            )

            index = int(raw["index"])
            confidence = round(float(raw["confidence"]), 6)

            if not 0 <= index < len(PLANT_VILLAGE_LABELS):
                raise ValueError(f"Invalid model class index: {index}")

            label = PLANT_VILLAGE_LABELS[index]
            crop, disease_name, is_healthy = _parse_label(label)

            return DiseaseClassificationResult(
                label=label,
                crop=crop,
                disease_name=disease_name,
                is_healthy=is_healthy,
                confidence=confidence,
                model_name=self._model_name or _DISEASE_MODEL,
                device=self._device or "cpu",
                supported=supported,
            )
        except Exception as exc:
            logger.exception("Disease classification inference failed: %s", exc)
            return DiseaseClassificationResult(
                label="unknown",
                crop="unknown",
                disease_name="unknown",
                is_healthy=False,
                confidence=0.0,
                model_name=self._model_name or _DISEASE_MODEL,
                device=self._device or "cpu",
                supported=supported,
                error=f"Inference error: {exc}",
            )

    async def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self._model_name,
            "device": self._device,
            "loaded": self._model is not None,
            "load_error": self._load_error,
            "class_count": len(PLANT_VILLAGE_LABELS),
            "supported_crops": SUPPORTED_CROPS,
        }

    async def _get_model(self) -> Optional[Any]:
        if self._model is not None or self._load_error is not None:
            return self._model

        async with self._lock:
            if self._model is not None or self._load_error is not None:
                return self._model

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._load_model)

        return self._model

    def _load_model(self) -> None:
        try:
            import torch
            from transformers import AutoConfig, AutoModelForImageClassification
            from pathlib import Path

            model_root = (
                Path.home() / ".cache" / "huggingface" / "hub"
                / _MODEL_CACHE / "snapshots"
            )

            # Use the already-downloaded snapshot; do not require a download.
            config_paths = list(model_root.glob("*/config.json"))
            if not config_paths:
                raise FileNotFoundError(
                    f"Cached model config not found in {model_root}"
                )

            model_path = config_paths[0].parent
            self._device_obj = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            self._device = str(self._device_obj)

            logger.info("Loading disease model from %s", model_path)

            config = AutoConfig.from_pretrained(
                str(model_path), local_files_only=True
            )
            model = AutoModelForImageClassification.from_pretrained(
                str(model_path),
                config=config,
                local_files_only=True,
            )

            # Use the checkpoint's actual label mapping where available.
            if getattr(config, "id2label", None):
                labels = [
                    config.id2label.get(i, config.id2label.get(str(i)))
                    for i in range(config.num_labels)
                ]
                if all(isinstance(label, str) for label in labels):
                    PLANT_VILLAGE_LABELS[:] = labels

            if model.config.num_labels != len(PLANT_VILLAGE_LABELS):
                raise ValueError(
                    f"Checkpoint has {model.config.num_labels} classes, "
                    f"but {len(PLANT_VILLAGE_LABELS)} labels are configured."
                )

            model.to(self._device_obj)
            model.eval()

            self._torch = torch
            self._model = model
            self._model_name = _DISEASE_MODEL
            logger.info(
                "Disease model loaded successfully: %d classes on %s",
                model.config.num_labels,
                self._device,
            )

        except Exception as exc:
            self._device = self._device or "cpu"
            self._load_error = (
                f"Could not load disease model '{_DISEASE_MODEL}': {exc}"
            )
            logger.exception(self._load_error)

    def _run_inference(self, pil_image: Any) -> Dict[str, Any]:
        import torch
        from torchvision import transforms

        if self._model is None or self._device_obj is None:
            raise RuntimeError("Disease model is not loaded.")

        # Matches the checkpoint's preprocessor config:
        # resize shortest edge to 256, center crop 224, scale to [0, 1],
        # then normalize RGB channels with mean/std of 0.5.
        preprocess = transforms.Compose([
            transforms.Resize(256, interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.5, 0.5, 0.5],
                std=[0.5, 0.5, 0.5],
            ),
        ])

        image = pil_image.convert("RGB")
        inputs = preprocess(image).unsqueeze(0).to(self._device_obj)

        with torch.inference_mode():
            outputs = self._model(pixel_values=inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)[0]
            confidence, index = torch.max(probabilities, dim=0)

        return {
            "index": int(index.item()),
            "confidence": float(confidence.item()),
        }


# Module-level singleton
disease_classifier = DiseaseClassifier()
