from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, HTTPException, Query

from app.config.settings import Settings
from app.consumer import PredictionEventConsumer
from app.database.prediction_repository import PredictionRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.security import require_admin
from app.services.dashboard_service import DashboardService

settings = Settings()
elasticsearch = Elasticsearch(settings.elasticsearch_url)
prediction_repository = PredictionRepository(settings)
evaluation_repository = EvaluationRepository(elasticsearch, settings.evaluations_index)
dashboard = DashboardService(
    prediction_repository,
    evaluation_repository,
    elasticsearch,
    settings.events_index,
)
consumer = PredictionEventConsumer(settings, elasticsearch)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer.start()
    yield
    consumer.stop()
    elasticsearch.close()


app = FastAPI(
    title="Google Analytics Prediction Events",
    description="Admin dashboard read model for prediction history, model evaluations and Kafka events.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "events_index": settings.events_index,
        "evaluations_index": settings.evaluations_index,
        "consumer_running": bool(consumer.thread and consumer.thread.is_alive()),
    }


@app.get("/api/dashboard/summary")
def summary(claims: dict = Depends(require_admin)):
    try:
        return dashboard.summary()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dashboard data sources are unavailable.") from exc


@app.get("/api/dashboard/recent")
def recent(limit: int = Query(default=20, ge=1, le=100), claims: dict = Depends(require_admin)):
    try:
        return dashboard.recent_events(limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dashboard event feed is unavailable.") from exc


@app.get("/api/dashboard/predictions")
def predictions(
    task: str = Query(default="all", pattern="^(all|regression|classification)$"),
    limit: int = Query(default=50, ge=1, le=100),
    claims: dict = Depends(require_admin),
):
    try:
        return prediction_repository.recent(limit=limit, task=task)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Prediction database is unavailable.") from exc


@app.get("/api/dashboard/evaluations")
def evaluations(
    task: str = Query(default="all", pattern="^(all|regression|classification)$"),
    limit: int = Query(default=50, ge=1, le=100),
    claims: dict = Depends(require_admin),
):
    try:
        return evaluation_repository.recent(limit=limit, task=task)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Evaluation index is unavailable.") from exc
