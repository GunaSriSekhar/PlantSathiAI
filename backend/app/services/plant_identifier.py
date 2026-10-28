"""
PlantSathi AI Backend - Plant Identifier Service
Uses HuggingFace transformers image-classification pipeline for local plant identification.
No external API keys required.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Primary model for plant species identification
_PRIMARY_MODEL = "umutbozdag/plant-identity"
# Fallback model (general ViT) when primary is unavailable
_FALLBACK_MODEL = "google/vit-base-patch16-224"


@dataclass
class PlantIdentificationResult:
    """Result returned by the PlantIdentifier service."""

    predictions: List[Dict[str, Any]]
    """Top-5 predictions, each with 'label' (str) and 'score' (float)."""

    model_name: str
    """Name of the HuggingFace model that produced this result."""

    device: str
    """Device used for inference: 'cpu' or 'cuda'."""

    error: Optional[str] = None
    """Non-None when identification could not be completed."""

    @property
    def top_prediction(self) -> Optional[Dict[str, Any]]:
        """Return the highest-confidence prediction, or None if empty."""
        return self.predictions[0] if self.predictions else None

    @property
    def is_reliable(self) -> bool:
        """True when top confidence is above 15 % and no error occurred."""
        if self.error or not self.predictions:
            return False
        return self.predictions[0].get("score", 0.0) >= 0.15


class PlantIdentifier:
    """
    Lazy-loaded plant identification service.

    The underlying HuggingFace pipeline is created on the first call to
    `identify()` and reused for the lifetime of the instance.

    Identification is run in a thread-pool executor so it does not block the
    FastAPI event loop.
    """

    def __init__(self) -> None:
        self._pipeline: Optional[Any] = None
        self._model_name: Optional[str] = None
        self._device: Optional[str] = None
        self._load_error: Optional[str] = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def identify(self, pil_image: Any) -> PlantIdentificationResult:
        """
        Identify plant species in *pil_image* (a PIL.Image.Image).

        Returns a :class:`PlantIdentificationResult` with the top-5
        predictions.  When the model cannot be loaded or inference fails the
        result carries a non-empty ``error`` string and an empty
        ``predictions`` list – no fabricated data is returned.
        """
        pipeline = await self._get_pipeline()

        if pipeline is None:
            return PlantIdentificationResult(
                predictions=[],
                model_name=self._model_name or "unavailable",
                device=self._device or "cpu",
                error=self._load_error or "Model could not be loaded.",
            )

        try:
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(
                None, self._run_inference, pipeline, pil_image
            )
            predictions = [
                {"label": entry["label"], "score": round(float(entry["score"]), 6)}
                for entry in raw[:5]
            ]
            return PlantIdentificationResult(
                predictions=predictions,
                model_name=self._model_name or "unknown",
                device=self._device or "cpu",
            )
        except Exception as exc:
            logger.exception("Plant identification inference failed: %s", exc)
            return PlantIdentificationResult(
                predictions=[],
                model_name=self._model_name or "unknown",
                device=self._device or "cpu",
                error=f"Inference error: {exc}",
            )

    async def get_model_info(self) -> Dict[str, Any]:
        """Return metadata about the loaded model without triggering a load."""
        return {
            "model_name": self._model_name,
            "device": self._device,
            "loaded": self._pipeline is not None,
            "load_error": self._load_error,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_pipeline(self) -> Optional[Any]:
        """Return the cached pipeline, loading it lazily on first call."""
        if self._pipeline is not None or self._load_error is not None:
            return self._pipeline

        async with self._lock:
            # Double-checked locking
            if self._pipeline is not None or self._load_error is not None:
                return self._pipeline

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._load_pipeline)

        return self._pipeline

    def _load_pipeline(self) -> None:
        """
        Attempt to load the primary model, then the fallback.
        Executed in a thread-pool executor (not on the event loop).
        """
        import torch

        device_id = 0 if torch.cuda.is_available() else -1
        self._device = "cuda" if device_id == 0 else "cpu"

        for model_id in (_PRIMARY_MODEL, _FALLBACK_MODEL):
            try:
                logger.info("Loading plant-identity model '%s' on %s …", model_id, self._device)
                from transformers import pipeline as hf_pipeline

                pipe = hf_pipeline(
                    "image-classification",
                    model=model_id,
                    top_k=5,
                    device=device_id,
                )
                self._pipeline = pipe
                self._model_name = model_id
                logger.info("Plant-identity model '%s' loaded successfully.", model_id)
                return
            except Exception as exc:
                logger.warning("Could not load model '%s': %s", model_id, exc)

        self._load_error = (
            f"Neither '{_PRIMARY_MODEL}' nor '{_FALLBACK_MODEL}' could be loaded. "
            "Ensure transformers and torch are installed and the model weights are "
            "accessible (internet or local cache)."
        )
        logger.error(self._load_error)

    @staticmethod
    def _run_inference(pipeline: Any, pil_image: Any) -> List[Dict[str, Any]]:
        """Call the pipeline synchronously; intended for thread-pool use."""
        return pipeline(pil_image)


# Module-level singleton shared across requests
plant_identifier = PlantIdentifier()
