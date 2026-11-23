from fastapi import APIRouter, Depends, HTTPException, Query

from app.elastic import list_evaluations
from app.security import require_admin


router = APIRouter(
    prefix="/api/v1",
    tags=["Evaluations"],
)


@router.get("/evaluations/{task}")
def evaluations(
    task: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    claims: dict = Depends(require_admin),
):
    if task not in (
        "regression",
        "classification",
    ):
        raise HTTPException(
            422,
            "Task must be regression or classification.",
        )
    try:
        return list_evaluations(task, limit)
    except Exception as exception:
        raise HTTPException(
            503,
            "Evaluation store unavailable.",
        ) from exception
