import json
import logging
import threading
from typing import Any

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


class PredictionEventConsumer:
    """Consumes prediction lifecycle events and materializes an idempotent ES event feed."""

    def __init__(self, settings: Any, client: Elasticsearch):
        self.settings = settings
        self.client = client
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def ensure_index(self) -> None:
        if self.client.indices.exists(index=self.settings.events_index):
            return
        self.client.indices.create(
            index=self.settings.events_index,
            mappings={"properties": {
                "event_type": {"type": "keyword"},
                "event_id": {"type": "keyword"},
                "task": {"type": "keyword"},
                "model_id": {"type": "keyword"},
                "app_name": {"type": "keyword"},
                "prediction": {"type": "keyword"},
                "dataset_rows": {"type": "integer"},
                "train_rows": {"type": "integer"},
                "test_rows": {"type": "integer"},
                "created_at": {"type": "date"},
                "metrics": {"type": "object", "dynamic": True},
                "payload": {"type": "object", "enabled": False},
            }},
        )

    def start(self) -> None:
        self.ensure_index()
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._consume, name="prediction-event-consumer", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=8)

    def _document(self, topic: str, data: dict) -> dict:
        event_type = "prediction" if topic == self.settings.prediction_topic else "evaluation"
        event_id = data.get("prediction_id") or data.get("evaluation_id")
        if not event_id:
            raise ValueError("Received an event without a prediction_id/evaluation_id.")
        return {
            "event_type": event_type,
            "event_id": str(event_id),
            "task": data.get("task"),
            "model_id": data.get("model_id"),
            "app_name": data.get("app_name"),
            "prediction": str(data["prediction"]) if data.get("prediction") is not None else None,
            "dataset_rows": data.get("dataset_rows"),
            "train_rows": data.get("train_rows"),
            "test_rows": data.get("test_rows"),
            "metrics": data.get("metrics"),
            "created_at": data.get("created_at"),
            "payload": data,
        }

    def _consume(self) -> None:
        consumer = None
        topics = [self.settings.prediction_topic, self.settings.evaluation_topic]
        while not self.stop_event.is_set():
            try:
                if consumer is None:
                    consumer = KafkaConsumer(
                        *topics,
                        bootstrap_servers=self.settings.kafka_bootstrap_servers.split(","),
                        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
                        group_id=self.settings.consumer_group,
                        auto_offset_reset="earliest",
                        enable_auto_commit=False,
                        consumer_timeout_ms=1000,
                    )
                for message in consumer:
                    if self.stop_event.is_set():
                        break
                    document = self._document(message.topic, message.value)
                    self.client.index(
                        index=self.settings.events_index,
                        id=document["event_id"],
                        document=document,
                        refresh=False,
                    )
                    # Commit only after Elasticsearch confirms the event is indexed.
                    consumer.commit()
            except Exception:
                logger.exception("Prediction event processing failed; reconnecting.")
                if consumer is not None:
                    try:
                        consumer.close()
                    except Exception:
                        logger.exception("Could not close Kafka consumer.")
                consumer = None
                self.stop_event.wait(3)
        if consumer is not None:
            consumer.close()
