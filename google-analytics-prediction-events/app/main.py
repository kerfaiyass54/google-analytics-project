import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from elasticsearch import Elasticsearch
from app.consumer import PredictionEventConsumer
from app.security import require_admin

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9290")
INDEX = os.getenv("EVENTS_INDEX", "prediction_dashboard_events")
KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
consumer = PredictionEventConsumer(KAFKA, ES_URL, INDEX)
es = Elasticsearch(ES_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer.start()
    yield
    consumer.stop()

app = FastAPI(title="Prediction Events Dashboard API", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "UP", "index": INDEX}

@app.get("/api/dashboard/summary")
def summary(claims: dict = Depends(require_admin)):
    try:
        result = es.search(index=INDEX, size=0, aggs={
            "predictions": {"filter": {"term": {"event_type": "prediction"}}},
            "evaluations": {"filter": {"term": {"event_type": "evaluation"}}},
            "apps": {"filter": {"term": {"event_type": "prediction"}}, "aggs": {"unique": {"cardinality": {"field": "app_name"}}}},
            "tasks": {"terms": {"field": "task"}}, "daily": {"date_histogram": {"field": "created_at", "calendar_interval": "day"}}
        })
        aggs = result["aggregations"]
        return {"predictions": aggs["predictions"]["doc_count"], "evaluations": aggs["evaluations"]["doc_count"],
            "unique_apps": aggs["apps"]["unique"]["value"], "tasks": aggs["tasks"]["buckets"], "daily": aggs["daily"]["buckets"]}
    except Exception as exc:
        raise HTTPException(503, "Dashboard event index is not ready.") from exc

@app.get("/api/dashboard/recent")
def recent(limit: int = 20, claims: dict = Depends(require_admin)):
    try:
        result = es.search(index=INDEX, size=max(1, min(limit, 100)), sort=[{"created_at": {"order": "desc"}}])
        return [hit["_source"] for hit in result["hits"]["hits"]]
    except Exception as exc:
        raise HTTPException(503, "Dashboard event index is not ready.") from exc
