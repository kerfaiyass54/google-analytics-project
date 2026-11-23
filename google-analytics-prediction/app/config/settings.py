from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Google Play Prediction API"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8010
    postgres_host: str = "localhost"
    postgres_port: int = 5540
    postgres_db: str = "analyticsforgoogle"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    elasticsearch_url: str = "http://localhost:9290"
    elasticsearch_evaluation_index: str = "prediction_model_evaluations"
    model_artifact_dir: Path = Path("artifacts")
    train_test_size: float = 0.2
    random_state: int = 42
    keycloak_issuer: str = "http://localhost:8280/realms/google-analytics"
    keycloak_client_id: str = "google-analytics-api"
    keycloak_audience: str | None = None
    admin_role: str = "ADMIN"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{quote_plus(self.postgres_user)}:"
            f"{quote_plus(self.postgres_password)}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
