from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import (
    require_admin,
    require_user,
)
from app.services import (
    activate_model,
    active_model,
    list_models,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Models"],
)


@router.get("/models")
def models(
    claims: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return list_models(db)


@router.get("/models/{task}/active")
def get_active_model(
    task: str,
    claims: dict = Depends(require_user),
    db: Session = Depends(get_db),
):
    try:
        model = active_model(db, task)
        return {
            "model_id": model.id,
            "task": model.task,
            "algorithm": model.algorithm,
            "version": model.version,
        }
    except (
        LookupError,
        FileNotFoundError,
    ) as exception:
        raise HTTPException(
            404,
            str(exception),
        )


@router.post("/models/{model_id}/activate")
def activate(
    model_id: str,
    claims: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return activate_model(db, model_id)
    except LookupError as exception:
        raise HTTPException(
            404,
            str(exception),
        )
    except FileNotFoundError as exception:
        raise HTTPException(
            409,
            str(exception),
        )
