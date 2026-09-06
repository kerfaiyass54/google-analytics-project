"""
Application service responsible for executing EDAs
and persisting complete analyses in Elasticsearch.
"""

from __future__ import annotations

from services.eda_service import EdaAnalysisService
from elastic.analysis_repository import AnalysisRepository
from schema.eda import (
    CompleteEdaAnalysis,
    EdaAnalysisPage,
)


class EdaPersistenceService:
    """
    Coordinates EDA execution and Elasticsearch persistence.
    """

    def __init__(
        self,
        analysis_service: EdaAnalysisService | None = None,
        analysis_repository: AnalysisRepository | None = None,
    ) -> None:

        self._analysis_service = (
            analysis_service
            or EdaAnalysisService()
        )

        self._analysis_repository = (
            analysis_repository
            or AnalysisRepository()
        )

    # ========================================================
    # RUN + SAVE
    # ========================================================

    def run_and_save(
        self,
    ) -> CompleteEdaAnalysis:
        """
        Execute all four EDAs and persist the result.
        """

        analysis = (
            self._analysis_service.run()
        )

        analysis_id = (
            self._analysis_repository.save(
                analysis
            )
        )

        return analysis.model_copy(
            update={
                "analysis_id": analysis_id,
            }
        )

    # ========================================================
    # RUN ONLY
    # ========================================================

    def run(
        self,
    ) -> CompleteEdaAnalysis:
        """
        Execute the analysis without persisting it.
        """

        return (
            self._analysis_service.run()
        )

    # ========================================================
    # DETAILS
    # ========================================================

    def get_by_id(
        self,
        analysis_id: str,
    ) -> CompleteEdaAnalysis | None:
        """
        Retrieve one stored analysis.
        """

        return (
            self._analysis_repository.find_by_id(
                analysis_id
            )
        )

    # ========================================================
    # LATEST
    # ========================================================

    def get_latest(
        self,
    ) -> CompleteEdaAnalysis | None:
        """
        Retrieve the latest stored analysis.
        """

        return (
            self._analysis_repository.find_latest()
        )

    # ========================================================
    # HISTORY
    # ========================================================

    def get_history(
        self,
        page: int = 0,
        size: int = 20,
    ) -> EdaAnalysisPage:
        """
        Retrieve paginated analysis history.
        """

        result = (
            self._analysis_repository.find_all(
                page=page,
                size=size,
            )
        )

        return EdaAnalysisPage(
            content=[
                CompleteEdaAnalysis.model_validate(
                    item
                )
                for item in result["content"]
            ],
            page=result["page"],
            size=result["size"],
            total_elements=result[
                "total_elements"
            ],
            total_pages=result[
                "total_pages"
            ],
        )

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return the number of stored analyses.
        """

        return (
            self._analysis_repository.count()
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        analysis_id: str,
    ) -> bool:
        """
        Delete one analysis.
        """

        return (
            self._analysis_repository.delete(
                analysis_id
            )
        )