# Prediction Events Dashboard Service

A separate FastAPI worker consumes prediction and evaluation events from Kafka and indexes them in Elasticsearch for the admin dashboard.

## Event flow
- Prediction API publishes prediction-events after a prediction is committed to PostgreSQL.
- Prediction API publishes evaluation-events after evaluation and model registry records are saved.
- This service consumes both topics using consumer group prediction-dashboard.
- Events are indexed in prediction_dashboard_events.
- Admin-only endpoints expose aggregated counts and a recent event feed for Angular.

## Run with Docker Compose
From the repository root, start the infrastructure, then run:
    docker compose -f docker-compose.yml -f google-analytics-prediction-events/compose.yml up -d --build prediction-events

The service listens on http://localhost:8020. Check /health and /docs.

## Run locally
    cd google-analytics-prediction-events
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
    $env:ELASTICSEARCH_URL="http://localhost:9290"
    $env:KEYCLOAK_ISSUER="http://localhost:8280/realms/google-analytics"
    uvicorn app.main:app --reload --port 8020

Use the Kafka external listener advertised by your root compose configuration. The Docker service uses kafka:29092. The Elasticsearch event index is created automatically.

## Endpoints
- GET /health
- GET /api/dashboard/summary (ADMIN bearer token)
- GET /api/dashboard/recent?limit=20 (ADMIN bearer token)

PostgreSQL remains the source of truth for predictions and model registry. The original training evaluations remain in prediction_model_evaluations; this event index is a derived dashboard feed.
