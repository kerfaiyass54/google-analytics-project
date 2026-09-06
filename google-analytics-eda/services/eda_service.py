"""
Main EDA orchestration service.

Executes the four Google Play Store EDAs:

    1. Ratings by Category
    2. Free vs Paid
    3. Install Distribution
    4. Review Counts

The service is responsible only for orchestration.

It does not:
    - access Elasticsearch
    - generate files
    - generate charts
    - handle HTTP requests
"""

from __future__ import annotations

from analysis.free_vs_paid import FreeVsPaidAnalysis
from analysis.install_distribution import (
    InstallDistributionAnalysis,
)
from analysis.ratings_by_category import (
    RatingsByCategoryAnalysis,
)
from analysis.review_counts import (
    ReviewCountsAnalysis,
)
from schema.eda import CompleteEdaAnalysis


class EdaAnalysisService:
    """
    Orchestrates the four individual EDA analyses.
    """

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

    # ========================================================
    # COMPLETE ANALYSIS
    # ========================================================

    def run(self) -> CompleteEdaAnalysis:
        """
        Execute all four EDAs.

        Returns:
            CompleteEdaAnalysis
        """

        ratings_by_category = (
            self._ratings_analysis.run()
        )

        free_vs_paid = (
            self._free_paid_analysis.run()
        )

        install_distribution = (
            self._install_analysis.run()
        )

        review_counts = (
            self._review_analysis.run()
        )

        return CompleteEdaAnalysis(
            analysis_date=self._get_current_timestamp(),

            ratings_by_category=(
                ratings_by_category
            ),

            free_vs_paid=(
                free_vs_paid
            ),

            install_distribution=(
                install_distribution
            ),

            review_counts=(
                review_counts
            ),
        )

    # ========================================================
    # INDIVIDUAL EDAs
    # ========================================================

    def run_ratings_by_category(self):
        """
        Execute EDA 01 only.
        """

        return (
            self._ratings_analysis.run()
        )

    def run_free_vs_paid(self):
        """
        Execute EDA 02 only.
        """

        return (
            self._free_paid_analysis.run()
        )

    def run_install_distribution(self):
        """
        Execute EDA 03 only.
        """

        return (
            self._install_analysis.run()
        )

    def run_review_counts(self):
        """
        Execute EDA 04 only.
        """

        return (
            self._review_analysis.run()
        )

    # ========================================================
    # PRIVATE
    # ========================================================

    @staticmethod
    def _get_current_timestamp():
        """
        Return the current UTC timestamp.
        """

        from datetime import datetime, timezone

        return datetime.now(
            timezone.utc
        )