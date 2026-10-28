"""
PlantSathi AI Backend - Singleton Model Loader
Thread-safe, lazy-loading manager for HuggingFace Transformers models.
Gracefully degrades when optional ML dependencies are unavailable.
"""
from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import get_settings
from app.ml.model_registry import (
    MODEL_REGISTRY,
    DISEASE_MODEL_ID,
    PLANT_ID_MODEL_ID,
    ModelMetadata,
    ModelStatus,
)

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Optional import guards
# ---------------------------------------------------------------------------

try:
    import torch  # noqa: F401

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    logger.warning("PyTorch not installed; disease model will use CPU-only fallback.")

try:
    from transformers import pipeline as hf_pipeline  # type: ignore[import-untyped]

    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False
    logger.warning(
        "HuggingFace Transformers not installed; models will be marked UNAVAILABLE."
    )


def _resolve_device() -> str:
    """Return ``'cuda'`` if a CUDA GPU is available, otherwise ``'cpu'``."""
    if _TORCH_AVAILABLE:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cpu"


# ---------------------------------------------------------------------------
# ModelLoader singleton
# ---------------------------------------------------------------------------


class ModelLoader:
    """
    Thread-safe singleton that lazily loads ML models on first use.

    Usage::

        loader = ModelLoader.get_instance()
        disease_pipeline = loader.get_disease_model()
        plant_pipeline   = loader.get_plant_id_model()
        status           = loader.get_status()

    Model loading is protected by a per-model ``threading.Lock`` so that
    concurrent requests during startup cannot trigger duplicate downloads.
    """

    _instance: Optional["ModelLoader"] = None
    _singleton_lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._disease_model: Any = None
        self._plant_id_model: Any = None
        self._disease_lock = threading.Lock()
        self._plant_id_lock = threading.Lock()
        self._device = _resolve_device()

        # Configure HuggingFace cache directory from settings
        os.environ.setdefault("HF_HOME", settings.HF_HOME)
        os.environ.setdefault("TRANSFORMERS_CACHE", settings.TRANSFORMERS_CACHE)

        logger.info(
            "ModelLoader initialised | device=%s | HF_HOME=%s",
            self._device,
            os.environ.get("HF_HOME"),
        )

    # ------------------------------------------------------------------
    # Singleton constructor
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        """
        Return the application-wide ``ModelLoader`` singleton.

        Thread-safe: uses a class-level lock to prevent duplicate
        instantiation under concurrent startup.
        """
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Disease model
    # ------------------------------------------------------------------

    def get_disease_model(self) -> Any:
        """
        Return the disease-detection pipeline, loading it on first call.

        Returns
        -------
        transformers.Pipeline | None
            A HuggingFace image-classification pipeline, or ``None`` if
            the model failed to load or dependencies are missing.
        """
        if self._disease_model is not None:
            return self._disease_model

        with self._disease_lock:
            # Double-checked locking
            if self._disease_model is not None:
                return self._disease_model

            meta = MODEL_REGISTRY["disease"]
            meta.device = self._device
            self._disease_model = self._load_transformers_pipeline(
                key="disease",
                model_id=DISEASE_MODEL_ID,
                task="image-classification",
                meta=meta,
            )
        return self._disease_model

    # ------------------------------------------------------------------
    # Plant ID model
    # ------------------------------------------------------------------

    def get_plant_id_model(self) -> Any:
        """
        Return the plant-identification pipeline, loading it on first call.

        Returns
        -------
        transformers.Pipeline | None
            A HuggingFace image-classification pipeline, or ``None`` if
            the model failed to load or dependencies are missing.
        """
        if self._plant_id_model is not None:
            return self._plant_id_model

        with self._plant_id_lock:
            if self._plant_id_model is not None:
                return self._plant_id_model

            meta = MODEL_REGISTRY["plant_id"]
            meta.device = self._device
            self._plant_id_model = self._load_transformers_pipeline(
                key="plant_id",
                model_id=PLANT_ID_MODEL_ID,
                task="image-classification",
                meta=meta,
            )
        return self._plant_id_model

    # ------------------------------------------------------------------
    # Internal loader
    # ------------------------------------------------------------------

    def _load_transformers_pipeline(
        self,
        key: str,
        model_id: str,
        task: str,
        meta: ModelMetadata,
    ) -> Any:
        """
        Load a HuggingFace transformers pipeline for *model_id*.

        Handles import errors, missing weights, and any runtime exception
        without crashing the application.  The ``MODEL_REGISTRY`` entry for
        *key* is updated to reflect the final load status.

        Parameters
        ----------
        key:
            Registry key, e.g. ``"disease"`` or ``"plant_id"``.
        model_id:
            HuggingFace hub model identifier.
        task:
            Transformers task string (e.g. ``"image-classification"``).
        meta:
            Mutable ``ModelMetadata`` instance to update in-place.

        Returns
        -------
        transformers.Pipeline | None
            Loaded pipeline or ``None`` on failure.
        """
        if not _TRANSFORMERS_AVAILABLE:
            meta.status = ModelStatus.UNAVAILABLE
            meta.error_message = "transformers library not installed"
            logger.error(
                "Cannot load model '%s': transformers not available.", model_id
            )
            return None

        meta.status = ModelStatus.LOADING
        logger.info("Loading model '%s' [%s] on device=%s …", model_id, task, self._device)

        try:
            # Resolve numeric device index for PyTorch (GPU=0, CPU=-1)
            device_arg: int | str
            if _TORCH_AVAILABLE:
                import torch

                device_arg = 0 if (self._device == "cuda" and torch.cuda.is_available()) else -1
            else:
                device_arg = -1  # CPU

            loaded_pipeline = hf_pipeline(
                task=task,
                model=model_id,
                device=device_arg,
                # Return all scores so callers can inspect the full distribution
                top_k=None,
            )

            meta.status = ModelStatus.LOADED
            meta.loaded_at = datetime.now(timezone.utc)
            meta.error_message = None
            logger.info(
                "Model '%s' loaded successfully (device=%s).", model_id, self._device
            )
            return loaded_pipeline

        except OSError as exc:
            # Typically: model weights not found / network unreachable
            meta.status = ModelStatus.FAILED
            meta.error_message = f"OSError loading model: {exc}"
            logger.error("OSError loading model '%s': %s", model_id, exc)

        except ValueError as exc:
            meta.status = ModelStatus.FAILED
            meta.error_message = f"ValueError loading model: {exc}"
            logger.error("ValueError loading model '%s': %s", model_id, exc)

        except Exception as exc:  # noqa: BLE001
            meta.status = ModelStatus.FAILED
            meta.error_message = f"Unexpected error: {exc}"
            logger.exception("Unexpected error loading model '%s'.", model_id)

        return None

    # ------------------------------------------------------------------
    # Status reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """
        Return a JSON-serialisable status dict for all registered models.
        """
        data: dict[str, Any] = {key: meta.to_dict() for key, meta in MODEL_REGISTRY.items()}
        data["all"] = [meta.to_dict() for meta in MODEL_REGISTRY.values()]
        return data

    def is_disease_model_ready(self) -> bool:
        """Return ``True`` if the disease pipeline is loaded and ready."""
        return MODEL_REGISTRY["disease"].status == ModelStatus.LOADED

    def is_plant_id_model_ready(self) -> bool:
        """Return ``True`` if the plant-ID pipeline is loaded and ready."""
        return MODEL_REGISTRY["plant_id"].status == ModelStatus.LOADED

    def preload_all(self) -> None:
        """
        Eagerly load both models.

        Intended to be called at application startup (e.g. from the FastAPI
        ``lifespan`` event) so that the first user request does not incur the
        model-loading latency.
        """
        logger.info("Pre-loading all ML models …")
        self.get_disease_model()
        self.get_plant_id_model()
        logger.info(
            "Model pre-load complete. Status: %s",
            {k: v["status"] for k, v in self.get_status().items()},
        )

    # ------------------------------------------------------------------
    # Allow direct instantiation for testing, but keep singleton path
    # ------------------------------------------------------------------

    def reset_for_testing(self) -> None:
        """
        Reset internal model references.

        **For unit tests only.** Clears cached models so they can be
        re-loaded (or mocked) in the next call.
        """
        with self._disease_lock:
            self._disease_model = None
        with self._plant_id_lock:
            self._plant_id_model = None
        for meta in MODEL_REGISTRY.values():
            meta.status = ModelStatus.NOT_LOADED
            meta.loaded_at = None
            meta.error_message = None
        logger.warning("ModelLoader state reset (testing only).")


def get_model_loader() -> ModelLoader:
    """Return the global ModelLoader singleton."""
    return ModelLoader.get_instance()

