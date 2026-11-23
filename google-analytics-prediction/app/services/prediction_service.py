from datetime import datetime, timezone
from uuid import uuid4

import joblib
from sqlalchemy.orm import Session

from app.ml import (
    features_frame,
    validate_rating,
)
from app.models import (
    InstallPrediction,
    RatingPrediction,
)
from app.services.model_service import active_model


def predict(
    db: Session,
    task: str,
    data: dict,
) -> dict:
    model = active_model(db, task)
    pipeline = joblib.load(model.artifact_path)
    prediction = pipeline.predict(
        features_frame([data])
    )[0]
    prediction_id = str(uuid4())
    now = datetime.now(
        timezone.utc
    ).isoformat()
    if task == "regression":
        result = validate_rating(
            float(prediction)
        )
        record = RatingPrediction(
            id=prediction_id,
            app_name=data["app"],
            input_data=data,
            predicted_rating=result,
            model_id=model.id,
        )
        output: float | str = round(result, 3)
    else:
        result = str(prediction)
        record = InstallPrediction(
            id=prediction_id,
            app_name=data["app"],
            input_data=data,
            predicted_bucket=result,
            model_id=model.id,
        )
        output = result
    db.add(record)
    db.commit()
    return {
        "prediction_id": prediction_id,
        "task": task,
        "model_id": model.id,
        "prediction": output,
        "created_at": now,
    }
