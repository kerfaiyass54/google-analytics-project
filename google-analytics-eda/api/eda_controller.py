from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schema.eda_document import EdaDocument
from schema.eda_page import EdaPage

from security.keycloak import (
    KeycloakUser,
    get_current_user,
)

from services.eda_management_service import (
    EdaManagementService,
)

from services.eda_service import (
    EdaAnalysisService,
)


router = APIRouter(
    prefix="/api/eda",
    tags=["EDA Analysis"],
)


# ============================================================
# CURRENT USER
# ============================================================

CurrentUser = Annotated[
    KeycloakUser,
    Depends(get_current_user),
]


# ============================================================
# ANALYSIS SERVICE
# ============================================================

def get_eda_analysis_service() -> EdaAnalysisService:

    return EdaAnalysisService()


EdaAnalysisServiceDependency = Annotated[
    EdaAnalysisService,
    Depends(get_eda_analysis_service),
]


# ============================================================
# MANAGEMENT SERVICE
# ============================================================

def get_eda_management_service() -> EdaManagementService:

    return EdaManagementService()


EdaManagementServiceDependency = Annotated[
    EdaManagementService,
    Depends(get_eda_management_service),
]


# ============================================================
# RUN + SAVE COMPLETE EDA
# ============================================================

@router.post(
    "",
    response_model=EdaDocument,
    status_code=status.HTTP_201_CREATED,
)
def run_and_save_eda(
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> EdaDocument:

    try:

        return service.run_and_save(
            user=current_user
        )

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to execute and "
                "save EDA analysis."
            ),
        ) from exception


# ============================================================
# GET EDA HISTORY
# ============================================================

@router.get(
    "",
    response_model=EdaPage,
)
def get_eda_history(
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
    page: int = Query(
        default=0,
        ge=0,
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> EdaPage:

    try:

        return service.get_history(
            user=current_user,
            page=page,
            size=size,
        )

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve EDA history.",
        ) from exception


# ============================================================
# RATINGS BY CATEGORY
# ============================================================

@router.get(
    "/ratings-by-category",
)
def get_ratings_by_category(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):

    try:

        return service.run_ratings_by_category()

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to execute "
                "ratings-by-category analysis."
            ),
        ) from exception


# ============================================================
# FREE VS PAID
# ============================================================

@router.get(
    "/free-vs-paid",
)
def get_free_vs_paid(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):

    try:

        return service.run_free_vs_paid()

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to execute "
                "free-vs-paid analysis."
            ),
        ) from exception


# ============================================================
# INSTALL DISTRIBUTION
# ============================================================

@router.get(
    "/install-distribution",
)
def get_install_distribution(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):

    try:

        return service.run_install_distribution()

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to execute "
                "install-distribution analysis."
            ),
        ) from exception


# ============================================================
# REVIEW COUNTS
# ============================================================

@router.get(
    "/review-counts",
)
def get_review_counts(
    current_user: CurrentUser,
    service: EdaAnalysisServiceDependency,
):

    try:

        return service.run_review_counts()

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to execute "
                "review-counts analysis."
            ),
        ) from exception


# ============================================================
# GET EDA BY ID
# ============================================================

@router.get(
    "/{eda_id}",
    response_model=EdaDocument,
)
def get_eda_by_id(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> EdaDocument:

    try:

        eda = service.get_by_id(
            eda_id=eda_id,
            user=current_user,
        )

        if eda is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"EDA with id "
                    f"'{eda_id}' was not found."
                ),
            )

        return eda

    except HTTPException:

        raise

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve EDA.",
        ) from exception


# ============================================================
# DELETE EDA
# ============================================================

@router.delete(
    "/{eda_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_eda(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaManagementServiceDependency,
) -> None:

    try:

        deleted = service.delete(
            eda_id=eda_id,
            user=current_user,
        )

        if not deleted:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"EDA with id "
                    f"'{eda_id}' was not found."
                ),
            )

    except HTTPException:

        raise

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete EDA.",
        ) from exception