"""
Tests for image validation and processing service.
"""
import io
import pytest
from PIL import Image

from app.services.image_processing import ImageValidator, ImageValidationError


@pytest.mark.asyncio
async def test_valid_jpeg_accepted(sample_jpeg_bytes):
    validator = ImageValidator()
    img = await validator.validate_and_load(sample_jpeg_bytes, "test.jpg", "image/jpeg")
    assert img is not None
    assert img.mode == "RGB"


@pytest.mark.asyncio
async def test_valid_png_accepted(sample_png_bytes):
    validator = ImageValidator()
    img = await validator.validate_and_load(sample_png_bytes, "test.png", "image/png")
    assert img is not None
    assert img.mode == "RGB"


@pytest.mark.asyncio
async def test_invalid_file_rejected(invalid_file_bytes):
    validator = ImageValidator()
    with pytest.raises(ImageValidationError):
        await validator.validate_and_load(invalid_file_bytes, "not_image.txt", "text/plain")


@pytest.mark.asyncio
async def test_empty_bytes_rejected():
    validator = ImageValidator()
    with pytest.raises(ImageValidationError):
        await validator.validate_and_load(b"", "empty.jpg", "image/jpeg")


def test_rgba_image_converted_to_rgb():
    """RGBA images are converted cleanly to RGB."""
    img = Image.new("RGBA", (100, 100), color=(34, 85, 34, 128))
    converted = img.convert("RGB")
    assert converted.mode == "RGB"


def test_grayscale_image_converted_to_rgb():
    """Grayscale images are converted cleanly to RGB."""
    img = Image.new("L", (100, 100), color=128)
    converted = img.convert("RGB")
    assert converted.mode == "RGB"
