from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ModelRegistry
from app.services.event_publisher import publish_event


def activate_model(
    db: Session,
    model_id: str,
) -> dict:
    model = db.get(ModelRegistry, model_id)
    if not model:
        raise LookupError("Model not found.")
    artifact = Path(model.artifact_path)
    if not artifact.is_file():
        raise FileNotFoundError(
            "Model artifact is missing; cannot activate."
        )
    (
        db.query(ModelRegistry)
        .filter(ModelRegistry.task == model.task)
        .update({ModelRegistry.is_active: False})
    )
    was_active = model.is_active
    model.is_active = True
    db.commit()
    if not was_active:
        publish_event("model-events", {
            "eventId": str(uuid4()),
            "eventType": "MODEL_PUBLISHED",
            "occurredAt": datetime.now(timezone.utc).isoformat(),
            "entityType": "MODEL",
            "entityId": model.id,
            "entityName": f"{model.task} {model.algorithm} v{model.version}",
            "payload": {"task": model.task, "algorithm": model.algorithm, "version": model.version},
        })
    return {
        "model_id": model.id,
        "task": model.task,
        "is_active": True,
    }


def active_model(
    db: Session,
    task: str,
) -> ModelRegistry:
    model = db.scalar(
        select(ModelRegistry).where(
            ModelRegistry.task == task,
            ModelRegistry.is_active.is_(True),
        )
    )
    if not model:
        raise LookupError(
            f"No active model configured for {task}."
        )
    if not Path(model.artifact_path).is_file():
        raise FileNotFoundError(
            "Active model artifact is missing."
        )
    return model


def list_models(
    db: Session,
) -> list[dict]:
    models = db.scalars(
        select(ModelRegistry).order_by(
            ModelRegistry.created_at.desc()
        )
    ).all()
    return [
        {
            "model_id": model.id,
            "task": model.task,
            "algorithm": model.algorithm,
            "version": model.version,
            "is_active": model.is_active,
            "evaluation_id": model.evaluation_id,
            "created_at": model.created_at.isoformat(),
        }
        for model in models
    ]
