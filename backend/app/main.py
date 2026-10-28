"""
PlantSathi AI - FastAPI Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging_config import setup_logging

logger = logging.getLogger("plantsathi")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────────────────
    setup_logging(settings.LOG_LEVEL, settings.LOG_FILE)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

        # Create required directories
    for directory in [
        settings.UPLOAD_DIR,
        settings.HF_HOME,
        settings.TRANSFORMERS_CACHE,
        "logs",
        "/app/data",
    ]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory: {directory}")

    # Set HuggingFace cache env vars before any model imports
    os.environ["HF_HOME"] = str(Path(settings.HF_HOME).resolve())
    os.environ["TRANSFORMERS_CACHE"] = str(Path(settings.TRANSFORMERS_CACHE).resolve())

    # Initialize database
    from app.models.database import init_db
    await init_db()
    logger.info("Database initialized")

    # Pre-warm models in background (non-blocking)
    # Models load lazily on first request; this just logs availability
    try:
        from app.ml.model_loader import get_model_loader
        loader = get_model_loader()
        status = loader.get_status()
        logger.info(f"Model registry initialized. Disease model: {status.get('disease', {}).get('status', 'not_loaded')}")
    except Exception as e:
        logger.warning(f"Model loader init warning (non-fatal): {e}")

    logger.info(f"PlantSathi AI ready. CORS origins: {settings.cors_origins}")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("Shutting down PlantSathi AI")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered plant identification and disease diagnosis platform",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # ── Global error handler ─────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again.",
                "detail": str(exc) if settings.DEBUG else None,
            },
        )

    # ── Routers ──────────────────────────────────────────────────────────────
    from app.api.routes.health import router as health_router
    from app.api.routes.identification import router as identify_router
    from app.api.routes.diagnosis import router as diagnosis_router
    from app.api.routes.analyze import router as analyze_router
    from app.api.routes.scans import router as scans_router
    from app.api.routes.chat import router as chat_router
    from app.api.routes.plants import router as plants_router

    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(identify_router, prefix="/api", tags=["Plant Identification"])
    app.include_router(diagnosis_router, prefix="/api", tags=["Disease Diagnosis"])
    app.include_router(analyze_router, prefix="/api", tags=["Combined Analysis"])
    app.include_router(scans_router, prefix="/api", tags=["Scan History"])
    app.include_router(chat_router, prefix="/api", tags=["AI Doctor"])
    app.include_router(plants_router, prefix="/api", tags=["My Plants"])

    # ── Root redirect ────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
            "health": "/api/health",
        }

    return app


app = create_app()
