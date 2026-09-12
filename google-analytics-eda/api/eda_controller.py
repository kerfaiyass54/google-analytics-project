"""
EDA Analysis API.

Provides endpoints for the four Google Play Store EDAs:

    1. Ratings by category
    2. Free vs paid
    3. Install distribution
    4. Review counts

The API returns JSON suitable for direct consumption
by the Angular frontend.

The generated complete analysis is persisted in
Elasticsearch for analysis history.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from schema.eda import (
    CompleteEdaAnalysis,
    FreeVsPaidResponse,
    InstallDistributionResponse,
    RatingsByCategoryResponse,
    ReviewCountsResponse,
)

from security.keycloak import (
    KeycloakUser,
    get_current_user,
)

from services.eda_service import (
    EdaAnalysisService,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/eda",
    tags=["EDA Analysis"],
)


# ============================================================
# DEPENDENCY
# ============================================================

CurrentUser = Annotated[
    KeycloakUser,
    Depends(get_current_user),
]


# ============================================================
# SERVICE
# ============================================================

def get_eda_service() -> EdaAnalysisService:
    """
    Create the EDA service.

    Keeping the service behind a dependency makes the
    controller easy to test and allows dependency overrides.
    """

    return EdaAnalysisService()


EdaServiceDependency = Annotated[
    EdaAnalysisService,
    Depends(get_eda_service),
]


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

@router.get(
    "",
    response_model=CompleteEdaAnalysis,
    summary="Run complete EDA",
    description=(
        "Execute all four Google Play Store exploratory "
        "data analyses."
    ),
)
def get_complete_analysis(
    user: CurrentUser,
    service: EdaServiceDependency,
) -> CompleteEdaAnalysis:
    """
    Execute all four EDAs.

    The authenticated user is used for audit/history
    information.

    The email is obtained from Keycloak and is never
    accepted from the client.
    """

    try:

        return service.run_complete_analysis(
            user_email=user.email,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to execute the EDA analysis."
            ),
        ) from exception


# ============================================================
# EDA 01
# ============================================================

@router.get(
    "/ratings-by-category",
    response_model=RatingsByCategoryResponse,
    summary="Ratings by category",
)
def get_ratings_by_category(
    user: CurrentUser,
    service: EdaServiceDependency,
) -> RatingsByCategoryResponse:
    """
    Execute EDA 01.

    Analyzes:

        - application count
        - rated application count
        - average rating
        - minimum rating
        - maximum rating
        - median rating
        - rating standard deviation

    grouped by category.
    """

    try:

        return service.run_ratings_by_category(
            user_email=user.email,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to calculate ratings by category."
            ),
        ) from exception


# ============================================================
# EDA 02
# ============================================================

@router.get(
    "/free-vs-paid",
    response_model=FreeVsPaidResponse,
    summary="Free versus paid applications",
)
def get_free_vs_paid(
    user: CurrentUser,
    service: EdaServiceDependency,
) -> FreeVsPaidResponse:
    """
    Execute EDA 02.

    Compares FREE and PAID applications using:

        - application count
        - percentages
        - ratings
        - reviews
        - prices
    """

    try:

        return service.run_free_vs_paid(
            user_email=user.email,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to calculate free versus paid "
                "statistics."
            ),
        ) from exception


# ============================================================
# EDA 03
# ============================================================

@router.get(
    "/install-distribution",
    response_model=InstallDistributionResponse,
    summary="Install distribution",
)
def get_install_distribution(
    user: CurrentUser,
    service: EdaServiceDependency,
) -> InstallDistributionResponse:
    """
    Execute EDA 03.

    Analyzes:

        - install distribution
        - average installs
        - median installs
        - total installs
        - category install statistics
        - top installed applications
    """

    try:

        return service.run_install_distribution(
            user_email=user.email,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to calculate install distribution."
            ),
        ) from exception


# ============================================================
# EDA 04
# ============================================================

@router.get(
    "/review-counts",
    response_model=ReviewCountsResponse,
    summary="Review counts",
)
def get_review_counts(
    user: CurrentUser,
    service: EdaServiceDependency,
) -> ReviewCountsResponse:
    """
    Execute EDA 04.

    Analyzes:

        - total reviews
        - average reviews
        - median reviews
        - minimum reviews
        - maximum reviews
        - review standard deviation
        - reviews by category
        - top reviewed applications
        - reviews versus installs
    """

    try:

        return service.run_review_counts(
            user_email=user.email,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to calculate review counts."
            ),
        ) from exception