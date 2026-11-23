from app.config import get_settings
from app.elastic.client import client


settings = get_settings()


def ensure_evaluation_index() -> None:
    index = settings.elasticsearch_evaluation_index
    if not client.indices.exists(index=index):
        client.indices.create(
            index=index,
            mappings={
                "properties": {
                    "evaluation_id": {"type": "keyword"},
                    "model_id": {"type": "keyword"},
                    "task": {"type": "keyword"},
                    "algorithm": {"type": "keyword"},
                    "metrics": {
                        "type": "object",
                        "dynamic": True,
                    },
                    "dataset_rows": {"type": "integer"},
                    "train_rows": {"type": "integer"},
                    "test_rows": {"type": "integer"},
                    "created_at": {"type": "date"},
                }
            },
        )


def save_evaluation(document: dict) -> None:
    client.index(
        index=settings.elasticsearch_evaluation_index,
        id=document["evaluation_id"],
        document=document,
        refresh="wait_for",
    )


def list_evaluations(
    task: str,
    limit: int = 50,
) -> list[dict]:
    response = client.search(
        index=settings.elasticsearch_evaluation_index,
        query={"term": {"task": task}},
        size=limit,
        sort=[{"created_at": {"order": "desc"}}],
    )
    return [
        hit["_source"]
        for hit in response["hits"]["hits"]
    ]
