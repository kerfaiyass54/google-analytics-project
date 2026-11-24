import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Environment-backed configuration for the dashboard aggregation service."""

    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9099")
    elasticsearch_url: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9290")
    events_index: str = os.getenv("EVENTS_INDEX", "prediction_dashboard_events")
    evaluations_index: str = os.getenv("EVALUATIONS_INDEX", "prediction_model_evaluations")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5540"))
    postgres_db: str = os.getenv("POSTGRES_DB", "analyticsforgoogle")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    keycloak_issuer: str = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8280/realms/google-analytics").rstrip("/")
    keycloak_jwks_url: str = os.getenv("KEYCLOAK_JWKS_URL", "")
    keycloak_client_id: str = os.getenv("KEYCLOAK_CLIENT_ID", "google-analytics-api")
    admin_role: str = os.getenv("ADMIN_ROLE", "ADMIN")
    consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "prediction-dashboard")
    prediction_topic: str = os.getenv("KAFKA_PREDICTION_TOPIC", "prediction-events")
    evaluation_topic: str = os.getenv("KAFKA_EVALUATION_TOPIC", "evaluation-events")

    @property
    def jwks_url(self) -> str:
        return self.keycloak_jwks_url or f"{self.keycloak_issuer}/protocol/openid-connect/certs"
