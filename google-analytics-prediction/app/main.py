from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.elastic import ensure_evaluation_index, client
from app.api import include_api_routers

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    if not client.ping():
        raise RuntimeError("Elasticsearch is unavailable.")
    Base.metadata.create_all(bind=engine)
    ensure_evaluation_index()
    settings.model_artifact_dir.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title=settings.app_name, version=settings.app_version,
              description="Google Play rating regression and install-bucket classification service.",
              lifespan=lifespan)
include_api_routers(app)

@app.get("/health", tags=["System"])
def health():
    return {"status": "UP"}

@app.get("/", tags=["System"])
def root():
    return {"name": settings.app_name, "version": settings.app_version, "status": "UP"}
