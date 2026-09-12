"""
Central Elasticsearch client.

Creates the single Elasticsearch client used by the application.
"""

from __future__ import annotations

from elasticsearch import Elasticsearch

from config import get_elasticsearch_config


# ============================================================
# CONFIGURATION
# ============================================================

config = get_elasticsearch_config()


# ============================================================
# CLIENT
# ============================================================

client = Elasticsearch(
    config.url,
)


# ============================================================
# HEALTH CHECK
# ============================================================

def check_connection() -> bool:
    """
    Check whether Elasticsearch is reachable.
    """

    return bool(client.ping())