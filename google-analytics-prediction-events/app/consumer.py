import json, logging, threading
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
logger = logging.getLogger(__name__)

class PredictionEventConsumer:
    def __init__(self, kafka_servers: str, elasticsearch_url: str, index: str):
        self.kafka_servers, self.es_url, self.index = kafka_servers, elasticsearch_url, index
        self.stop_event = threading.Event()
        self.thread = None
        self.client = Elasticsearch(elasticsearch_url)

    def ensure_index(self):
        if not self.client.indices.exists(index=self.index):
            self.client.indices.create(index=self.index, mappings={"properties": {
                "event_type": {"type": "keyword"}, "event_id": {"type": "keyword"},
                "task": {"type": "keyword"}, "model_id": {"type": "keyword"},
                "app_name": {"type": "keyword"}, "prediction": {"type": "keyword"},
                "dataset_rows": {"type": "integer"}, "train_rows": {"type": "integer"},
                "test_rows": {"type": "integer"}, "created_at": {"type": "date"},
                "metrics": {"type": "object", "dynamic": True}, "payload": {"type": "object", "enabled": False}
            }})

    def start(self):
        self.ensure_index()
        self.thread = threading.Thread(target=self._consume, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)

    def _consume(self):
        consumer = None
        while not self.stop_event.is_set():
            try:
                if consumer is None:
                    consumer = KafkaConsumer("prediction-events", "evaluation-events",
                        bootstrap_servers=self.kafka_servers.split(","), value_deserializer=lambda b: json.loads(b.decode()),
                        group_id="prediction-dashboard", auto_offset_reset="earliest", enable_auto_commit=True,
                        consumer_timeout_ms=1000)
                for message in consumer:
                    if self.stop_event.is_set(): break
                    data = message.value
                    event_type = "prediction" if message.topic == "prediction-events" else "evaluation"
                    doc = {"event_type": event_type, "event_id": data.get("prediction_id") or data.get("evaluation_id"),
                        "task": data.get("task"), "model_id": data.get("model_id"), "app_name": data.get("app_name"),
                        "prediction": str(data.get("prediction")) if data.get("prediction") is not None else None,
                        "dataset_rows": data.get("dataset_rows"), "train_rows": data.get("train_rows"),
                        "test_rows": data.get("test_rows"), "metrics": data.get("metrics"),
                        "created_at": data.get("created_at"), "payload": data}
                    if doc["event_id"]:
                        self.client.index(index=self.index, id=doc["event_id"], document=doc, refresh=False)
            except Exception:
                logger.exception("Prediction event consumer unavailable; retrying")
                if consumer:
                    try: consumer.close()
                    except Exception: pass
                consumer = None
                self.stop_event.wait(3)
        if consumer:
            consumer.close()
