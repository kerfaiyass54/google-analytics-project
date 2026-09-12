from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from schema.export_page import ExportPage
from schema.export_response import ExportResponse

from security.keycloak import (
    KeycloakUser,
    get_current_user,
)

from services.eda_export_service import EdaExportService


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
# CREATE JSON EXPORT
# ============================================================

@router.post(
    "/{eda_id}/exports/json",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
def export_json(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> ExportResponse:

    try:

        return service.export_json(
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
            detail="Failed to create JSON export.",
        ) from exception


# ============================================================
# CREATE CSV EXPORT
# ============================================================

@router.post(
    "/{eda_id}/exports/csv",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
def export_csv(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> ExportResponse:

    try:

        return service.export_csv(
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
            detail="Failed to create CSV export.",
        ) from exception


# ============================================================
# CREATE PDF EXPORT
# ============================================================

@router.post(
    "/{eda_id}/exports/pdf",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
def export_pdf(
    eda_id: str,
    current_user: CurrentUser,
    service: EdaExportServiceDependency,
) -> ExportResponse:

    try:

        return service.export_pdf(
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
            detail="Failed to create PDF export.",
        ) from exception


# ============================================================
# GET EXPORT HISTORY
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