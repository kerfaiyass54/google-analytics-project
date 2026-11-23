# Google Play Prediction Service

Independent FastAPI service for Google Play app rating regression and install-bucket classification.

## Responsibilities
- Reads training records from the existing PostgreSQL `google_play_apps` table.
- Saves rating predictions in PostgreSQL table `predict_rating`.
- Saves install-bucket predictions in PostgreSQL table `predict_installs`.
- Persists model metadata and the active model selection in PostgreSQL table `prediction_model_registry`.
- Stores each training evaluation report in Elasticsearch index `prediction_model_evaluations`.
- Stores fitted model pipelines as versioned joblib artifacts. Mount `artifacts/` persistently in deployments.

## Run locally (PowerShell)
```powershell
cd google-analytics-prediction
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8010
```

The defaults match the existing compose stack's host ports (PostgreSQL 5540, Elasticsearch 9290). Adjust credentials and ports in `.env`.

## Run with Docker
Build from the repository root:
```powershell
docker build -t google-analytics-prediction ./google-analytics-prediction
docker run --rm --name google-analytics-prediction --network backend -p 8010:8010 --env-file google-analytics-prediction/.env -e POSTGRES_HOST=analytics_postgres -e ELASTICSEARCH_URL=http://analytics_elasticsearch:9200 -v prediction_artifacts:/app/artifacts google-analytics-prediction
```

Inside Docker, use the compose service/container network names and internal ports (PostgreSQL 5432 and Elasticsearch 9200), not host-mapped ports.

## API
- `GET /health`
- `GET /api/v1/predictions/metadata`
- `POST /api/v1/predictions/rating`
- `POST /api/v1/predictions/installs`
- `GET /api/v1/models`
- `GET /api/v1/models/{task}`
- `POST /api/v1/training/{task}` (admin endpoint; authentication integration is intentionally pending)
- `GET /api/v1/evaluations/{task}`

Training requires enough valid rows and at least two target classes for classification. Model choices are validated per task. A trained model is not activated automatically; explicitly activate it with `POST /api/v1/models/{model_id}/activate`.

## Notes
- Install targets are converted to stable numeric buckets: <1K, 1K–<10K, 10K–<100K, 100K–<1M, 1M–<10M, 10M–<100M, and 100M+.
- App names, category, reviews, size, type, price, content rating, genres, last-updated date, current version, and Android version are model inputs. Rating and installs are never accepted as prediction features.
- The service deliberately does not trust an admin/user role supplied in request data. Secure the training and activation routes with the project's Keycloak admin dependency before exposing the service outside a trusted development environment.
