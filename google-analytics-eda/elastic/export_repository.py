from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from elastic.client import client
from elastic.indices import EDA_EXPORTS_INDEX
from schema.export_document import ExportDocument


class ExportRepository:

    def __init__(
        self,
        elasticsearch_client: Elasticsearch = client,
    ) -> None:

        self.client = elasticsearch_client
        self.index = EDA_EXPORTS_INDEX

    # ============================================================
    # SAVE
    # ============================================================

    def save(
        self,
        export: ExportDocument,
    ) -> str:

        response = self.client.index(
            index=self.index,
            document=export.model_dump(
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
        export_id: str,
    ) -> ExportDocument | None:

        try:

            response = self.client.get(
                index=self.index,
                id=export_id,
            )

            source = response["_source"]

            source["export_id"] = response["_id"]

            return ExportDocument.model_validate(
                source
            )

        except NotFoundError:

            return None

    # ============================================================
    # FIND BY ID + OWNER
    # ============================================================

    def find_by_id_and_email(
        self,
        export_id: str,
        email: str,
    ) -> ExportDocument | None:

        response = self.client.search(
            index=self.index,
            size=1,
            query={
                "bool": {
                    "must": [
                        {
                            "ids": {
                                "values": [
                                    export_id
                                ]
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

        source["export_id"] = hit["_id"]

        return ExportDocument.model_validate(
            source
        )

    # ============================================================
    # FIND BY EDA ID
    # ============================================================

    def find_by_eda_id(
        self,
        eda_id: str,
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
                    "eda_id": eda_id
                }
            },
        )

        return self._build_page_result(
            response,
            page,
            size,
        )

    # ============================================================
    # FIND BY EDA ID + OWNER
    # ============================================================

    def find_by_eda_id_and_email(
        self,
        eda_id: str,
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
                "bool": {
                    "must": [
                        {
                            "term": {
                                "eda_id": eda_id
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
        export_id: str,
    ) -> bool:

        try:

            self.client.delete(
                index=self.index,
                id=export_id,
                refresh="wait_for",
            )

            return True

        except NotFoundError:

            return False

    # ============================================================
    # DELETE BY EDA
    # ============================================================

    def delete_by_eda_id(
        self,
        eda_id: str,
    ) -> None:

        self.client.delete_by_query(
            index=self.index,
            query={
                "term": {
                    "eda_id": eda_id
                }
            },
            refresh=True,
        )

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
    # BUILD PAGE RESULT
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

            source["export_id"] = hit["_id"]

            content.append(
                ExportDocument.model_validate(
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

    def find_by_email(
            self,
            email: str,
            page: int = 0,
            size: int = 20,
    ) -> dict:

        result = self._client.search(
            index=self._index_name,
            query={
                "term": {
                    "email.keyword": email,
                }
            },
            from_=page * size,
            size=size,
            sort=[
                {
                    "date": {
                        "order": "desc",
                    }
                }
            ],
        )

        exports = [
            ExportDocument(
                **hit["_source"]
            )
            for hit in result["hits"]["hits"]
        ]

        total_elements = (
            result["hits"]["total"]["value"]
        )

        total_pages = (
            (total_elements + size - 1) // size
            if total_elements > 0
            else 0
        )

        return {
            "content": exports,
            "page": page,
            "size": size,
            "total_elements": total_elements,
            "total_pages": total_pages,
        }