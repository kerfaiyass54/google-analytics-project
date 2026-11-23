from __future__ import annotations

import base64
import json
from datetime import datetime, timezone

from fastapi import Response

from elastic.eda_repository import EdaRepository
from elastic.export_repository import ExportRepository

from export.pdf_exporter import ChartZipExporter
from export.excel_exporter import ExcelExporter

from schema.eda_document import EdaDocument
from schema.export_document import ExportDocument
from schema.export_page import ExportPage
from schema.export_response import ExportResponse

from config import get_keycloak_config
from security.keycloak import KeycloakUser


class EdaExportService:

    def __init__(
        self,
        eda_repository: EdaRepository | None = None,
        export_repository: ExportRepository | None = None,
    ) -> None:

        self._eda_repository = (
            eda_repository
            or EdaRepository()
        )

        self._export_repository = (
            export_repository
            or ExportRepository()
        )

    # ============================================================
    # EXPORT EXCEL
    # ============================================================

    def export_excel(
        self,
        eda_id: str,
        user: KeycloakUser,
    ) -> Response:

        eda = self._get_accessible_eda(
            eda_id,
            user,
        )

        content = ExcelExporter.export(eda)

        return self._save_export(
            eda_id=eda_id,
            email=user.email,
            file_type="xlsx",
            filename=f"eda-{eda_id}.xlsx",
            content=content,
        )

    # ============================================================
    # EXPORT CHART ZIP
    # ============================================================

    def export_charts_zip(
        self,
        eda_id: str,
        user: KeycloakUser,
    ) -> Response:

        eda = self._get_accessible_eda(
            eda_id,
            user,
        )

        content = ChartZipExporter.export(eda)

        return self._save_export(
            eda_id=eda_id,
            email=user.email,
            file_type="zip",
            filename=f"eda-charts-{eda_id}.zip",
            content=content,
        )

    # ============================================================
    # GET EXPORT HISTORY FOR ONE EDA
    # ============================================================

    def get_exports(
        self,
        eda_id: str,
        user: KeycloakUser,
        page: int = 0,
        size: int = 20,
    ) -> ExportPage:

        self._get_accessible_eda(
            eda_id,
            user,
        )

        if self._is_admin(user):

            result = (
                self._export_repository.find_by_eda_id(
                    eda_id=eda_id,
                    page=page,
                    size=size,
                )
            )

        else:

            result = (
                self._export_repository
                .find_by_eda_id_and_email(
                    eda_id=eda_id,
                    email=user.email,
                    page=page,
                    size=size,
                )
            )

        return self._to_export_page(result)

    # ============================================================
    # GET CURRENT USER EXPORT HISTORY
    # ============================================================

    def get_exports_by_email(
        self,
        email: str,
        page: int = 0,
        size: int = 20,
    ) -> ExportPage:

        result = (
            self._export_repository.find_by_email(
                email=email,
                page=page,
                size=size,
            )
        )

        return self._to_export_page(result)

    # ============================================================
    # GET EXPORT
    # ============================================================

    def get_export(
        self,
        export_id: str,
        user: KeycloakUser,
    ) -> ExportDocument | None:

        if self._is_admin(user):

            return (
                self._export_repository.find_by_id(
                    export_id
                )
            )

        return (
            self._export_repository
            .find_by_id_and_email(
                export_id=export_id,
                email=user.email,
            )
        )

    # ============================================================
    # CREATE DOWNLOAD RESPONSE
    # ============================================================

    @staticmethod
    def create_download_response(
        export: ExportDocument,
    ) -> Response:

        content = base64.b64decode(
            export.content
        )

        media_types = {
            "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            "zip": "application/zip",
            "xlsx": (
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        }

        media_type = media_types.get(
            export.file_type.lower(),
            "application/octet-stream",
        )

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; '
                    f'filename="{export.filename}"'
                )
            },
        )

    # ============================================================
    # SAVE EXPORT
    # ============================================================

    def _save_export(
        self,
        eda_id: str,
        email: str,
        file_type: str,
        filename: str,
        content: bytes,
    ) -> Response:

        encoded_content = (
            base64.b64encode(content)
            .decode("ascii")
        )

        document = ExportDocument(
            eda_id=eda_id,
            email=email,
            date=datetime.now(timezone.utc),
            file_type=file_type,
            filename=filename,
            content=encoded_content,
        )

        self._export_repository.save(document)

        media_types = {
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "zip": "application/zip",
        }

        return Response(
            content=content,
            media_type=media_types.get(
                file_type,
                "application/octet-stream",
            ),
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            },
            status_code=201,
        )

    # ============================================================
    # GET ACCESSIBLE EDA
    # ============================================================

    def _get_accessible_eda(
        self,
        eda_id: str,
        user: KeycloakUser,
    ) -> EdaDocument:

        if self._is_admin(user):

            eda = (
                self._eda_repository.find_by_id(
                    eda_id
                )
            )

        else:

            eda = (
                self._eda_repository
                .find_by_id_and_email(
                    eda_id=eda_id,
                    email=user.email,
                )
            )

        if eda is None:

            raise ValueError(
                f"EDA with id '{eda_id}' "
                "was not found."
            )

        return eda

    # ============================================================
    # ADMIN CHECK
    # ============================================================

    @staticmethod
    def _is_admin(
        user: KeycloakUser,
    ) -> bool:

        config = get_keycloak_config()
        role_source = config.admin_role_source.lower()

        if role_source == "realm":
            return config.admin_role in user.realm_roles
        if role_source == "both":
            return (
                config.admin_role in user.realm_roles
                or config.admin_role in user.client_roles
            )
        return config.admin_role in user.client_roles

    # ============================================================
    # CONVERT REPOSITORY RESULT TO PAGE
    # ============================================================

    @staticmethod
    def _to_export_page(
        result: dict,
    ) -> ExportPage:

        metadata = [
            ExportResponse(
                export_id=export.export_id,
                eda_id=export.eda_id,
                email=export.email,
                date=export.date,
                file_type=export.file_type,
                filename=export.filename,
            )
            for export in result["content"]
        ]

        return ExportPage(
            content=metadata,
            page=result["page"],
            size=result["size"],
            total_elements=result["total_elements"],
            total_pages=result["total_pages"],
        )

    # ============================================================
    # JSON CONTENT
    # ============================================================

    @staticmethod
    def _create_json_content(
        eda: EdaDocument,
    ) -> bytes:

        data = eda.model_dump(mode="json")

        data.pop("eda_id", None)

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ).encode("utf-8")