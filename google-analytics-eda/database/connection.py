from __future__ import annotations

import os

from sqlalchemy import create_engine


DATABASE_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

DATABASE_PORT = os.getenv(
    "POSTGRES_PORT",
    "5540",
)

DATABASE_NAME = os.getenv(
    "POSTGRES_DB",
    "analyticsforgoogle",
)

DATABASE_USER = os.getenv(
    "POSTGRES_USER",
    "postgres",
)

DATABASE_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "postgres",
)


DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}"
    f"/{DATABASE_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)