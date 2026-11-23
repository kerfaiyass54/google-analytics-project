from __future__ import annotations

from datetime import datetime, timezone

from elastic.eda_repository import EdaRepository
from elastic.export_repository import ExportRepository
from schema.eda_document import EdaDocument
from schema.export_document import ExportDocument
from schema.eda_page import EdaPage
from config import get_keycloak_config
from security.keycloak import KeycloakUser
from services.eda_service import EdaAnalysisService
from services.notification_event_publisher import publish_notification_event


class EdaManagementService:

    def __init__(
        self,
        analysis_service: EdaAnalysisService | None = None,
        eda_repository: EdaRepository | None = None,
        export_repository: ExportRepository | None = None,
    ) -> None:
        self._analysis_service = analysis_service or EdaAnalysisService()
        self._eda_repository = eda_repository or EdaRepository()
        self._export_repository = export_repository or ExportRepository()

    def run_and_save(self, user: KeycloakUser) -> EdaDocument:
        analysis = self._analysis_service.run()
        document = EdaDocument(
            email=user.email,
            date=datetime.now(timezone.utc),
            ratings_by_category=analysis.ratings_by_category,
            free_vs_paid=analysis.free_vs_paid,
            install_distribution=analysis.install_distribution,
            review_counts=analysis.review_counts,
        )
        eda_id = self._eda_repository.save(document)
        publish_notification_event(
            "EDA_CREATED",
            entity_type="EDA",
            entity_id=str(eda_id),
            entity_name="EDA analysis",
            payload={"creator": user.email},
        )
        return document.model_copy(update={"eda_id": eda_id})

    def get_by_id(self, eda_id: str, user: KeycloakUser) -> EdaDocument | None:
        if self._is_admin(user):
            return self._eda_repository.find_by_id(eda_id)
        return self._eda_repository.find_by_id_and_email(eda_id=eda_id, email=user.email)

    def get_history(
        self,
        user: KeycloakUser,
        page: int = 0,
        size: int = 20,
        eda_id: str | None = None,
        creator_email: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        metric_filters: dict[str, dict[str, float]] | None = None,
    ) -> EdaPage:
        # Non-admin users can only search their own history. Admins may
        # optionally narrow the search to a creator email.
        email_filter = creator_email if self._is_admin(user) else user.email
        result = self._eda_repository.find_filtered(
            page=page,
            size=size,
            eda_id=eda_id,
            email=email_filter,
            date_from=date_from,
            date_to=date_to,
            search=search,
            metric_filters=metric_filters,
        )
        return EdaPage(
            content=result["content"],
            page=result["page"],
            size=result["size"],
            total_elements=result["total_elements"],
            total_pages=result["total_pages"],
        )

    def delete(self, eda_id: str, user: KeycloakUser) -> bool:
        if self._is_admin(user):
            eda = self._eda_repository.find_by_id(eda_id)
        else:
            eda = self._eda_repository.find_by_id_and_email(eda_id=eda_id, email=user.email)

        if eda is None:
            return False

        exports_snapshot = self._load_all_exports(eda_id)
        deleted = self._eda_repository.delete(eda_id)
        if not deleted:
            return False

        try:
            self._export_repository.delete_by_eda_id(eda_id)
            return True
        except Exception as exception:
            self._rollback_delete(eda_id=eda_id, eda=eda, exports=exports_snapshot)
            raise RuntimeError(
                "Failed to delete exports. EDA deletion has been rolled back."
            ) from exception

    def _load_all_exports(self, eda_id: str) -> list[ExportDocument]:
        page = 0
        size = 200
        exports: list[ExportDocument] = []
        while True:
            result = self._export_repository.find_by_eda_id(
                eda_id=eda_id, page=page, size=size
            )
            exports.extend(result["content"])
            if page + 1 >= result["total_pages"]:
                break
            page += 1
        return exports

    def _rollback_delete(
        self,
        eda_id: str,
        eda: EdaDocument,
        exports: list[ExportDocument],
    ) -> None:
        self._eda_repository.save_with_id(eda_id=eda_id, eda=eda)
        for export in exports:
            if export.export_id is None:
                raise RuntimeError("Cannot rollback export without id.")
            self._export_repository.save_with_id(
                export_id=export.export_id, export=export
            )

    def count(self, user: KeycloakUser) -> int:
        if self._is_admin(user):
            return self._eda_repository.count()
        return self._eda_repository.count_by_email(user.email)

    @staticmethod
    def _is_admin(user: KeycloakUser) -> bool:
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
