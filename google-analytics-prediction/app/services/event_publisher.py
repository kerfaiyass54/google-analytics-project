import json, logging
from kafka import KafkaProducer
from app.config import get_settings
logger = logging.getLogger(__name__)
_producer = None

def publish_event(topic: str, event: dict) -> None:
    global _producer
    try:
        settings = get_settings()
        if _producer is None:
            _producer = KafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
                retries=3, request_timeout_ms=5000)
        _producer.send(topic, event).get(timeout=5)
    except Exception:
        logger.exception("Kafka event publish failed for topic %s", topic)
