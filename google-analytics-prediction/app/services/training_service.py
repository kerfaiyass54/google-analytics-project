from datetime import datetime, timezone
from uuid import uuid4

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.elastic import save_evaluation
from app.ml import (
    build_pipeline,
    features_frame,
)
from app.models import ModelRegistry
from app.services.training_data_service import (
    load_training_data,
)


def train_model(
    db: Session,
    task: str,
    algorithm: str,
    test_size: float,
) -> dict:
    if task not in (
        "regression",
        "classification",
    ):
        raise ValueError(
            "Task must be regression or classification."
        )
    features, target = load_training_data(
        db,
        task,
    )
    if len(features) < 30:
        raise ValueError(
            "At least 30 valid training rows are required."
        )
    if (
        task == "classification"
        and target.nunique() < 2
    ):
        raise ValueError(
            "Install classification requires at least "
            "two distinct install buckets."
        )
    stratify = (
        target
        if (
            task == "classification"
            and target.value_counts().min() >= 2
        )
        else None
    )
    settings = get_settings()
    train_features, test_features, train_target, test_target = (
        train_test_split(
            features,
            target,
            test_size=test_size,
            random_state=settings.random_state,
            stratify=stratify,
        )
    )
    pipeline = build_pipeline(task, algorithm)
    pipeline.fit(
        features_frame(
            train_features.to_dict("records")
        ),
        train_target,
    )
    predicted = pipeline.predict(
        features_frame(
            test_features.to_dict("records")
        )
    )
    if task == "regression":
        metrics = {
            "mae": float(
                mean_absolute_error(
                    test_target,
                    predicted,
                )
            ),
            "rmse": float(np.sqrt(
                mean_squared_error(
                    test_target,
                    predicted,
                )
            )),
            "r2": float(
                r2_score(test_target, predicted)
            ),
        }
    else:
        precision, recall, f1, _ = (
            precision_recall_fscore_support(
                test_target,
                predicted,
                average="weighted",
                zero_division=0,
            )
        )
        labels = sorted(target.unique().tolist())
        metrics = {
            "accuracy": float(
                accuracy_score(
                    test_target,
                    predicted,
                )
            ),
            "precision_weighted": float(precision),
            "recall_weighted": float(recall),
            "f1_weighted": float(f1),
            "labels": labels,
            "confusion_matrix": confusion_matrix(
                test_target,
                predicted,
                labels=labels,
            ).tolist(),
        }
    model_id = str(uuid4())
    evaluation_id = str(uuid4())
    latest_version = db.scalar(
        select(ModelRegistry.version)
        .where(ModelRegistry.task == task)
        .order_by(
            ModelRegistry.version.desc()
        )
        .limit(1)
    ) or 0
    version = latest_version + 1
    directory = settings.model_artifact_dir / task
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory / f"{model_id}.joblib"
    joblib.dump(pipeline, artifact)
    now = datetime.now(timezone.utc).isoformat()
    evaluation = {
        "evaluation_id": evaluation_id,
        "model_id": model_id,
        "task": task,
        "algorithm": algorithm,
        "metrics": metrics,
        "dataset_rows": int(len(features)),
        "train_rows": int(len(train_features)),
        "test_rows": int(len(test_features)),
        "created_at": now,
    }
    try:
        save_evaluation(evaluation)
        registry = ModelRegistry(
            id=model_id,
            task=task,
            algorithm=algorithm,
            version=version,
            artifact_path=str(artifact),
            evaluation_id=evaluation_id,
            is_active=False,
        )
        db.add(registry)
        db.commit()
    except Exception:
        db.rollback()
        artifact.unlink(missing_ok=True)
        raise
    return {
        "model_id": model_id,
        "evaluation_id": evaluation_id,
        "task": task,
        "algorithm": algorithm,
        "version": version,
        "metrics": metrics,
        "dataset_rows": len(features),
        "train_rows": len(train_features),
        "test_rows": len(test_features),
        "is_active": False,
    }
