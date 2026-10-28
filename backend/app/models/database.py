"""
PlantSathi AI Backend - Async Database Setup
SQLAlchemy async engine and session management using aiosqlite.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


# ---------------------------------------------------------------------------
# Engine & session factory (module-level singletons, created on first import)
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine() -> AsyncEngine:
    """Return the module-level async engine, creating it on first call."""
    global _engine
    if _engine is None:
        connect_args: dict[str, Any] = {}
        database_url = settings.DATABASE_URL

        # SQLite-specific: enable WAL mode and foreign-key support
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        _engine = create_async_engine(
            database_url,
            connect_args=connect_args,
            echo=settings.DEBUG,
            future=True,
            # Pool tuning - aiosqlite is single-threaded so keep small
            pool_pre_ping=True,
        )
        logger.info("Async database engine created: %s", database_url)
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return (or create) the module-level async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        logger.debug("Async session factory configured.")
    return _async_session_factory


# Public aliases used by the rest of the application
def get_engine() -> AsyncEngine:
    """Return the shared async database engine."""
    return _get_engine()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared async session factory."""
    return _get_session_factory()


# ---------------------------------------------------------------------------
# Database lifecycle helpers
# ---------------------------------------------------------------------------


async def init_db() -> None:
    """
    Create all tables defined in the ORM models.

    Should be called once at application startup (e.g. in the lifespan event).
    Safe to call multiple times - SQLAlchemy uses ``CREATE TABLE IF NOT EXISTS``.
    """
    # Import entities here to ensure all models are registered on Base.metadata
    # before we issue CREATE TABLE statements.
    import app.models.entities  # noqa: F401  # registers models

    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised successfully.")


async def close_db() -> None:
    """Dispose the engine connection pool.  Call during application shutdown."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine disposed.")


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a transactional ``AsyncSession``.

    Usage::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...

    The session is automatically committed on success and rolled back on any
    unhandled exception, then closed in all cases.
    """
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
