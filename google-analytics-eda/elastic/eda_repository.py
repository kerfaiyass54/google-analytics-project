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

    def save(self, eda: EdaDocument) -> str:
        response = self.client.index(
            index=self.index,
            document=eda.model_dump(mode="json"),
            refresh="wait_for",
        )
        return response["_id"]

    def save_with_id(self, eda_id: str, eda: EdaDocument) -> None:
        self.client.index(
            index=self.index,
            id=eda_id,
            document=eda.model_dump(mode="json", exclude={"eda_id"}),
            refresh="wait_for",
        )

    def find_by_id(self, eda_id: str) -> EdaDocument | None:
        try:
            response = self.client.get(index=self.index, id=eda_id)
            source = response["_source"]
            source["eda_id"] = response["_id"]
            return EdaDocument.model_validate(source)
        except NotFoundError:
            return None

    def find_by_id_and_email(self, eda_id: str, email: str) -> EdaDocument | None:
        response = self.client.search(
            index=self.index,
            size=1,
            query={"bool": {"must": [
                {"term": {"_id": eda_id}},
                {"term": {"email": email}},
            ]}},
        )
        hits = response["hits"]["hits"]
        if not hits:
            return None
        hit = hits[0]
        source = hit["_source"]
        source["eda_id"] = hit["_id"]
        return EdaDocument.model_validate(source)

    def find_all(self, page: int = 0, size: int = 20) -> dict[str, Any]:
        return self.find_filtered(page=page, size=size)

    def find_all_by_email(self, email: str, page: int = 0, size: int = 20) -> dict[str, Any]:
        return self.find_filtered(email=email, page=page, size=size)

    def find_filtered(
        self,
        page: int = 0,
        size: int = 20,
        eda_id: str | None = None,
        email: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        filters: list[dict] = []
        must: list[dict] = []

        if email:
            filters.append({"term": {"email": email}})

        if eda_id:
            must.append({"wildcard": {"_id": {
                "value": f"*{eda_id.strip()}*",
                "case_insensitive": True,
            }}})

        if search and search.strip():
            term = search.strip()
            must.append({"bool": {"should": [
                {"term": {"_id": term}},
                {"wildcard": {"email": {"value": f"*{term}*", "case_insensitive": True}}},
            ], "minimum_should_match": 1}})

        date_range: dict[str, str] = {}
        if date_from:
            date_range["gte"] = date_from
        if date_to:
            date_range["lte"] = date_to
        if date_range:
            filters.append({"range": {"date": date_range}})

        query: dict = {"bool": {}}
        if filters:
            query["bool"]["filter"] = filters
        if must:
            query["bool"]["must"] = must
        if not filters and not must:
            query = {"match_all": {}}

        response = self.client.search(
            index=self.index,
            from_=page * size,
            size=size,
            sort=[{"date": {"order": "desc"}}],
            query=query,
        )
        return self._build_page_result(response, page, size)

    def delete(self, eda_id: str) -> bool:
        try:
            self.client.delete(index=self.index, id=eda_id, refresh="wait_for")
            return True
        except NotFoundError:
            return False

    def count(self) -> int:
        return int(self.client.count(index=self.index)["count"])

    def count_by_email(self, email: str) -> int:
        response = self.client.count(index=self.index, query={"term": {"email": email}})
        return int(response["count"])

    @staticmethod
    def _build_page_result(response, page: int, size: int) -> dict[str, Any]:
        content = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            source["eda_id"] = hit["_id"]
            content.append(EdaDocument.model_validate(source))

        total = response["hits"]["total"]
        if isinstance(total, dict):
            total = total["value"]

        return {
            "content": content,
            "page": page,
            "size": size,
            "total_elements": total,
            "total_pages": (total + size - 1) // size if size > 0 else 0,
        }
