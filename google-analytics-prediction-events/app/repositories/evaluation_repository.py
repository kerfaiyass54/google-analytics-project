from typing import Any

from elasticsearch import Elasticsearch


class EvaluationRepository:
    """Read-only access to the canonical model evaluation index."""

    def __init__(self, client: Elasticsearch, index: str):
        self.client = client
        self.index = index

    def recent(self, limit: int = 20, task: str = "all") -> list[dict]:
        if not self.client.indices.exists(index=self.index):
            return []
        filters = []
        if task in ("regression", "classification"):
            filters.append({"term": {"task": task}})
        response = self.client.search(
            index=self.index,
            size=max(1, min(limit, 100)),
            query={"bool": {"filter": filters}} if filters else {"match_all": {}},
            sort=[{"created_at": {"order": "desc", "unmapped_type": "date"}}],
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def counts(self) -> dict:
        if not self.client.indices.exists(index=self.index):
            return {"total": 0, "regression": 0, "classification": 0}
        response = self.client.search(
            index=self.index,
            size=0,
            aggs={
                "by_task": {"terms": {"field": "task", "size": 5}},
            },
        )
        counts = {bucket["key"]: bucket["doc_count"]
                  for bucket in response["aggregations"]["by_task"]["buckets"]}
        return {
            "total": sum(counts.values()),
            "regression": counts.get("regression", 0),
            "classification": counts.get("classification", 0),
        }
