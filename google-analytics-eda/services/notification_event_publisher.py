from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from kafka import KafkaProducer

logger = logging.getLogger(__name__)
_producer: KafkaProducer | None = None


def publish_notification_event(
    event_type: str,
    *,
    entity_type: str,
    entity_id: str,
    entity_name: str,
    payload: dict | None = None,
) -> None:
    global _producer
    try:
        if _producer is None:
            _producer = KafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
                value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
                retries=3,
                request_timeout_ms=5000,
            )
        event = {
            "eventId": str(uuid4()),
            "eventType": event_type,
            "occurredAt": datetime.now(timezone.utc).isoformat(),
            "entityType": entity_type,
            "entityId": entity_id,
            "entityName": entity_name,
            "payload": payload or {},
        }
        _producer.send("eda-events", event).get(timeout=5)
    except Exception:
        logger.exception("Could not publish notification event %s", event_type)
