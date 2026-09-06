"""
PostgreSQL database connection management.

This module is responsible only for creating and exposing
the SQLAlchemy engine used by the analytics application.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import get_database_config


# ============================================================
# Engine Configuration
# ============================================================

def create_database_engine() -> Engine:
    """
    Create the SQLAlchemy PostgreSQL engine.

    Returns:
        Configured SQLAlchemy Engine.
    """

    config = get_database_config()

    return create_engine(
        config.url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        echo=False,
    )


# ============================================================
# Application Database Engine
# ============================================================

engine: Engine = create_database_engine()


# ============================================================
# Connection Health Check
# ============================================================

def test_connection() -> bool:
    """
    Check whether PostgreSQL is reachable.

    Returns:
        True if the connection succeeds, otherwise False.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception as exception:
        print(
            f"PostgreSQL connection failed: {exception}"
        )

        return False