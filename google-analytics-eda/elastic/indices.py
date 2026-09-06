"""
Elasticsearch index definitions and initialization.

This module defines the mappings for:
    - EDA analysis history
    - EDA export history

Indices are created only when they do not already exist.
Existing indices are never deleted or recreated automatically.
"""

from __future__ import annotations

from elasticsearch import Elasticsearch

from elastic.client import client


# ============================================================
# Index Names
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

            # ------------------------------------------------
            # Analysis metadata
            # ------------------------------------------------

            "analysis_date": {
                "type": "date"
            },

            # ------------------------------------------------
            # EDA 01 — Ratings by Category
            # ------------------------------------------------

            "ratings_by_category": {
                "properties": {

                    "statistics": {
                        "type": "object"
                    },

                    "categories": {
                        "type": "object"
                    }
                }
            },

            # ------------------------------------------------
            # EDA 02 — Free vs Paid
            # ------------------------------------------------

            "free_vs_paid": {
                "properties": {

                    "statistics": {
                        "type": "object"
                    },

                    "distribution": {
                        "type": "object"
                    },

                    "ratings": {
                        "type": "object"
                    },

                    "reviews": {
                        "type": "object"
                    }
                }
            },

            # ------------------------------------------------
            # EDA 03 — Install Distribution
            # ------------------------------------------------

            "install_distribution": {
                "properties": {

                    "statistics": {
                        "type": "object"
                    },

                    "distribution": {
                        "type": "object"
                    },

                    "categories": {
                        "type": "object"
                    }
                }
            },

            # ------------------------------------------------
            # EDA 04 — Review Counts
            # ------------------------------------------------

            "review_counts": {
                "properties": {

                    "statistics": {
                        "type": "object"
                    },

                    "categories": {
                        "type": "object"
                    },

                    "top_applications": {
                        "type": "object"
                    }
                }
            }
        }
    }
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

            "email": {
                "type": "keyword"
            },

            "date": {
                "type": "date"
            },

            "filename": {
                "type": "keyword"
            }
        }
    }
}


# ============================================================
# CREATE INDEX
# ============================================================

def create_index_if_not_exists(
    elasticsearch_client: Elasticsearch,
    index_name: str,
    index_definition: dict,
) -> None:
    """
    Create an Elasticsearch index if it does not already exist.

    Existing indices are preserved.

    Args:
        elasticsearch_client:
            Elasticsearch client instance.

        index_name:
            Name of the index.

        index_definition:
            Index settings and mappings.
    """

    if elasticsearch_client.indices.exists(
        index=index_name
    ):
        return

    elasticsearch_client.indices.create(
        index=index_name,
        settings=index_definition["settings"],
        mappings=index_definition["mappings"],
    )


# ============================================================
# INITIALIZE INDICES
# ============================================================

def initialize_indices(
    elasticsearch_client: Elasticsearch = client,
) -> None:
    """
    Initialize all application Elasticsearch indices.

    This function is safe to call multiple times.
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
# INDEX HEALTH
# ============================================================

def indices_exist(
    elasticsearch_client: Elasticsearch = client,
) -> bool:
    """
    Check whether all required application indices exist.
    """

    return (
        elasticsearch_client.indices.exists(
            index=EDA_ANALYSES_INDEX
        )
        and
        elasticsearch_client.indices.exists(
            index=EDA_EXPORTS_INDEX
        )
    )