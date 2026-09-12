from __future__ import annotations

from datetime import datetime, timezone

from elastic.eda_repository import EdaRepository
from elastic.export_repository import ExportRepository
from schema.eda_document import EdaDocument
from schema.eda_page import EdaPage
from security.keycloak import KeycloakUser
from services.eda_service import EdaAnalysisService


class EdaManagementService:

    def __init__(
        self,
        analysis_service: EdaAnalysisService | None = None,
        eda_repository: EdaRepository | None = None,
        export_repository: ExportRepository | None = None,
    ) -> None:

        self._analysis_service = (
            analysis_service
            or EdaAnalysisService()
        )

        self._eda_repository = (
            eda_repository
            or EdaRepository()
        )

        self._export_repository = (
            export_repository
            or ExportRepository()
        )

    # ============================================================
    # RUN + SAVE
    # ============================================================

    def run_and_save(
        self,
        user: KeycloakUser,
    ) -> EdaDocument:

        analysis = self._analysis_service.run()

        document = EdaDocument(
            email=user.email,
            date=datetime.now(timezone.utc),
            ratings_by_category=(
                analysis.ratings_by_category
            ),
            free_vs_paid=(
                analysis.free_vs_paid
            ),
            install_distribution=(
                analysis.install_distribution
            ),
            review_counts=(
                analysis.review_counts
            ),
        )

        eda_id = self._eda_repository.save(
            document
        )

        return document.model_copy(
            update={
                "eda_id": eda_id
            }
        )

    # ============================================================
    # GET BY ID
    # ============================================================

    def get_by_id(
        self,
        eda_id: str,
        user: KeycloakUser,
    ) -> EdaDocument | None:

        if self._is_admin(user):

            return self._eda_repository.find_by_id(
                eda_id
            )

        return (
            self._eda_repository.find_by_id_and_email(
                eda_id=eda_id,
                email=user.email,
            )
        )

    # ============================================================
    # GET HISTORY
    # ============================================================

    def get_history(
        self,
        user: KeycloakUser,
        page: int = 0,
        size: int = 20,
    ) -> EdaPage:

        if self._is_admin(user):

            result = self._eda_repository.find_all(
                page=page,
                size=size,
            )

        else:

            result = (
                self._eda_repository.find_all_by_email(
                    email=user.email,
                    page=page,
                    size=size,
                )
            )

        return EdaPage(
            content=result["content"],
            page=result["page"],
            size=result["size"],
            total_elements=result[
                "total_elements"
            ],
            total_pages=result[
                "total_pages"
            ],
        )

    # ============================================================
    # DELETE
    # ============================================================

    def delete(
        self,
        eda_id: str,
        user: KeycloakUser,
    ) -> bool:

        # --------------------------------------------------------
        # ADMIN
        # --------------------------------------------------------

        if self._is_admin(user):

            eda = self._eda_repository.find_by_id(
                eda_id
            )

        # --------------------------------------------------------
        # USER
        # --------------------------------------------------------

        else:

            eda = (
                self._eda_repository.find_by_id_and_email(
                    eda_id=eda_id,
                    email=user.email,
                )
            )

        # --------------------------------------------------------
        # EDA does not exist OR user does not own it
        # --------------------------------------------------------

        if eda is None:

            return False

        # --------------------------------------------------------
        # Delete all exports belonging to the EDA
        # --------------------------------------------------------

        self._export_repository.delete_by_eda_id(
            eda_id
        )

        # --------------------------------------------------------
        # Delete EDA
        # --------------------------------------------------------

        return self._eda_repository.delete(
            eda_id
        )

    # ============================================================
    # COUNT
    # ============================================================

    def count(
        self,
        user: KeycloakUser,
    ) -> int:

        if self._is_admin(user):

            return self._eda_repository.count()

        return self._eda_repository.count_by_email(
            user.email
        )

    # ============================================================
    # ADMIN CHECK
    # ============================================================

    @staticmethod
    def _is_admin(
        user: KeycloakUser,
    ) -> bool:

        return "ADMIN" in user.roles