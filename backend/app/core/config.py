"""
PlantSathi AI Backend - Application Configuration
Uses pydantic-settings for type-safe environment variable management.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "PlantSathi AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./plantsathi.db"

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    @property
    def allowed_mime_types(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    # Plant Identification Model
    PLANT_ID_MODEL: str = "umutbozdag/plant-identity"
    PLANT_ID_CONFIDENCE_THRESHOLD: float = 0.15

    # Disease Detection Model
    DISEASE_MODEL: str = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    DISEASE_CONFIDENCE_THRESHOLD: float = 0.40

    # PlantNet API (optional)
    PLANTNET_API_KEY: str = ""
    PLANTNET_API_URL: str = "https://my-api.plantnet.org/v2/identify/all"

    # Gemini API (optional)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # HuggingFace cache
    HF_HOME: str = "./model_cache"
    TRANSFORMERS_CACHE: str = "./model_cache/transformers"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/plantsathi.log"

    @property
    def has_plantnet_key(self) -> bool:
        return bool(self.PLANTNET_API_KEY and self.PLANTNET_API_KEY.strip())

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())

    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
