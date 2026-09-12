from __future__ import annotations

from datetime import datetime, timezone

from analysis.free_vs_paid import FreeVsPaidAnalysis
from analysis.install_distribution import InstallDistributionAnalysis
from analysis.ratings_by_category import RatingsByCategoryAnalysis
from analysis.review_counts import ReviewCountsAnalysis
from schema.eda import CompleteEdaAnalysis


class EdaAnalysisService:

    def __init__(
        self,
        ratings_analysis: RatingsByCategoryAnalysis | None = None,
        free_paid_analysis: FreeVsPaidAnalysis | None = None,
        install_analysis: InstallDistributionAnalysis | None = None,
        review_analysis: ReviewCountsAnalysis | None = None,
    ) -> None:

        self._ratings_analysis = (
            ratings_analysis
            or RatingsByCategoryAnalysis()
        )

        self._free_paid_analysis = (
            free_paid_analysis
            or FreeVsPaidAnalysis()
        )

        self._install_analysis = (
            install_analysis
            or InstallDistributionAnalysis()
        )

        self._review_analysis = (
            review_analysis
            or ReviewCountsAnalysis()
        )

    # ============================================================
    # COMPLETE EDA
    # ============================================================

    def run(self) -> CompleteEdaAnalysis:

        ratings_by_category = (
            self.run_ratings_by_category()
        )

        free_vs_paid = (
            self.run_free_vs_paid()
        )

        install_distribution = (
            self.run_install_distribution()
        )

        review_counts = (
            self.run_review_counts()
        )

        return CompleteEdaAnalysis(
            analysis_date=self._get_current_timestamp(),
            ratings_by_category=ratings_by_category,
            free_vs_paid=free_vs_paid,
            install_distribution=install_distribution,
            review_counts=review_counts,
        )

    # ============================================================
    # RATINGS BY CATEGORY
    # ============================================================

    def run_ratings_by_category(self) -> dict:

        return self._ratings_analysis.run()

    # ============================================================
    # FREE VS PAID
    # ============================================================

    def run_free_vs_paid(self) -> dict:

        return self._free_paid_analysis.run()

    # ============================================================
    # INSTALL DISTRIBUTION
    # ============================================================

    def run_install_distribution(self) -> dict:

        return self._install_analysis.run()

    # ============================================================
    # REVIEW COUNTS
    # ============================================================

    def run_review_counts(self) -> dict:

        return self._review_analysis.run()

    # ============================================================
    # CURRENT TIMESTAMP
    # ============================================================

    @staticmethod
    def _get_current_timestamp() -> datetime:

        return datetime.now(
            timezone.utc
        )