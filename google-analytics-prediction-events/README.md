# Google Analytics Prediction Events

A dedicated FastAPI read service for admin prediction dashboards. It reads persisted predictions from PostgreSQL, training evaluations from Elasticsearch, and consumes Kafka events to maintain a searchable event feed.

## Responsibilities

- **Database repository:** read prediction history and model counts from PostgreSQL. PostgreSQL remains the source of truth for `predict_rating`, `predict_installs`, and `prediction_model_registry`.
- **Evaluation repository:** read the canonical training evaluation documents from Elasticsearch index `prediction_model_evaluations`.
- **Kafka consumer:** consume `prediction-events` and `evaluation-events`, then index idempotent event documents in `prediction_dashboard_events`.
- **Dashboard service:** aggregate source data and expose a unified admin read API.
- **Security:** validate Keycloak bearer tokens and require the configured ADMIN role.

Each module has one responsibility. Classes are kept in individual files under `app/database`, `app/repositories`, `app/services`, and `app/config`.

## Event flow

1. Prediction API commits a prediction to PostgreSQL, then publishes a prediction event.
2. Prediction API stores its training evaluation and model registry record, then publishes an evaluation event.
3. This service consumes both Kafka topics and indexes the event using its prediction/evaluation ID as the Elasticsearch document ID.
4. Dashboard endpoints read persisted source records and the event feed. Replayed Kafka messages overwrite the same event document instead of creating duplicates.

Kafka delivery is at-least-once; offsets are committed only after Elasticsearch indexing succeeds.

## API

All dashboard endpoints require an ADMIN bearer token.

- `GET /health`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent?limit=20`
- `GET /api/dashboard/predictions?task=all&limit=50`
- `GET /api/dashboard/evaluations?task=all&limit=50`

Task values: `all`, `regression`, `classification`.

## Run with Docker Compose

From the repository root:

```bash
docker compose -f docker-compose.yml -f google-analytics-prediction-events/compose.yml up -d --build prediction-events
```

Service URL: `http://localhost:8020`. API documentation: `http://localhost:8020/docs`.

The service connects to the existing PostgreSQL, Kafka and Elasticsearch containers. It does not create or modify prediction/evaluation records.

## Run locally

```powershell
cd google-analytics-prediction-events
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
$env:ELASTICSEARCH_URL="http://localhost:9290"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5540"
$env:KEYCLOAK_ISSUER="http://localhost:8280/realms/google-analytics"
uvicorn app.main:app --reload --port 8020
```

Use the external Kafka listener configured in the root Compose file.
