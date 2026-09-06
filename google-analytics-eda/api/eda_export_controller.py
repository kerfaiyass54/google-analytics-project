"""
EDA Export API.

This module exposes HTTP endpoints for:

    - Generating EDA exports
    - Listing user's export history
    - Retrieving an export
    - Downloading an export
    - Deleting an export history record

Authentication:
    Keycloak JWT.

Important security rule:
    The user's email is NEVER accepted from the request body
    or query parameters.

    It is extracted from the authenticated Keycloak token.

Architecture:

    Angular
       |
       | Bearer JWT
       v
    FastAPI
       |
       v
    EdaExportController
       |
       v
    EdaExportService
       |
       +---- PostgreSQL
       |
       +---- Elasticsearch
       |
       +---- File system
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path as FastAPIPath,
    Query,
    status,
)
from fastapi.responses import FileResponse

from elastic.export_repository import ExportRepository
from schema.eda import ExportRecord, ExportPage
from services.eda_export_service import (
    EdaExportService,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/eda/exports",
    tags=["EDA Exports"],
)


# ============================================================
# CONSTANTS
# ============================================================

EXPORT_DIRECTORY = Path(
    "exports"
)


SUPPORTED_FORMATS = {
    "csv",
    "xlsx",
    "pdf",
}


# ============================================================
# DEPENDENCIES
# ============================================================

def get_export_service() -> EdaExportService:
    """
    Create the EDA export service.

    Keeping dependency creation in one place makes the API
    easier to test and allows dependency overrides.
    """

    return EdaExportService()


def get_export_repository() -> ExportRepository:
    """
    Create the Elasticsearch export repository.
    """

    return ExportRepository()


# ------------------------------------------------------------
# Replace this dependency with your Keycloak JWT dependency.
# ------------------------------------------------------------

def get_current_user_email() -> str:
    """
    Return the authenticated user's email.

    This function is intentionally kept as a dependency
    boundary.

    It MUST be replaced by the application's real
    Keycloak JWT validation dependency.

    The dependency should:

        1. Read Authorization: Bearer <token>
        2. Validate the JWT signature
        3. Validate issuer
        4. Validate audience
        5. Validate expiration
        6. Extract the email claim

    It must raise HTTP 401 when the token is invalid.
    """

    raise NotImplementedError(
        "Configure the Keycloak JWT dependency."
    )


# ============================================================
# TYPE ALIASES
# ============================================================

CurrentUserEmail = Annotated[
    str,
    Depends(
        get_current_user_email
    ),
]


ExportService = Annotated[
    EdaExportService,
    Depends(
        get_export_service
    ),
]


ExportRepo = Annotated[
    ExportRepository,
    Depends(
        get_export_repository
    ),
]


# ============================================================
# CREATE EXPORT
# ============================================================

@router.post(
    "/{file_format}",
    response_model=ExportRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an EDA export",
    description=(
        "Execute the four EDAs and generate a CSV, XLSX "
        "or PDF report."
    ),
)
def create_export(
    file_format: Literal[
        "csv",
        "xlsx",
        "pdf",
    ],
    current_user_email: CurrentUserEmail,
    service: ExportService,
) -> ExportRecord:
    """
    Generate a complete Google Play Store EDA export.

    The authenticated user's email is obtained from Keycloak.

    Supported formats:

        POST /api/eda/exports/csv
        POST /api/eda/exports/xlsx
        POST /api/eda/exports/pdf
    """

    try:

        return service.export(
            email=current_user_email,
            file_format=file_format,
            output_directory=EXPORT_DIRECTORY,
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
                "The EDA export could not be generated."
            ),
        ) from exception


# ============================================================
# LIST MY EXPORTS
# ============================================================

@router.get(
    "",
    response_model=ExportPage,
    summary="Get my export history",
)
def get_my_exports(
    current_user_email: CurrentUserEmail,
    repository: ExportRepo,
    page: int = Query(
        default=0,
        ge=0,
        description="Zero-based page number.",
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of exports per page.",
    ),
) -> ExportPage:
    """
    Retrieve the authenticated user's export history.

    Results are sorted by export date descending.
    """

    try:

        result = (
            repository.find_by_email(
                email=current_user_email,
                page=page,
                size=size,
            )
        )

        return ExportPage(
            **result
        )

    except ValueError as exception:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception


# ============================================================
# GET MY EXPORT
# ============================================================

@router.get(
    "/{export_id}",
    response_model=ExportRecord,
    summary="Get an export",
)
def get_my_export(
    export_id: str = FastAPIPath(
        ...,
        min_length=1,
    ),
    current_user_email: CurrentUserEmail = None,
    repository: ExportRepo = None,
) -> ExportRecord:
    """
    Retrieve one export belonging to the authenticated user.

    An export belonging to another user is intentionally
    returned as HTTP 404 rather than HTTP 403.

    This prevents leaking the existence of another user's
    export IDs.
    """

    record = (
        repository.find_by_id(
            export_id
        )
    )

    if record is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if record.email.lower() != (
        current_user_email.strip().lower()
    ):

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    return record


# ============================================================
# DOWNLOAD EXPORT
# ============================================================

@router.get(
    "/{export_id}/download",
    response_class=FileResponse,
    summary="Download an export",
)
def download_export(
    export_id: str = FastAPIPath(
        ...,
        min_length=1,
    ),
    current_user_email: CurrentUserEmail = None,
    repository: ExportRepo = None,
):
    """
    Download an export belonging to the authenticated user.

    Security:

        - Elasticsearch record must exist.
        - Record must belong to current user.
        - Filename is resolved inside EXPORT_DIRECTORY.
        - Path traversal is explicitly prevented.
    """

    record = (
        repository.find_by_id(
            export_id
        )
    )

    # --------------------------------------------------------
    # Do not expose existence of another user's export.
    # --------------------------------------------------------

    if record is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    if record.email.lower() != (
        current_user_email.strip().lower()
    ):

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    # --------------------------------------------------------
    # Resolve filename safely
    # --------------------------------------------------------

    filename = Path(
        record.filename
    ).name

    file_path = (
        EXPORT_DIRECTORY / filename
    ).resolve()

    export_directory = (
        EXPORT_DIRECTORY
        .resolve()
    )

    # --------------------------------------------------------
    # Path traversal protection
    # --------------------------------------------------------

    try:

        file_path.relative_to(
            export_directory
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid export filename.",
        )

    # --------------------------------------------------------
    # Check physical file
    # --------------------------------------------------------

    if not file_path.is_file():

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The export file is no longer available."
            ),
        )

    # --------------------------------------------------------
    # Determine media type
    # --------------------------------------------------------

    media_types = {
        ".csv": "text/csv",
        ".xlsx": (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        ".pdf": "application/pdf",
    }

    media_type = (
        media_types.get(
            file_path.suffix.lower()
        )
        or "application/octet-stream"
    )

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )


# ============================================================
# DELETE EXPORT
# ============================================================

@router.delete(
    "/{export_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an export history record",
)
def delete_export(
    export_id: str = FastAPIPath(
        ...,
        min_length=1,
    ),
    current_user_email: CurrentUserEmail = None,
    repository: ExportRepo = None,
) -> None:
    """
    Delete an export history record belonging to the user.

    IMPORTANT:

        This removes the Elasticsearch metadata.

        It does NOT remove the physical file.

    Physical file deletion should be handled separately
    if/when required.
    """

    record = (
        repository.find_by_id(
            export_id
        )
    )

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    if record is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    # --------------------------------------------------------
    # Ownership
    # --------------------------------------------------------

    if record.email.lower() != (
        current_user_email.strip().lower()
    ):

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )

    # --------------------------------------------------------
    # Delete metadata
    # --------------------------------------------------------

    deleted = (
        repository.delete(
            export_id
        )
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found.",
        )