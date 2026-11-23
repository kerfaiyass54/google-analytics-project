# Google Play Prediction Service

Independent FastAPI service for Google Play app rating regression and install-bucket classification.

## Responsibilities
- Reads training records from the existing PostgreSQL google_play_apps table.
- Creates the configured PostgreSQL database when it does not exist (the configured PostgreSQL account must have CREATEDB permission).
- Creates predict_rating, predict_installs and prediction_model_registry tables automatically.
- Saves prediction ownership using the authenticated Keycloak subject, so users only see their own prediction history.
- Stores model evaluation reports in Elasticsearch index prediction_model_evaluations.
- Publishes prediction-events and evaluation-events to Kafka for the separate prediction-events dashboard service.
- Persists model pipelines as versioned joblib artifacts.

## Run locally (PowerShell)
    cd google-analytics-prediction
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Copy-Item .env.example .env
    # Update .env with the credentials and host ports from the root compose .env.
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8010

Host defaults are PostgreSQL 5540 and Elasticsearch 9290. Kafka uses the external listener (default 9092); do not use the mapped internal listener port from the Docker screenshot unless it is also configured as the external advertised listener.

## Run with Docker Compose
From the repository root:
    docker compose -f docker-compose.yml -f google-analytics-prediction/compose.yml up -d --build prediction

The service joins the existing backend network and persists model artifacts in prediction_artifacts. In Docker it uses postgres:5432, elasticsearch:9200 and kafka:29092.

## Main API
- GET /health
- GET /api/v1/predictions/metadata
- POST /api/v1/predictions/rating
- POST /api/v1/predictions/installs
- GET /api/v1/predictions/mine?task=all|regression|classification
- GET /api/v1/predictions/{prediction_id}
- GET /api/v1/models (ADMIN)
- POST /api/v1/training/{task} (ADMIN)
- POST /api/v1/models/{model_id}/activate (ADMIN)
- GET /api/v1/evaluations/{task} (ADMIN)

All prediction endpoints require a valid Keycloak bearer token. Training, model listing, activation and evaluation endpoints require ADMIN. New models are not activated automatically.

## Storage
- PostgreSQL is the source of truth for prediction records and model registry.
- Elasticsearch prediction_model_evaluations stores training metrics, model IDs and dataset/train/test row counts.
- The Kafka event service builds a separate searchable event index for the admin dashboard.
