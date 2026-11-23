from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AppFeatures
from app.security import require_user
from app.services import predict

router = APIRouter(prefix="/api/v1", tags=["Predictions"])

@router.post("/predictions/rating")
def predict_rating(payload: AppFeatures, claims: dict = Depends(require_user), db: Session = Depends(get_db)):
    try:
        return predict(db, "regression", payload.model_dump(mode="json"), claims.get("sub"))
    except (LookupError, FileNotFoundError) as exc:
        raise HTTPException(409, str(exc))
    except Exception as exc:
        raise HTTPException(500, "Rating prediction failed.") from exc

@router.post("/predictions/installs")
def predict_installs(payload: AppFeatures, claims: dict = Depends(require_user), db: Session = Depends(get_db)):
    try:
        return predict(db, "classification", payload.model_dump(mode="json"), claims.get("sub"))
    except (LookupError, FileNotFoundError) as exc:
        raise HTTPException(409, str(exc))
    except Exception as exc:
        raise HTTPException(500, "Install prediction failed.") from exc

@router.get("/predictions/metadata")
def prediction_metadata(claims: dict = Depends(require_user)):
    return {"fields": {"app": {"type": "string", "required": True}, "category": {"type": "string", "required": True},
        "reviews": {"type": "integer", "minimum": 0}, "size_mb": {"type": "number", "exclusiveMinimum": 0},
        "type": {"type": "enum", "values": ["FREE", "PAID"]}, "price": {"type": "number", "minimum": 0},
        "content_rating": {"type": "string"}, "genres": {"type": "string"},
        "last_updated": {"type": "date", "format": "YYYY-MM-DD"}, "current_version": {"type": "string"},
        "android_version": {"type": "string"}},
        "targets": {"rating": "0-5 regression", "installs": ["<1K", "1K-<10K", "10K-<100K", "100K-<1M", "1M-<10M", "10M-<100M", "100M+"]}}
