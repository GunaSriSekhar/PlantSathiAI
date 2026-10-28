"""
PlantSathi AI - Image Processing Service
Handles secure image upload validation, loading, and preprocessing.
"""
import io
import logging
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image, ExifTags, UnidentifiedImageError

logger = logging.getLogger("plantsathi.image_processing")

# PIL decompression bomb protection
Image.MAX_IMAGE_PIXELS = 178_956_970  # ~170 megapixels


class ImageValidationError(Exception):
    """Raised when an uploaded image fails validation."""

    def __init__(self, message: str, code: str = "invalid_image"):
        self.message = message
        self.code = code
        super().__init__(message)


class ImageValidator:
    """
    Validates and securely loads uploaded images.

    Security measures:
    - Detects actual image format via PIL (ignores extension/Content-Type)
    - PIL.MAX_IMAGE_PIXELS enforced (decompression bomb protection)
    - Rejects files that cannot be decoded as images
    - Rejects empty files
    - Safe filename generation (UUID-based, no path traversal)
    """

    SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_DIMENSION = 8192  # pixels

    async def validate_and_load(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        max_size_bytes: int = 10 * 1024 * 1024,
    ) -> Image.Image:
        """
        Validate file bytes and return a clean RGB PIL Image.

        Args:
            file_bytes: Raw bytes from upload
            filename: Original filename (for logging only)
            content_type: Declared MIME type (NOT trusted for format detection)
            max_size_bytes: Maximum allowed file size in bytes

        Returns:
            PIL Image in RGB mode, EXIF-corrected

        Raises:
            ImageValidationError: If validation fails
        """
        # 1. Check for empty file
        if not file_bytes:
            raise ImageValidationError("Uploaded file is empty.", code="empty_file")

        # 2. Check file size
        size_mb = len(file_bytes) / (1024 * 1024)
        if len(file_bytes) > max_size_bytes:
            raise ImageValidationError(
                f"File too large ({size_mb:.1f} MB). Maximum allowed: {max_size_bytes // (1024 * 1024)} MB.",
                code="file_too_large",
            )

        # 3. Try to open with PIL (actual format detection, not trusting metadata)
        try:
            buf = io.BytesIO(file_bytes)
            img = Image.open(buf)
            img.verify()  # Verify image integrity
            # Reopen after verify (verify() consumes the stream)
            buf.seek(0)
            img = Image.open(buf)
        except UnidentifiedImageError:
            raise ImageValidationError(
                "The uploaded file is not a recognized image format. "
                "Please upload a JPEG, PNG, or WebP image.",
                code="not_an_image",
            )
        except Exception as e:
            raise ImageValidationError(
                f"Could not open the image file: {e}",
                code="corrupt_image",
            )

        # 4. Check format
        detected_format = img.format or ""
        if detected_format.upper() not in self.SUPPORTED_FORMATS:
            raise ImageValidationError(
                f"Unsupported image format: {detected_format}. "
                f"Supported formats: JPEG, PNG, WebP.",
                code="unsupported_format",
            )

        # 5. Check dimensions
        width, height = img.size
        if width < 32 or height < 32:
            raise ImageValidationError(
                f"Image is too small ({width}×{height}px). "
                "Please upload a larger, clearer photograph.",
                code="image_too_small",
            )

        if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
            logger.info(f"Image {width}×{height} exceeds {self.MAX_DIMENSION}px — will resize")

        # 6. Apply EXIF rotation correction
        img = self._fix_exif_rotation(img)

        # 7. Convert to RGB (handles RGBA, L/grayscale, P/palette, etc.)
        if img.mode != "RGB":
            logger.debug(f"Converting image mode {img.mode} → RGB")
            if img.mode == "RGBA":
                # Composite onto white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            else:
                img = img.convert("RGB")

        # 8. Resize oversized images (preserving aspect ratio)
        if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
            img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.LANCZOS)
            logger.debug(f"Resized image to {img.size}")

        logger.info(
            f"Image validated: {filename} | {detected_format} | {img.size} | {size_mb:.2f}MB"
        )
        return img

    def _fix_exif_rotation(self, img: Image.Image) -> Image.Image:
        """Correct image rotation based on EXIF orientation tag."""
        try:
            exif = img.getexif()
            if exif is None:
                return img

            orientation_key = next(
                (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
            )
            if orientation_key is None:
                return img

            orientation = exif.get(orientation_key)
            rotation_map = {
                3: 180,
                6: 270,
                8: 90,
            }
            if orientation in rotation_map:
                img = img.rotate(rotation_map[orientation], expand=True)
        except Exception as e:
            logger.debug(f"EXIF rotation check skipped: {e}")
        return img

    def save_upload(self, image: Image.Image, upload_dir: Path) -> str:
        """
        Save a validated image to disk with a UUID filename.

        Args:
            image: PIL Image to save
            upload_dir: Target directory (must exist)

        Returns:
            Unique filename (not full path — prevents path exposure)
        """
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        save_path = upload_dir / filename
        image.save(save_path, format="JPEG", quality=90, optimize=True)
        logger.info(f"Image saved: {filename}")
        return filename
