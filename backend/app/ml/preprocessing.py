"""
PlantSathi AI Backend - Image Preprocessing Pipeline
Prepares PIL images for the disease detection and plant identification models.
Handles EXIF auto-rotation, colour-space conversions, and model-specific
normalisation so that callers receive ready-to-use NumPy arrays.
"""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
from PIL import Image, ExifTags, ImageOps

logger = logging.getLogger(__name__)

# ImageNet channel statistics used by most ViT / timm models
_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Orientation tag key in EXIF data
_EXIF_ORIENTATION_TAG: int | None = next(
    (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fix_exif_rotation(image: Image.Image) -> Image.Image:
    """
    Apply EXIF orientation metadata so the image is visually upright.

    Uses ``PIL.ImageOps.exif_transpose`` when available (Pillow ≥ 6.0),
    with a manual fallback for older versions.

    Parameters
    ----------
    image:
        Input PIL image (any mode).

    Returns
    -------
    Image.Image
        A copy of the image with correct orientation applied.
    """
    try:
        return ImageOps.exif_transpose(image)
    except Exception:
        # Manual fallback using raw EXIF data
        try:
            exif = image._getexif()  # type: ignore[attr-defined]
            if exif is not None and _EXIF_ORIENTATION_TAG is not None:
                orientation = exif.get(_EXIF_ORIENTATION_TAG)
                _ORIENTATION_TRANSFORMS = {
                    2: Image.FLIP_LEFT_RIGHT,
                    3: Image.ROTATE_180,
                    4: Image.FLIP_TOP_BOTTOM,
                    5: Image.TRANSPOSE,
                    6: Image.ROTATE_270,
                    7: Image.TRANSVERSE,
                    8: Image.ROTATE_90,
                }
                if orientation in _ORIENTATION_TRANSFORMS:
                    image = image.transpose(_ORIENTATION_TRANSFORMS[orientation])
        except Exception as exc:
            logger.debug("EXIF rotation correction skipped: %s", exc)
    return image


def _to_rgb(image: Image.Image) -> Image.Image:
    """
    Convert any PIL image to ``RGB`` mode.

    Handles:
    - ``RGBA`` / ``PA`` → composite onto white background then convert.
    - ``L`` (greyscale) / ``LA`` → RGB by replicating the single channel.
    - All other modes → direct ``convert("RGB")``.

    Parameters
    ----------
    image:
        Input PIL image.

    Returns
    -------
    Image.Image
        An RGB PIL image.
    """
    if image.mode in ("RGBA", "PA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "PA":
            image = image.convert("RGBA")
        background.paste(image, mask=image.split()[3])
        return background
    if image.mode in ("L", "LA"):
        return image.convert("RGB")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resize_and_pad(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """
    Resize an image to *target_size* while preserving aspect ratio,
    padding any empty space with black pixels.

    This avoids distorting the subject when the source aspect ratio differs
    from the model's expected square input.

    Parameters
    ----------
    image:
        Input PIL image (any mode; callers should convert to RGB first).
    target_size:
        ``(width, height)`` tuple for the output image.

    Returns
    -------
    Image.Image
        Resized-and-padded PIL image.
    """
    target_w, target_h = target_size
    orig_w, orig_h = image.size

    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new(image.mode if image.mode == "RGB" else "RGB", (target_w, target_h), (0, 0, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y))
    return canvas


def preprocess_for_disease_model(pil_image: Image.Image) -> np.ndarray:
    """
    Preprocess a PIL image for the MobileNetV2 plant-disease model.

    Pipeline
    --------
    1. Fix EXIF rotation.
    2. Convert to RGB (handles RGBA, greyscale, etc.).
    3. Resize to 224 × 224 using ``resize_and_pad``.
    4. Convert to float32 NumPy array.
    5. Normalise pixel values to ``[0, 1]`` by dividing by 255.
    6. Add batch dimension → shape ``(1, 224, 224, 3)``.

    Parameters
    ----------
    pil_image:
        Raw input PIL image as loaded from disk or an upload.

    Returns
    -------
    np.ndarray
        Float32 array of shape ``(1, 224, 224, 3)`` ready for the
        ``linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`` model.
    """
    image = _fix_exif_rotation(pil_image)
    image = _to_rgb(image)
    image = resize_and_pad(image, (224, 224))

    arr = np.array(image, dtype=np.float32) / 255.0  # → [0, 1]
    arr = np.expand_dims(arr, axis=0)                 # → (1, 224, 224, 3)

    logger.debug(
        "preprocess_for_disease_model: output shape=%s dtype=%s range=[%.3f, %.3f]",
        arr.shape, arr.dtype, arr.min(), arr.max(),
    )
    return arr


def preprocess_for_plant_id_model(pil_image: Image.Image) -> np.ndarray:
    """
    Preprocess a PIL image for the ViT-based plant-identification model.

    Pipeline
    --------
    1. Fix EXIF rotation.
    2. Convert to RGB.
    3. Resize to 224 × 224 using ``resize_and_pad``.
    4. Convert to float32 NumPy array.
    5. Normalise to ``[0, 1]`` (divide by 255).
    6. Apply ImageNet channel-wise z-score normalisation
       (subtract mean, divide by std).
    7. Transpose from ``(H, W, C)`` to ``(C, H, W)`` (PyTorch convention).
    8. Add batch dimension → shape ``(1, 3, 224, 224)``.

    Parameters
    ----------
    pil_image:
        Raw input PIL image.

    Returns
    -------
    np.ndarray
        Float32 array of shape ``(1, 3, 224, 224)`` ready for a
        HuggingFace ``transformers`` ViT pipeline / feature extractor.

    Notes
    -----
    When using a HuggingFace ``pipeline`` or ``AutoFeatureExtractor``, you
    may pass the *original* PIL image directly - the feature extractor handles
    normalisation internally.  Use this function only when calling the model
    manually without the pipeline wrapper.
    """
    image = _fix_exif_rotation(pil_image)
    image = _to_rgb(image)
    image = resize_and_pad(image, (224, 224))

    arr = np.array(image, dtype=np.float32) / 255.0          # → [0, 1]
    arr = (arr - _IMAGENET_MEAN) / _IMAGENET_STD             # ImageNet z-score
    arr = arr.transpose(2, 0, 1)                              # (H,W,C) → (C,H,W)
    arr = np.expand_dims(arr, axis=0)                         # → (1, 3, 224, 224)

    logger.debug(
        "preprocess_for_plant_id_model: output shape=%s dtype=%s",
        arr.shape, arr.dtype,
    )
    return arr
