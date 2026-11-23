from datetime import datetime, timezone
from uuid import uuid4
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error, mean_squared_error, precision_recall_fscore_support, r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import get_settings
from app.elastic import save_evaluation
from app.ml import build_pipeline, features_frame
from app.models import ModelRegistry
from app.services.training_data_service import load_training_data
from app.services.event_publisher import publish_event

def train_model(db: Session, task: str, algorithm: str, test_size: float) -> dict:
    if task not in ("regression", "classification"):
        raise ValueError("Task must be regression or classification.")
    features, target = load_training_data(db, task)
    if len(features) < 30:
        raise ValueError("At least 30 valid training rows are required.")
    if task == "classification" and target.nunique() < 2:
        raise ValueError("Install classification requires at least two distinct install buckets.")
    stratify = target if task == "classification" and target.value_counts().min() >= 2 else None
    settings = get_settings()
    train_x, test_x, train_y, test_y = train_test_split(features, target, test_size=test_size,
        random_state=settings.random_state, stratify=stratify)
    pipeline = build_pipeline(task, algorithm)
    pipeline.fit(features_frame(train_x.to_dict("records")), train_y)
    predicted = pipeline.predict(features_frame(test_x.to_dict("records")))
    if task == "regression":
        metrics = {"mae": float(mean_absolute_error(test_y, predicted)),
            "rmse": float(np.sqrt(mean_squared_error(test_y, predicted))), "r2": float(r2_score(test_y, predicted))}
    else:
        precision, recall, f1, _ = precision_recall_fscore_support(test_y, predicted, average="weighted", zero_division=0)
        labels = sorted(target.unique().tolist())
        metrics = {"accuracy": float(accuracy_score(test_y, predicted)), "precision_weighted": float(precision),
            "recall_weighted": float(recall), "f1_weighted": float(f1), "labels": labels,
            "confusion_matrix": confusion_matrix(test_y, predicted, labels=labels).tolist()}
    model_id, evaluation_id = str(uuid4()), str(uuid4())
    latest = db.scalar(select(ModelRegistry.version).where(ModelRegistry.task == task).order_by(ModelRegistry.version.desc()).limit(1)) or 0
    version = latest + 1
    directory = settings.model_artifact_dir / task
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory / f"{model_id}.joblib"
    joblib.dump(pipeline, artifact)
    evaluation = {"evaluation_id": evaluation_id, "model_id": model_id, "task": task, "algorithm": algorithm,
        "metrics": metrics, "dataset_rows": int(len(features)), "train_rows": int(len(train_x)),
        "test_rows": int(len(test_x)), "created_at": datetime.now(timezone.utc).isoformat()}
    try:
        save_evaluation(evaluation)
        db.add(ModelRegistry(id=model_id, task=task, algorithm=algorithm, version=version,
            artifact_path=str(artifact), evaluation_id=evaluation_id, is_active=False))
        db.commit()
    except Exception:
        db.rollback()
        artifact.unlink(missing_ok=True)
        raise
    publish_event("evaluation-events", evaluation)
    return {"model_id": model_id, "evaluation_id": evaluation_id, "task": task, "algorithm": algorithm,
        "version": version, "metrics": metrics, "dataset_rows": len(features), "train_rows": len(train_x),
        "test_rows": len(test_x), "is_active": False}
