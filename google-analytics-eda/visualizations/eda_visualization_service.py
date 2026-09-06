"""
Visualization data service.

This service converts CompleteEdaAnalysis objects into
pandas DataFrames.

It does not execute the EDA calculations.

It is used by the export layer to create:

    - CSV files
    - Excel files
    - PDF reports
    - charts

Visualization data is therefore created only when an
export is requested.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from schema.eda import CompleteEdaAnalysis


class EdaVisualizationService:
    """
    Converts EDA results into visualization-ready
    pandas DataFrames.
    """

    # ========================================================
    # ALL EDAs
    # ========================================================

    def build_all(
        self,
        analysis: CompleteEdaAnalysis,
    ) -> dict[str, pd.DataFrame]:
        """
        Build DataFrames for all four EDAs.
        """

        return {
            "ratings_by_category": (
                self.ratings_by_category(
                    analysis
                )
            ),

            "free_vs_paid": (
                self.free_vs_paid(
                    analysis
                )
            ),

            "install_distribution": (
                self.install_distribution(
                    analysis
                )
            ),

            "review_counts": (
                self.review_counts(
                    analysis
                )
            ),
        }

    # ========================================================
    # EDA 01
    # ========================================================

    @staticmethod
    def ratings_by_category(
        analysis: CompleteEdaAnalysis,
    ) -> pd.DataFrame:
        """
        DataFrame for ratings by category.
        """

        rows: list[dict[str, Any]] = []

        for item in (
            analysis
            .ratings_by_category
            .categories
        ):

            rows.append(
                {
                    "Category": item.category,
                    "App Count": item.app_count,
                    "Rated App Count": (
                        item.rated_app_count
                    ),
                    "Average Rating": (
                        item.average_rating
                    ),
                    "Minimum Rating": (
                        item.minimum_rating
                    ),
                    "Maximum Rating": (
                        item.maximum_rating
                    ),
                    "Median Rating": (
                        item.median_rating
                    ),
                    "Rating Std Dev": (
                        item.rating_stddev
                    ),
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "Category",
                "App Count",
                "Rated App Count",
                "Average Rating",
                "Minimum Rating",
                "Maximum Rating",
                "Median Rating",
                "Rating Std Dev",
            ],
        )

    # ========================================================
    # EDA 02
    # ========================================================

    @staticmethod
    def free_vs_paid(
        analysis: CompleteEdaAnalysis,
    ) -> pd.DataFrame:
        """
        DataFrame for free vs paid analysis.
        """

        rows: list[dict[str, Any]] = []

        for item in (
            analysis
            .free_vs_paid
            .applications
        ):

            rows.append(
                {
                    "Type": item.type,
                    "App Count": item.app_count,
                    "Rated App Count": (
                        item.rated_app_count
                    ),
                    "Average Rating": (
                        item.average_rating
                    ),
                    "Median Rating": (
                        item.median_rating
                    ),
                    "Average Reviews": (
                        item.average_reviews
                    ),
                    "Median Reviews": (
                        item.median_reviews
                    ),
                    "Total Reviews": (
                        item.total_reviews
                    ),
                    "Average Price": (
                        item.average_price
                    ),
                    "Minimum Price": (
                        item.minimum_price
                    ),
                    "Maximum Price": (
                        item.maximum_price
                    ),
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "Type",
                "App Count",
                "Rated App Count",
                "Average Rating",
                "Median Rating",
                "Average Reviews",
                "Median Reviews",
                "Total Reviews",
                "Average Price",
                "Minimum Price",
                "Maximum Price",
            ],
        )

    # ========================================================
    # EDA 03
    # ========================================================

    @staticmethod
    def install_distribution(
        analysis: CompleteEdaAnalysis,
    ) -> pd.DataFrame:
        """
        DataFrame for install distribution.
        """

        rows: list[dict[str, Any]] = []

        for item in (
            analysis
            .install_distribution
            .distribution
        ):

            rows.append(
                {
                    "Installs": item.installs,
                    "Installs Numeric": (
                        item.installs_numeric
                    ),
                    "App Count": item.app_count,
                    "Percentage": item.percentage,
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "Installs",
                "Installs Numeric",
                "App Count",
                "Percentage",
            ],
        )

    # ========================================================
    # EDA 04
    # ========================================================

    @staticmethod
    def review_counts(
        analysis: CompleteEdaAnalysis,
    ) -> pd.DataFrame:
        """
        DataFrame for review count analysis.
        """

        rows: list[dict[str, Any]] = []

        for item in (
            analysis
            .review_counts
            .categories
        ):

            rows.append(
                {
                    "Category": item.category,
                    "App Count": item.app_count,
                    "Average Reviews": (
                        item.average_reviews
                    ),
                    "Median Reviews": (
                        item.median_reviews
                    ),
                    "Total Reviews": (
                        item.total_reviews
                    ),
                    "Maximum Reviews": (
                        item.maximum_reviews
                    ),
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "Category",
                "App Count",
                "Average Reviews",
                "Median Reviews",
                "Total Reviews",
                "Maximum Reviews",
            ],
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def build_summary(
        analysis: CompleteEdaAnalysis,
    ) -> pd.DataFrame:
        """
        Build a summary DataFrame containing the
        most important global statistics.
        """

        return pd.DataFrame(
            [
                {
                    "Analysis Date": (
                        analysis.analysis_date
                    ),

                    "Total Categories": (
                        analysis
                        .ratings_by_category
                        .total_categories
                    ),

                    "Total Rated Applications": (
                        analysis
                        .ratings_by_category
                        .total_rated_applications
                    ),

                    "Overall Average Rating": (
                        analysis
                        .ratings_by_category
                        .overall_average_rating
                    ),

                    "Free Applications": (
                        analysis
                        .free_vs_paid
                        .free_applications
                    ),

                    "Paid Applications": (
                        analysis
                        .free_vs_paid
                        .paid_applications
                    ),

                    "Free Percentage": (
                        analysis
                        .free_vs_paid
                        .free_percentage
                    ),

                    "Paid Percentage": (
                        analysis
                        .free_vs_paid
                        .paid_percentage
                    ),

                    "Total Applications": (
                        analysis
                        .install_distribution
                        .total_applications
                    ),

                    "Total Installs": (
                        analysis
                        .install_distribution
                        .total_installs
                    ),

                    "Average Installs": (
                        analysis
                        .install_distribution
                        .average_installs
                    ),

                    "Median Installs": (
                        analysis
                        .install_distribution
                        .median_installs
                    ),

                    "Total Reviews": (
                        analysis
                        .review_counts
                        .statistics
                        .total_reviews
                    ),

                    "Average Reviews": (
                        analysis
                        .review_counts
                        .statistics
                        .average_reviews
                    ),

                    "Median Reviews": (
                        analysis
                        .review_counts
                        .statistics
                        .median_reviews
                    ),
                }
            ]
        )