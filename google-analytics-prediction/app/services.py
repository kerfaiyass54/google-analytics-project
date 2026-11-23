from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_recall_fscore_support, confusion_matrix
from app.config import get_settings
from app.models import ModelRegistry, RatingPrediction, InstallPrediction
from app.ml import build_pipeline, features_frame, parse_installs, install_bucket, validate_rating
from app.elasticsearch import save_evaluation

FEATURE_COLUMNS = ["app", "category", "reviews", "size_mb", "type", "price", "content_rating", "genres", "last_updated", "current_version", "android_version"]
DATA_QUERY = text("""
SELECT app, category, rating, reviews, size_mb, installs, type, price,
       content_rating, genres, last_updated, current_version, android_version
FROM google_play_apps
WHERE app IS NOT NULL AND category IS NOT NULL
""")

def load_training_data(db: Session, task: str) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_sql(DATA_QUERY, db.connection())
    if task == "regression":
        frame["rating"] = pd.to_numeric(frame["rating"], errors="coerce")
        frame = frame[frame["rating"].between(0, 5)].dropna(subset=["rating"])
        target = frame["rating"].astype(float)
    else:
        frame["installs_numeric"] = frame["installs"].map(parse_installs)
        frame = frame.dropna(subset=["installs_numeric"])
        frame["target"] = frame["installs_numeric"].astype(int).map(install_bucket)
        target = frame["target"]
    return frame[FEATURE_COLUMNS].copy(), target

def train_model(db: Session, task: str, algorithm: str, test_size: float) -> dict:
    if task not in ("regression", "classification"):
        raise ValueError("Task must be regression or classification.")
    X, y = load_training_data(db, task)
    if len(X) < 30:
        raise ValueError("At least 30 valid training rows are required.")
    if task == "classification" and y.nunique() < 2:
        raise ValueError("Install classification requires at least two distinct install buckets.")
    stratify = y if task == "classification" and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=get_settings().random_state, stratify=stratify)
    pipeline = build_pipeline(task, algorithm)
    pipeline.fit(features_frame(X_train.to_dict("records")), y_train)
    predicted = pipeline.predict(features_frame(X_test.to_dict("records")))
    if task == "regression":
        metrics = {"mae": float(mean_absolute_error(y_test, predicted)),
                   "rmse": float(np.sqrt(mean_squared_error(y_test, predicted))),
                   "r2": float(r2_score(y_test, predicted))}
    else:
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, predicted, average="weighted", zero_division=0)
        labels = sorted(y.unique().tolist())
        metrics = {"accuracy": float(accuracy_score(y_test, predicted)), "precision_weighted": float(precision),
                   "recall_weighted": float(recall), "f1_weighted": float(f1),
                   "labels": labels, "confusion_matrix": confusion_matrix(y_test, predicted, labels=labels).tolist()}
    settings = get_settings()
    model_id, evaluation_id = str(uuid4()), str(uuid4())
    rows = db.scalar(select(ModelRegistry.version).where(ModelRegistry.task == task).order_by(ModelRegistry.version.desc()).limit(1)) or 0
    version = rows + 1
    directory = settings.model_artifact_dir / task
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory / f"{model_id}.joblib"
    joblib.dump(pipeline, artifact)
    now = datetime.now(timezone.utc).isoformat()
    evaluation = {"evaluation_id": evaluation_id, "model_id": model_id, "task": task, "algorithm": algorithm,
                  "metrics": metrics, "dataset_rows": int(len(X)), "train_rows": int(len(X_train)),
                  "test_rows": int(len(X_test)), "created_at": now}
    try:
        save_evaluation(evaluation)
        registry = ModelRegistry(id=model_id, task=task, algorithm=algorithm, version=version,
                                 artifact_path=str(artifact), evaluation_id=evaluation_id, is_active=False)
        db.add(registry)
        db.commit()
    except Exception:
        db.rollback()
        artifact.unlink(missing_ok=True)
        raise
    return {"model_id": model_id, "evaluation_id": evaluation_id, "task": task, "algorithm": algorithm,
            "version": version, "metrics": metrics, "dataset_rows": len(X), "train_rows": len(X_train),
            "test_rows": len(X_test), "is_active": False}

def activate_model(db: Session, model_id: str) -> dict:
    model = db.get(ModelRegistry, model_id)
    if not model:
        raise LookupError("Model not found.")
    artifact = Path(model.artifact_path)
    if not artifact.is_file():
        raise FileNotFoundError("Model artifact is missing; cannot activate.")
    db.query(ModelRegistry).filter(ModelRegistry.task == model.task).update({ModelRegistry.is_active: False})
    model.is_active = True
    db.commit()
    return {"model_id": model.id, "task": model.task, "is_active": True}

def active_model(db: Session, task: str) -> ModelRegistry:
    model = db.scalar(select(ModelRegistry).where(ModelRegistry.task == task, ModelRegistry.is_active.is_(True)))
    if not model:
        raise LookupError(f"No active model configured for {task}.")
    if not Path(model.artifact_path).is_file():
        raise FileNotFoundError("Active model artifact is missing.")
    return model

def predict(db: Session, task: str, data: dict) -> dict:
    model = active_model(db, task)
    pipeline = joblib.load(model.artifact_path)
    prediction = pipeline.predict(features_frame([data]))[0]
    prediction_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    if task == "regression":
        result = validate_rating(float(prediction))
        record = RatingPrediction(id=prediction_id, app_name=data["app"], input_data=data,
                                  predicted_rating=result, model_id=model.id)
        output: float | str = round(result, 3)
    else:
        result = str(prediction)
        record = InstallPrediction(id=prediction_id, app_name=data["app"], input_data=data,
                                   predicted_bucket=result, model_id=model.id)
        output = result
    db.add(record)
    db.commit()
    return {"prediction_id": prediction_id, "task": task, "model_id": model.id,
            "prediction": output, "created_at": now}

def list_models(db: Session) -> list[dict]:
    models = db.scalars(select(ModelRegistry).order_by(ModelRegistry.created_at.desc())).all()
    return [{"model_id": m.id, "task": m.task, "algorithm": m.algorithm, "version": m.version,
             "is_active": m.is_active, "evaluation_id": m.evaluation_id, "created_at": m.created_at.isoformat()}
            for m in models]
