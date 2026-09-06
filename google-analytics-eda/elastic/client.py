"""
Central application configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class ApplicationSettings(BaseSettings):

    name: str = Field(
        default="Google Play Analytics API",
        validation_alias="APP_NAME",
    )

    version: str = Field(
        default="1.0.0",
        validation_alias="APP_VERSION",
    )

    host: str = Field(
        default="0.0.0.0",
        validation_alias="APP_HOST",
    )

    port: int = Field(
        default=8000,
        validation_alias="APP_PORT",
    )

    debug: bool = Field(
        default=False,
        validation_alias="APP_DEBUG",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DatabaseSettings(BaseSettings):

    host: str = Field(
        default="localhost",
        validation_alias="POSTGRES_HOST",
    )

    port: int = Field(
        default=5432,
        validation_alias="POSTGRES_PORT",
    )

    database: str = Field(
        default="analyticsforgoogle",
        validation_alias="POSTGRES_DB",
    )

    username: str = Field(
        default="postgres",
        validation_alias="POSTGRES_USER",
    )

    password: str = Field(
        default="postgres",
        validation_alias="POSTGRES_PASSWORD",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def url(self) -> str:

        return (
            "postgresql://"
            f"{self.username}:"
            f"{self.password}@"
            f"{self.host}:"
            f"{self.port}/"
            f"{self.database}"
        )


class ElasticsearchSettings(BaseSettings):

    url: str = Field(
        default="http://localhost:9200",
        validation_alias="ELASTICSEARCH_URL",
    )

    username: str | None = Field(
        default=None,
        validation_alias="ELASTICSEARCH_USERNAME",
    )

    password: str | None = Field(
        default=None,
        validation_alias="ELASTICSEARCH_PASSWORD",
    )

    use_ssl: bool = Field(
        default=False,
        validation_alias="ELASTICSEARCH_USE_SSL",
    )

    eda_analysis_index: str = Field(
        default="eda_analyses",
        validation_alias="ELASTICSEARCH_EDA_ANALYSIS_INDEX",
    )

    eda_exports_index: str = Field(
        default="eda_exports",
        validation_alias="ELASTICSEARCH_EDA_EXPORTS_INDEX",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class KeycloakSettings(BaseSettings):

    issuer: str = Field(
        validation_alias="KEYCLOAK_ISSUER",
    )

    client_id: str = Field(
        validation_alias="KEYCLOAK_CLIENT_ID",
    )

    audience: str | None = Field(
        default=None,
        validation_alias="KEYCLOAK_AUDIENCE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ExportSettings(BaseSettings):

    directory: str = Field(
        default="exports",
        validation_alias="EDA_EXPORT_DIRECTORY",
    )

    max_file_size_mb: int = Field(
        default=100,
        validation_alias="EDA_MAX_EXPORT_SIZE_MB",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings:

    def __init__(self) -> None:

        self.application = ApplicationSettings()

        self.database = DatabaseSettings()

        self.elasticsearch = (
            ElasticsearchSettings()
        )

        self.keycloak = KeycloakSettings()

        self.export = ExportSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:

    return Settings()


settings = get_settings()


def get_application_config() -> ApplicationSettings:
    return settings.application


def get_database_config() -> DatabaseSettings:
    return settings.database


def get_elasticsearch_config() -> ElasticsearchSettings:
    return settings.elasticsearch


def get_keycloak_config() -> KeycloakSettings:
    return settings.keycloak


def get_export_config() -> ExportSettings:
    return settings.export