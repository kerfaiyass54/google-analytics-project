# Prediction Events Dashboard Service

A separate FastAPI worker that consumes prediction and evaluation events from Kafka and indexes them in Elasticsearch for operational dashboards.

## Event flow

- Prediction API publishes prediction-events after a prediction is committed to PostgreSQL.
- Prediction API publishes evaluation-events after the evaluation and model registry entry are saved.
- This service consumes both topics using the prediction-dashboard consumer group.
- Events are indexed in Elasticsearch index prediction_dashboard_events.
- The service exposes aggregated counts and a recent event feed for the Angular admin dashboard.

## Run with the existing Docker stack

From the repository root, start the existing infrastructure first, then run:

    docker compose -f docker-compose.yml -f google-analytics-prediction-events/compose.yml up -d --build prediction-events

The service listens on http://localhost:8020. Check /health and /docs.

## Run locally

    cd google-analytics-prediction-events
    py -3.12 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    $env:KAFKA_BOOTSTRAP_SERVERS="localhost:29099"
    $env:ELASTICSEARCH_URL="http://localhost:9290"
    uvicorn app.main:app --reload --port 8020

Ensure the Kafka external listener is exposed on port 29099 in the root compose environment. The Elasticsearch index is created automatically on service startup.

## Read endpoints

- GET /health
- GET /api/dashboard/summary
- GET /api/dashboard/recent?limit=20

The dashboard event index is a derived event store. PostgreSQL remains the source of truth for prediction records and model registry data; original evaluation documents remain in prediction_model_evaluations.
