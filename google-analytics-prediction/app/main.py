from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
import psycopg2
from psycopg2 import sql
from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.elastic import ensure_evaluation_index, client
from app.api import include_api_routers

settings = get_settings()

def ensure_database_exists() -> None:
    connection = psycopg2.connect(host=settings.postgres_host, port=settings.postgres_port,
        dbname="postgres", user=settings.postgres_user, password=settings.postgres_password)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.postgres_db,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.postgres_db)))
    finally:
        connection.close()

def ensure_prediction_schema() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE predict_rating ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"))
        connection.execute(text("ALTER TABLE predict_installs ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_predict_rating_user_id ON predict_rating (user_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_predict_installs_user_id ON predict_installs (user_id)"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database_exists()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    if not client.ping():
        raise RuntimeError("Elasticsearch is unavailable.")
    ensure_prediction_schema()
    ensure_evaluation_index()
    settings.model_artifact_dir.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title=settings.app_name, version=settings.app_version,
    description="Google Play rating regression and install-bucket classification service.", lifespan=lifespan)
include_api_routers(app)

@app.get("/health", tags=["System"])
def health():
    return {"status": "UP"}

@app.get("/", tags=["System"])
def root():
    return {"name": settings.app_name, "version": settings.app_version, "status": "UP"}
