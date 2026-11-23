from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TrainingRequest
from app.security import require_admin
from app.services import train_model


router = APIRouter(
    prefix="/api/v1",
    tags=["Model Training"],
)


@router.post("/training/{task}")
def train(
    task: str,
    request: TrainingRequest,
    claims: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return train_model(
            db,
            task,
            request.algorithm,
            request.test_size,
        )
    except ValueError as exception:
        raise HTTPException(
            422,
            str(exception),
        )
    except Exception as exception:
        raise HTTPException(
            500,
            "Model training failed.",
        ) from exception
