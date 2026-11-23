from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AppFeatures, TrainingRequest
from app.services import predict, train_model, activate_model, list_models, active_model
from app.elasticsearch import list_evaluations

router = APIRouter(prefix="/api/v1", tags=["Prediction and Model Management"])

@router.post("/predictions/rating")
def predict_rating(payload: AppFeatures, db: Session = Depends(get_db)):
    try: return predict(db, "regression", payload.model_dump(mode="json"))
    except (LookupError, FileNotFoundError) as exc: raise HTTPException(409, str(exc))
    except Exception as exc: raise HTTPException(500, "Rating prediction failed.") from exc

@router.post("/predictions/installs")
def predict_installs(payload: AppFeatures, db: Session = Depends(get_db)):
    try: return predict(db, "classification", payload.model_dump(mode="json"))
    except (LookupError, FileNotFoundError) as exc: raise HTTPException(409, str(exc))
    except Exception as exc: raise HTTPException(500, "Install prediction failed.") from exc

@router.post("/training/{task}")
def train(task: str, request: TrainingRequest, db: Session = Depends(get_db)):
    try: return train_model(db, task, request.algorithm, request.test_size)
    except ValueError as exc: raise HTTPException(422, str(exc))
    except Exception as exc: raise HTTPException(500, "Model training failed.") from exc

@router.get("/models")
def models(db: Session = Depends(get_db)):
    return list_models(db)

@router.get("/models/{task}/active")
def get_active_model(task: str, db: Session = Depends(get_db)):
    try:
        model = active_model(db, task)
        return {"model_id": model.id, "task": model.task, "algorithm": model.algorithm, "version": model.version}
    except (LookupError, FileNotFoundError) as exc: raise HTTPException(404, str(exc))

@router.post("/models/{model_id}/activate")
def activate(model_id: str, db: Session = Depends(get_db)):
    try: return activate_model(db, model_id)
    except LookupError as exc: raise HTTPException(404, str(exc))
    except FileNotFoundError as exc: raise HTTPException(409, str(exc))

@router.get("/evaluations/{task}")
def evaluations(task: str, limit: int = Query(default=50, ge=1, le=200)):
    if task not in ("regression", "classification"):
        raise HTTPException(422, "Task must be regression or classification.")
    try: return list_evaluations(task, limit)
    except Exception as exc: raise HTTPException(503, "Evaluation store unavailable.") from exc

@router.get("/predictions/metadata")
def prediction_metadata():
    return {
        "fields": {
            "app": {"type": "string", "required": True},
            "category": {"type": "string", "required": True},
            "reviews": {"type": "integer", "minimum": 0},
            "size_mb": {"type": "number", "exclusiveMinimum": 0},
            "type": {"type": "enum", "values": ["Free", "Paid"]},
            "price": {"type": "number", "minimum": 0, "free_must_be_zero": True},
            "content_rating": {"type": "string"},
            "genres": {"type": "string"},
            "last_updated": {"type": "date", "format": "YYYY-MM-DD"},
            "current_version": {"type": "string"},
            "android_version": {"type": "string"}
        },
        "targets": {"rating": "0-5 regression", "installs": ["<1K", "1K-<10K", "10K-<100K", "100K-<1M", "1M-<10M", "10M-<100M", "100M+"]}
    }
