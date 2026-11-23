from __future__ import annotations

import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from schema.export_page import ExportPage

from security.keycloak import (
    KeycloakUser,
    get_current_user,
)

from services.eda_export_service import EdaExportService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/eda",
    tags=["EDA Exports"],
)


# ============================================================
# CURRENT USER
# ============================================================

CurrentUser = Annotated[
    KeycloakUser,
    Depends(get_current_user),
]


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_eda_export_service() -> EdaExportService:
    return EdaExportService()


EdaExportServiceDependency = Annotated[
    EdaExportService,
    Depends(get_eda_export_service),
]


# ============================================================
# CREATE EXCEL EXPORT
# ============================================================

@router.post(
    "/{eda_id}/exports/xlsx",
    status_code=status.HTTP_201_CREATED,
)
def export_excel(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> Response:

    try:
        return service.export_excel(
            eda_id=eda_id,
            user=current_user,
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception),
        ) from exception
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Excel export.",
        ) from exception


# ============================================================
# CREATE CHART ZIP EXPORT
# ============================================================

@router.post(
    "/{eda_id}/exports/zip",
    status_code=status.HTTP_201_CREATED,
)
def export_charts_zip(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> Response:

    try:
        return service.export_charts_zip(
            eda_id=eda_id,
            user=current_user,
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception),
        ) from exception
    except Exception as exception:
        logger.exception("Chart ZIP export failed for EDA %s", eda_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chart ZIP export.",
        ) from exception


# ============================================================
# GET CURRENT USER EXPORT HISTORY
# ============================================================

# ============================================================
# GET CURRENT USER EXPORT HISTORY
# ============================================================

@router.get(
    "/exports/my",
    response_model=ExportPage,
)
def get_my_exports(
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
    page: int = Query(
        default=0,
        ge=0,
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> ExportPage:

    try:

        return service.get_exports_by_email(
            email=current_user.email,
            page=page,
            size=size,
        )

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user exports.",
        ) from exception


# ============================================================
# GET EXPORT HISTORY FOR ONE EDA
# ============================================================

@router.get(
    "/{eda_id}/exports",
    response_model=ExportPage,
)
def get_exports(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
    page: int = Query(
        default=0,
        ge=0,
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> ExportPage:

    try:

        return service.get_exports(
            eda_id=eda_id,
            user=current_user,
            page=page,
            size=size,
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception),
        ) from exception

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve EDA exports.",
        ) from exception


# ============================================================
# DOWNLOAD EXPORT
# ============================================================

@router.get(
    "/exports/{export_id}",
)
def download_export(
    export_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> Response:

    try:

        export = service.get_export(
            export_id=export_id,
            user=current_user,
        )

        if export is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Export with id "
                    f"'{export_id}' was not found."
                ),
            )

        return service.create_download_response(
            export
        )

    except HTTPException:

        raise

    except Exception as exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download export.",
        ) from exception