"""
Elasticsearch index definitions.

Indexes:
    - eda_analyses
    - eda_exports

Existing indexes are never deleted or recreated automatically.
"""

from __future__ import annotations

from elasticsearch import Elasticsearch

from elastic.client import client


# ============================================================
# INDEX NAMES
# ============================================================

EDA_ANALYSES_INDEX = "eda_analyses"

EDA_EXPORTS_INDEX = "eda_exports"


# ============================================================
# EDA ANALYSES MAPPING
# ============================================================

EDA_ANALYSES_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "dynamic": True,
        "properties": {
            "email": {
                "type": "keyword",
            },
            "date": {
                "type": "date",
            },
            "ratings_by_category": {
                "type": "object",
            },
            "free_vs_paid": {
                "type": "object",
            },
            "install_distribution": {
                "type": "object",
            },
            "review_counts": {
                "type": "object",
            },
        },
    },
}


# ============================================================
# EDA EXPORTS MAPPING
# ============================================================

EDA_EXPORTS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "dynamic": False,
        "properties": {
            "eda_id": {
                "type": "keyword",
            },
            "email": {
                "type": "keyword",
            },
            "date": {
                "type": "date",
            },
            "file_type": {
                "type": "keyword",
            },
            "filename": {
                "type": "keyword",
            },
            "content": {
                "type": "binary",
            },
        },
    },
}


# ============================================================
# CREATE INDEX
# ============================================================

def create_index_if_not_exists(
    elasticsearch_client: Elasticsearch,
    index_name: str,
    mapping: dict,
) -> None:
    """
    Create an Elasticsearch index if it does not exist.

    Existing indexes are left untouched.
    """

    if elasticsearch_client.indices.exists(
        index=index_name,
    ):
        return

    elasticsearch_client.indices.create(
        index=index_name,
        settings=mapping["settings"],
        mappings=mapping["mappings"],
    )


# ============================================================
# INITIALIZE INDEXES
# ============================================================

def initialize_indexes(
    elasticsearch_client: Elasticsearch = client,
) -> None:
    """
    Create all required application indexes.
    """

    create_index_if_not_exists(
        elasticsearch_client,
        EDA_ANALYSES_INDEX,
        EDA_ANALYSES_MAPPING,
    )

    create_index_if_not_exists(
        elasticsearch_client,
        EDA_EXPORTS_INDEX,
        EDA_EXPORTS_MAPPING,
    )


# ============================================================
# CHECK INDEXES
# ============================================================

def indexes_exist(
    elasticsearch_client: Elasticsearch = client,
) -> bool:
    """
    Return True when both required indexes exist.
    """

    return (
        elasticsearch_client.indices.exists(
            index=EDA_ANALYSES_INDEX,
        )
        and
        elasticsearch_client.indices.exists(
            index=EDA_EXPORTS_INDEX,
        )
    )