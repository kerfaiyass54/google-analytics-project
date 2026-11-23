from __future__ import annotations

from typing import Annotated
import json
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schema.eda_document import EdaDocument
from schema.eda_page import EdaPage
from security.keycloak import KeycloakUser, get_current_user
from services.eda_management_service import EdaManagementService
from services.eda_service import EdaAnalysisService


router = APIRouter(prefix="/api/eda", tags=["EDA Analysis"])

CurrentUser = Annotated[KeycloakUser, Depends(get_current_user)]


def get_eda_analysis_service() -> EdaAnalysisService:
    return EdaAnalysisService()


EdaAnalysisServiceDependency = Annotated[
    EdaAnalysisService, Depends(get_eda_analysis_service)
]


def get_eda_management_service() -> EdaManagementService:
    return EdaManagementService()


EdaManagementServiceDependency = Annotated[
    EdaManagementService, Depends(get_eda_management_service)
]


@router.post("", response_model=EdaDocument, status_code=status.HTTP_201_CREATED)
def run_and_save_eda(
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> EdaDocument:
    try:
        return service.run_and_save(user=current_user)
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute and save EDA analysis.",
        ) from exception


@router.get("", response_model=EdaPage)
def get_eda_history(
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
    page: int = Query(default=0, ge=0),
    size: int = Query(default=20, ge=1, le=100),
    eda_id: str | None = Query(default=None, max_length=128),
    creator_email: str | None = Query(default=None, max_length=320),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=320),
    metric_filters: str | None = Query(default=None, max_length=12000),
) -> EdaPage:
    try:
        parsed_metric_filters = None
        if metric_filters:
            try:
                parsed_metric_filters = json.loads(metric_filters)
            except json.JSONDecodeError as exception:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="metric_filters must be valid JSON.",
                ) from exception

            if not isinstance(parsed_metric_filters, dict):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="metric_filters must be a JSON object.",
                )

            allowed_metrics = {
                "ratings_by_category.total_categories",
                "ratings_by_category.total_rated_applications",
                "ratings_by_category.overall_average_rating",
                "free_vs_paid.free_applications",
                "free_vs_paid.paid_applications",
                "free_vs_paid.free_percentage",
                "free_vs_paid.paid_percentage",
                "install_distribution.total_applications",
                "install_distribution.total_installs",
                "install_distribution.average_installs",
                "install_distribution.median_installs",
                "review_counts.statistics.app_count",
                "review_counts.statistics.average_reviews",
                "review_counts.statistics.median_reviews",
                "review_counts.statistics.minimum_reviews",
                "review_counts.statistics.maximum_reviews",
                "review_counts.statistics.total_reviews",
                "review_counts.correlation_reviews_installs",
            }
            if set(parsed_metric_filters) - allowed_metrics:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="One or more EDA metric fields are not supported.",
                )

            for bounds in parsed_metric_filters.values():
                if not isinstance(bounds, dict) or not bounds or set(bounds) - {"min", "max"}:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Each metric filter must contain only min and/or max.",
                    )
                for bound in bounds.values():
                    if isinstance(bound, bool) or not isinstance(bound, (int, float)) or not math.isfinite(bound):
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Metric range bounds must be numeric.",
                        )
                if "min" in bounds and "max" in bounds and bounds["min"] > bounds["max"]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="A metric minimum cannot exceed its maximum.",
                    )

        return service.get_history(
            user=current_user,
            page=page,
            size=size,
            eda_id=eda_id,
            creator_email=creator_email,
            date_from=date_from,
            date_to=date_to,
            search=search,
            metric_filters=parsed_metric_filters,
        )
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve EDA history.",
        ) from exception


@router.get("/ratings-by-category")
def get_ratings_by_category(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):
    try:
        return service.run_ratings_by_category()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute ratings-by-category analysis.",
        ) from exception


@router.get("/free-vs-paid")
def get_free_vs_paid(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):
    try:
        return service.run_free_vs_paid()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute free-vs-paid analysis.",
        ) from exception


@router.get("/install-distribution")
def get_install_distribution(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):
    try:
        return service.run_install_distribution()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute install-distribution analysis.",
        ) from exception


@router.get("/review-counts")
def get_review_counts(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):
    try:
        return service.run_review_counts()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute review-counts analysis.",
        ) from exception


@router.get("/{eda_id}", response_model=EdaDocument)
def get_eda_by_id(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> EdaDocument:
    try:
        eda = service.get_by_id(eda_id=eda_id, user=current_user)
        if eda is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"EDA with id '{eda_id}' was not found.",
            )
        return eda
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve EDA.",
        ) from exception


def require_admin(user: KeycloakUser) -> None:
    if not any(role.upper() == "ADMIN" for role in user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role is required to delete EDA records.",
        )


@router.delete("/{eda_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_eda(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> None:
    require_admin(current_user)
    try:
        deleted = service.delete(eda_id=eda_id, user=current_user)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"EDA with id '{eda_id}' was not found.",
            )
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete EDA.",
        ) from exception
