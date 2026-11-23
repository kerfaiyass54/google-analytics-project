from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RatingPrediction, InstallPrediction
from app.security import require_admin

router = APIRouter(prefix="/api/v1/admin/predictions", tags=["Admin Predictions"])

@router.get("")
def all_predictions(model_id: str | None = None,
                   task: str = Query(default="all", pattern="^(all|regression|classification)$"),
                   limit: int = Query(default=100, ge=1, le=500),
                   claims: dict = Depends(require_admin), db: Session = Depends(get_db)):
    items = []
    if task in ("all", "regression"):
        query = select(RatingPrediction).order_by(desc(RatingPrediction.created_at))
        if model_id and model_id != "all":
            query = query.where(RatingPrediction.model_id == model_id)
        rows = db.scalars(query.limit(limit)).all()
        items += [{"id": r.id, "task": "regression", "app_name": r.app_name, "input_data": r.input_data,
                   "prediction": r.predicted_rating, "model_id": r.model_id, "user_id": r.user_id,
                   "created_at": r.created_at} for r in rows]
    if task in ("all", "classification"):
        query = select(InstallPrediction).order_by(desc(InstallPrediction.created_at))
        if model_id and model_id != "all":
            query = query.where(InstallPrediction.model_id == model_id)
        rows = db.scalars(query.limit(limit)).all()
        items += [{"id": r.id, "task": "classification", "app_name": r.app_name, "input_data": r.input_data,
                   "prediction": r.predicted_bucket, "model_id": r.model_id, "user_id": r.user_id,
                   "created_at": r.created_at} for r in rows]
    return sorted(items, key=lambda item: item["created_at"], reverse=True)[:limit]
