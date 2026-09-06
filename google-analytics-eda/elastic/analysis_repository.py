"""
Elasticsearch repository for EDA analysis history.
"""

from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from elastic.client import client
from elastic.indices import EDA_ANALYSES_INDEX
from schema.eda import CompleteEdaAnalysis


class AnalysisRepository:
    """
    Repository for complete EDA analysis documents.
    """

    def __init__(
        self,
        elasticsearch_client: Elasticsearch = client,
    ) -> None:

        self.client = elasticsearch_client
        self.index = EDA_ANALYSES_INDEX

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        analysis: CompleteEdaAnalysis,
        analysis_id: str | None = None,
    ) -> str:
        """
        Save a complete EDA analysis.
        """

        document = analysis.model_dump(
            mode="json"
        )

        response = self.client.index(
            index=self.index,
            id=analysis_id,
            document=document,
            refresh="wait_for",
        )

        return response["_id"]

    # ========================================================
    # FIND BY ID
    # ========================================================

    def find_by_id(
        self,
        analysis_id: str,
    ) -> CompleteEdaAnalysis | None:
        """
        Retrieve an analysis by Elasticsearch ID.
        """

        try:

            response = self.client.get(
                index=self.index,
                id=analysis_id,
            )

        except NotFoundError:

            return None

        source = dict(
            response["_source"]
        )

        source["analysis_id"] = (
            response["_id"]
        )

        return CompleteEdaAnalysis.model_validate(
            source
        )

    # ========================================================
    # FIND ALL
    # ========================================================

    def find_all(
        self,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:
        """
        Retrieve paginated analysis history.
        """

        page = max(
            page,
            0,
        )

        size = min(
            max(size, 1),
            100,
        )

        response = self.client.search(
            index=self.index,
            from_=page * size,
            size=size,
            sort=[
                {
                    "analysis_date": {
                        "order": "desc",
                    }
                }
            ],
            query={
                "match_all": {},
            },
        )

        hits = response[
            "hits"
        ][
            "hits"
        ]

        analyses = [
            self._to_dict(
                hit
            )
            for hit in hits
        ]

        total = response[
            "hits"
        ][
            "total"
        ]

        if isinstance(
            total,
            dict,
        ):
            total = total["value"]

        return {
            "content": analyses,
            "page": page,
            "size": size,
            "total_elements": total,
            "total_pages": (
                (
                    total + size - 1
                )
                // size
                if total > 0
                else 0
            ),
        }

    # ========================================================
    # LATEST
    # ========================================================

    def find_latest(
        self,
    ) -> CompleteEdaAnalysis | None:
        """
        Retrieve the most recent analysis.
        """

        response = self.client.search(
            index=self.index,
            size=1,
            sort=[
                {
                    "analysis_date": {
                        "order": "desc",
                    }
                }
            ],
            query={
                "match_all": {},
            },
        )

        hits = response[
            "hits"
        ][
            "hits"
        ]

        if not hits:
            return None

        return self._to_model(
            hits[0]
        )

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Count stored analyses.
        """

        response = self.client.count(
            index=self.index,
        )

        return int(
            response["count"]
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        analysis_id: str,
    ) -> bool:
        """
        Delete an analysis.
        """

        try:

            self.client.delete(
                index=self.index,
                id=analysis_id,
                refresh="wait_for",
            )

            return True

        except NotFoundError:

            return False

    # ========================================================
    # PRIVATE
    # ========================================================

    @staticmethod
    def _to_dict(
        hit: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert Elasticsearch hit to dictionary.
        """

        return {
            "analysis_id": hit["_id"],
            **hit["_source"],
        }

    @staticmethod
    def _to_model(
        hit: dict[str, Any],
    ) -> CompleteEdaAnalysis:
        """
        Convert Elasticsearch hit to Pydantic model.
        """

        source = dict(
            hit["_source"]
        )

        source["analysis_id"] = (
            hit["_id"]
        )

        return CompleteEdaAnalysis.model_validate(
            source
        )