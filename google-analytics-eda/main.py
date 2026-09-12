from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.eda_controller import router as eda_router
from api.eda_export_controller import router as eda_export_router

from config import get_settings

from elastic.client import check_connection
from elastic.indices import initialize_indexes


# ============================================================
# CONFIGURATION
# ============================================================

settings = get_settings()


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # --------------------------------------------------------
    # Validate Elasticsearch connection
    # --------------------------------------------------------

    if not check_connection():
        raise RuntimeError(
            "Unable to connect to Elasticsearch."
        )

    # --------------------------------------------------------
    # Create required directories
    # --------------------------------------------------------

    Path("exports").mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Initialize Elasticsearch indexes
    # --------------------------------------------------------

    initialize_indexes()

    yield


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.application.name,
    version=settings.application.version,
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
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
    ],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    eda_router,
)

app.include_router(
    eda_export_router,
)


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
def health() -> dict[str, str]:

    return {
        "status": "UP",
    }


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root() -> dict[str, str]:

    return {
        "name": settings.application.name,
        "version": settings.application.version,
        "status": "UP",
    }