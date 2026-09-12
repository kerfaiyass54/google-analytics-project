from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from elastic.client import client
from elastic.indices import EDA_ANALYSES_INDEX
from schema.eda_document import EdaDocument


class EdaRepository:

    def __init__(
        self,
        elasticsearch_client: Elasticsearch = client,
    ) -> None:

        self.client = elasticsearch_client
        self.index = EDA_ANALYSES_INDEX

    # ============================================================
    # SAVE
    # ============================================================

    def save(
        self,
        eda: EdaDocument,
    ) -> str:

        response = self.client.index(
            index=self.index,
            document=eda.model_dump(
                mode="json"
            ),
            refresh="wait_for",
        )

        return response["_id"]

    # ============================================================
    # FIND BY ID
    # ============================================================

    def find_by_id(
        self,
        eda_id: str,
    ) -> EdaDocument | None:

        try:

            response = self.client.get(
                index=self.index,
                id=eda_id,
            )

            source = response["_source"]

            source["eda_id"] = response["_id"]

            return EdaDocument.model_validate(
                source
            )

        except NotFoundError:

            return None

    # ============================================================
    # FIND BY ID + OWNER
    # ============================================================

    def find_by_id_and_email(
        self,
        eda_id: str,
        email: str,
    ) -> EdaDocument | None:

        response = self.client.search(
            index=self.index,
            size=1,
            query={
                "bool": {
                    "must": [
                        {
                            "term": {
                                "_id": eda_id
                            }
                        },
                        {
                            "term": {
                                "email": email
                            }
                        },
                    ]
                }
            },
        )

        hits = response["hits"]["hits"]

        if not hits:
            return None

        hit = hits[0]

        source = hit["_source"]

        source["eda_id"] = hit["_id"]

        return EdaDocument.model_validate(
            source
        )

    # ============================================================
    # FIND ALL
    # ============================================================

    def find_all(
        self,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:

        response = self.client.search(
            index=self.index,
            from_=page * size,
            size=size,
            sort=[
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ],
            query={
                "match_all": {}
            },
        )

        return self._build_page_result(
            response,
            page,
            size,
        )

    # ============================================================
    # FIND ALL BY OWNER
    # ============================================================

    def find_all_by_email(
        self,
        email: str,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:

        response = self.client.search(
            index=self.index,
            from_=page * size,
            size=size,
            sort=[
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ],
            query={
                "term": {
                    "email": email
                }
            },
        )

        return self._build_page_result(
            response,
            page,
            size,
        )

    # ============================================================
    # DELETE
    # ============================================================

    def delete(
        self,
        eda_id: str,
    ) -> bool:

        try:

            self.client.delete(
                index=self.index,
                id=eda_id,
                refresh="wait_for",
            )

            return True

        except NotFoundError:

            return False

    # ============================================================
    # COUNT
    # ============================================================

    def count(self) -> int:

        response = self.client.count(
            index=self.index
        )

        return int(
            response["count"]
        )

    # ============================================================
    # COUNT BY OWNER
    # ============================================================

    def count_by_email(
        self,
        email: str,
    ) -> int:

        response = self.client.count(
            index=self.index,
            query={
                "term": {
                    "email": email
                }
            },
        )

        return int(
            response["count"]
        )

    # ============================================================
    # PAGE RESULT
    # ============================================================

    @staticmethod
    def _build_page_result(
        response,
        page: int,
        size: int,
    ) -> dict[str, Any]:

        hits = response["hits"]["hits"]

        content = []

        for hit in hits:

            source = hit["_source"]

            source["eda_id"] = hit["_id"]

            content.append(
                EdaDocument.model_validate(
                    source
                )
            )

        total = response["hits"]["total"]

        if isinstance(total, dict):
            total = total["value"]

        return {
            "content": content,
            "page": page,
            "size": size,
            "total_elements": total,
            "total_pages": (
                (total + size - 1) // size
                if size > 0
                else 0
            ),
        }