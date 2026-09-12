"""
Central Elasticsearch client.

Creates the Elasticsearch client from the application
configuration and exposes it as the shared `client` instance.
"""

from __future__ import annotations

from elasticsearch import Elasticsearch

from config import get_elasticsearch_config


# ============================================================
# CONFIGURATION
# ============================================================

elasticsearch_config = get_elasticsearch_config()


# ============================================================
# CLIENT OPTIONS
# ============================================================

client_options: dict = {
    "hosts": [elasticsearch_config.url],
}


if (
    elasticsearch_config.username
    and elasticsearch_config.password
):
    client_options["basic_auth"] = (
        elasticsearch_config.username,
        elasticsearch_config.password,
    )


# ============================================================
# ELASTICSEARCH CLIENT
# ============================================================

client = Elasticsearch(
    **client_options
)