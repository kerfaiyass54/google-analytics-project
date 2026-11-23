from contextlib import closing
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


class PredictionRepository:
    """Read-only queries against the prediction service PostgreSQL tables."""

    def __init__(self, settings: Any):
        self.connection_settings = {
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "dbname": settings.postgres_db,
            "user": settings.postgres_user,
            "password": settings.postgres_password,
            "connect_timeout": 5,
        }

    def _fetch(self, query: str, params: tuple = ()) -> list[dict]:
        with closing(psycopg2.connect(**self.connection_settings)) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

    def counts(self) -> dict:
        query = """
            SELECT
              (SELECT COUNT(*) FROM predict_rating) AS regression_predictions,
              (SELECT COUNT(*) FROM predict_installs) AS classification_predictions,
              (SELECT COUNT(*) FROM prediction_model_registry) AS registered_models,
              (SELECT COUNT(*) FROM prediction_model_registry WHERE is_active = TRUE) AS active_models
        """
        rows = self._fetch(query)
        return rows[0] if rows else {}

    def recent(self, limit: int = 20, task: str = "all") -> list[dict]:
        limit = max(1, min(limit, 100))
        statements = []
        params: list[Any] = []
        if task in ("all", "regression"):
            statements.append("""
                SELECT id, 'regression' AS task, app_name, input_data,
                       predicted_rating::text AS prediction, model_id, user_id, created_at
                FROM predict_rating
            """)
        if task in ("all", "classification"):
            statements.append("""
                SELECT id, 'classification' AS task, app_name, input_data,
                       predicted_bucket AS prediction, model_id, user_id, created_at
                FROM predict_installs
            """)
        if not statements:
            return []
        query = " UNION ALL ".join(statements) + " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        return self._fetch(query, tuple(params))

    def prediction_counts_by_task(self) -> list[dict]:
        rows = self._fetch("""
            SELECT task, COUNT(*) AS total
            FROM (
              SELECT 'regression' AS task FROM predict_rating
              UNION ALL
              SELECT 'classification' AS task FROM predict_installs
            ) AS predictions
            GROUP BY task ORDER BY task
        """)
        return rows
