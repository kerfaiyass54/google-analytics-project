from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RatingPrediction, InstallPrediction
from app.security import require_user

router = APIRouter(prefix="/api/v1/predictions", tags=["My Predictions"])

@router.get("/mine")
def my_predictions(task: str = Query(default="all", pattern="^(all|regression|classification)$"),
                   claims: dict = Depends(require_user), db: Session = Depends(get_db)):
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(401, "User identity missing from token.")
    items = []
    if task in ("all", "regression"):
        rows = db.scalars(select(RatingPrediction).where(RatingPrediction.user_id == user_id).order_by(desc(RatingPrediction.created_at))).all()
        items += [{"id": r.id, "task": "regression", "app_name": r.app_name, "input_data": r.input_data,
                   "prediction": r.predicted_rating, "model_id": r.model_id, "created_at": r.created_at} for r in rows]
    if task in ("all", "classification"):
        rows = db.scalars(select(InstallPrediction).where(InstallPrediction.user_id == user_id).order_by(desc(InstallPrediction.created_at))).all()
        items += [{"id": r.id, "task": "classification", "app_name": r.app_name, "input_data": r.input_data,
                   "prediction": r.predicted_bucket, "model_id": r.model_id, "created_at": r.created_at} for r in rows]
    return sorted(items, key=lambda x: x["created_at"], reverse=True)

@router.get("/{prediction_id}")
def prediction_detail(prediction_id: str, claims: dict = Depends(require_user), db: Session = Depends(get_db)):
    uid = claims.get("sub")
    row = db.scalar(select(RatingPrediction).where(RatingPrediction.id == prediction_id, RatingPrediction.user_id == uid))
    if row:
        return {"id": row.id, "task": "regression", "app_name": row.app_name, "input_data": row.input_data,
                "prediction": row.predicted_rating, "model_id": row.model_id, "created_at": row.created_at}
    row = db.scalar(select(InstallPrediction).where(InstallPrediction.id == prediction_id, InstallPrediction.user_id == uid))
    if row:
        return {"id": row.id, "task": "classification", "app_name": row.app_name, "input_data": row.input_data,
                "prediction": row.predicted_bucket, "model_id": row.model_id, "created_at": row.created_at}
    raise HTTPException(404, "Prediction not found.")
