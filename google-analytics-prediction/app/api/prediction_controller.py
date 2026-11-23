from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AppFeatures
from app.security import require_user
from app.services import predict


router = APIRouter(
    prefix="/api/v1",
    tags=["Predictions"],
)


@router.post("/predictions/rating")
def predict_rating(
    payload: AppFeatures,
    claims: dict = Depends(require_user),
    db: Session = Depends(get_db),
):
    try:
        return predict(
            db,
            "regression",
            payload.model_dump(mode="json"),
        )
    except (
        LookupError,
        FileNotFoundError,
    ) as exception:
        raise HTTPException(
            409,
            str(exception),
        )
    except Exception as exception:
        raise HTTPException(
            500,
            "Rating prediction failed.",
        ) from exception


@router.post("/predictions/installs")
def predict_installs(
    payload: AppFeatures,
    claims: dict = Depends(require_user),
    db: Session = Depends(get_db),
):
    try:
        return predict(
            db,
            "classification",
            payload.model_dump(mode="json"),
        )
    except (
        LookupError,
        FileNotFoundError,
    ) as exception:
        raise HTTPException(
            409,
            str(exception),
        )
    except Exception as exception:
        raise HTTPException(
            500,
            "Install prediction failed.",
        ) from exception


@router.get("/predictions/metadata")
def prediction_metadata(
    claims: dict = Depends(require_user),
):
    return {
        "fields": {
            "app": {
                "type": "string",
                "required": True,
            },
            "category": {
                "type": "string",
                "required": True,
            },
            "reviews": {
                "type": "integer",
                "minimum": 0,
            },
            "size_mb": {
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "type": {
                "type": "enum",
                "values": ["FREE", "PAID"],
            },
            "price": {
                "type": "number",
                "minimum": 0,
                "free_must_be_zero": True,
            },
            "content_rating": {
                "type": "string",
            },
            "genres": {"type": "string"},
            "last_updated": {
                "type": "date",
                "format": "YYYY-MM-DD",
            },
            "current_version": {
                "type": "string",
            },
            "android_version": {
                "type": "string",
            },
        },
        "targets": {
            "rating": "0-5 regression",
            "installs": [
                "<1K",
                "1K-<10K",
                "10K-<100K",
                "100K-<1M",
                "1M-<10M",
                "10M-<100M",
                "100M+",
            ],
        },
    }
