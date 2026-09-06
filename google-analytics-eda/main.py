"""
FastAPI application entry point.

Responsibilities:
    - Create the FastAPI application
    - Register API routers
    - Configure middleware
    - Configure application metadata
    - Perform startup infrastructure checks

Infrastructure:

    PostgreSQL
    Elasticsearch
    Keycloak

The application itself does not contain business logic.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    get_application_config,
    get_database_config,
    get_elasticsearch_config,
    get_keycloak_config,
)

from api.eda_export_controller import router as eda_export_router


# ============================================================
# LOGGER
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "google-play-analytics"
)


# ============================================================
# STARTUP / SHUTDOWN
# ============================================================

@asynccontextmanager
async def lifespan(
    application: FastAPI,
):
    """
    Application lifecycle.

    Startup:
        - Validate configuration
        - Create export directory
        - Verify Elasticsearch connectivity

    Shutdown:
        - Gracefully terminate the application
    """

    logger.info(
        "Starting Google Play Analytics API..."
    )

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    application_config = (
        get_application_config()
    )

    database_config = (
        get_database_config()
    )

    elasticsearch_config = (
        get_elasticsearch_config()
    )

    keycloak_config = (
        get_keycloak_config()
    )

    # --------------------------------------------------------
    # Log non-sensitive configuration
    # --------------------------------------------------------

    logger.info(
        "Application: %s",
        application_config.name,
    )

    logger.info(
        "Version: %s",
        application_config.version,
    )

    logger.info(
        "PostgreSQL: %s:%s/%s",
        database_config.host,
        database_config.port,
        database_config.database,
    )

    logger.info(
        "Elasticsearch: %s",
        elasticsearch_config.url,
    )

    logger.info(
        "Keycloak issuer: %s",
        keycloak_config.issuer,
    )

    # --------------------------------------------------------
    # Create export directory
    # --------------------------------------------------------

    from pathlib import Path

    export_directory = Path(
        "exports"
    )

    export_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "EDA export directory: %s",
        export_directory.resolve(),
    )

    # --------------------------------------------------------
    # Elasticsearch health check
    # --------------------------------------------------------

    try:

        from elastic.client import client

        if not client.ping():

            raise RuntimeError(
                "Elasticsearch is not reachable."
            )

        logger.info(
            "Elasticsearch connection: OK"
        )

    except Exception as exception:

        logger.error(
            "Elasticsearch connection failed: %s",
            exception,
        )

        raise

    # --------------------------------------------------------
    # Startup completed
    # --------------------------------------------------------

    logger.info(
        "Google Play Analytics API started successfully."
    )

    yield

    # ========================================================
    # SHUTDOWN
    # ========================================================

    logger.info(
        "Shutting down Google Play Analytics API..."
    )


# ============================================================
# APPLICATION
# ============================================================

application_config = (
    get_application_config()
)


app = FastAPI(
    title=application_config.name,
    version=application_config.version,
    description=(
        "Google Play Store analytics and "
        "exploratory data analysis API."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:4200",
    ],

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
    ],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    eda_export_router
)


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Application health check",
)
def health_check() -> dict[str, str]:
    """
    Basic application health endpoint.

    This endpoint only confirms that FastAPI itself
    is running.

    Infrastructure health is checked separately during
    startup.
    """

    return {
        "status": "UP",
        "service": application_config.name,
        "version": application_config.version,
    }


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["Application"],
    summary="Application information",
)
def root() -> dict[str, str]:
    """
    Return basic API information.
    """

    return {
        "name": application_config.name,
        "version": application_config.version,
        "docs": "/docs",
        "health": "/health",
    }