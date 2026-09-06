"""
EDA 01 — Ratings by Category.

This module analyzes Google Play application ratings
grouped by application category.

Responsibilities:
    - Retrieve rating statistics from PostgreSQL
    - Build a Pandas DataFrame
    - Calculate global statistics
    - Prepare visualization-ready data
    - Return a validated API response

Visualization generation is intentionally kept outside
this module.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import text

from database import engine
from queries import GET_RATINGS_BY_CATEGORY
from schemas.eda import (
    RatingCategoryStatistics,
    RatingsByCategoryResponse,
)


class RatingsByCategoryAnalysis:
    """
    Performs EDA 01: ratings by application category.
    """

    # ========================================================
    # PUBLIC API
    # ========================================================

    def run(self) -> RatingsByCategoryResponse:
        """
        Execute the complete ratings-by-category analysis.

        Returns:
            Validated RatingsByCategoryResponse.
        """

        dataframe = self._load_data()

        return self._build_response(dataframe)

    # ========================================================
    # DATA LOADING
    # ========================================================

    def _load_data(self) -> pd.DataFrame:
        """
        Execute the PostgreSQL query and return the result
        as a Pandas DataFrame.

        Returns:
            DataFrame containing category-level rating statistics.
        """

        with engine.connect() as connection:

            dataframe = pd.read_sql(
                text(GET_RATINGS_BY_CATEGORY),
                connection,
            )

        return self._prepare_dataframe(dataframe)

    # ========================================================
    # DATA PREPARATION
    # ========================================================

    @staticmethod
    def _prepare_dataframe(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize the DataFrame returned by PostgreSQL.

        This method ensures that numerical columns have
        predictable Pandas types and removes invalid rows.

        Args:
            dataframe:
                Raw DataFrame returned by PostgreSQL.

        Returns:
            Clean visualization-ready DataFrame.
        """

        if dataframe.empty:
            return dataframe

        dataframe = dataframe.copy()

        # ----------------------------------------------------
        # Numeric columns
        # ----------------------------------------------------

        numeric_columns = [
            "app_count",
            "rated_app_count",
            "average_rating",
            "minimum_rating",
            "maximum_rating",
            "median_rating",
            "rating_stddev",
        ]

        for column in numeric_columns:

            if column in dataframe.columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )

        # ----------------------------------------------------
        # Remove invalid categories
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["category"]
            .notna()
        ]

        dataframe["category"] = (
            dataframe["category"]
            .astype(str)
            .str.strip()
        )

        dataframe = dataframe[
            dataframe["category"] != ""
        ]

        # ----------------------------------------------------
        # Remove rows without usable ratings
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["average_rating"]
            .notna()
        ]

        # ----------------------------------------------------
        # Sort by average rating
        # ----------------------------------------------------

        dataframe = dataframe.sort_values(
            by="average_rating",
            ascending=False,
        )

        # ----------------------------------------------------
        # Reset index for predictable API/export behavior
        # ----------------------------------------------------

        dataframe = dataframe.reset_index(
            drop=True
        )

        return dataframe

    # ========================================================
    # RESPONSE
    # ========================================================

    def _build_response(
        self,
        dataframe: pd.DataFrame,
    ) -> RatingsByCategoryResponse:
        """
        Build the API response from the DataFrame.
        """

        analyzed_at = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------------
        # Empty dataset
        # ----------------------------------------------------

        if dataframe.empty:

            return RatingsByCategoryResponse(
                analyzed_at=analyzed_at,
                total_categories=0,
                total_rated_applications=0,
                overall_average_rating=None,
                categories=[],
            )

        # ----------------------------------------------------
        # Global statistics
        # ----------------------------------------------------

        total_categories = len(dataframe)

        total_rated_applications = int(
            dataframe["rated_app_count"]
            .sum()
        )

        overall_average_rating = self._calculate_weighted_average(
            dataframe
        )

        # ----------------------------------------------------
        # Category statistics
        # ----------------------------------------------------

        categories = [
            RatingCategoryStatistics(
                category=str(row["category"]),

                app_count=int(
                    row["app_count"]
                ),

                rated_app_count=int(
                    row["rated_app_count"]
                ),

                average_rating=self._safe_float(
                    row["average_rating"]
                ),

                minimum_rating=self._safe_float(
                    row["minimum_rating"]
                ),

                maximum_rating=self._safe_float(
                    row["maximum_rating"]
                ),

                median_rating=self._safe_float(
                    row["median_rating"]
                ),

                rating_stddev=self._safe_float(
                    row["rating_stddev"]
                ),
            )

            for _, row in dataframe.iterrows()
        ]

        return RatingsByCategoryResponse(
            analyzed_at=analyzed_at,

            total_categories=(
                total_categories
            ),

            total_rated_applications=(
                total_rated_applications
            ),

            overall_average_rating=(
                overall_average_rating
            ),

            categories=categories,
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    @staticmethod
    def _calculate_weighted_average(
        dataframe: pd.DataFrame,
    ) -> float | None:
        """
        Calculate the overall rating using the number of
        rated applications as weights.

        This is more accurate than simply averaging the
        category averages because categories contain
        different numbers of applications.
        """

        valid_data = dataframe[
            dataframe["average_rating"]
            .notna()
            &
            dataframe["rated_app_count"]
            .notna()
        ]

        if valid_data.empty:
            return None

        total_ratings = (
            valid_data["average_rating"]
            *
            valid_data["rated_app_count"]
        ).sum()

        total_apps = (
            valid_data["rated_app_count"]
            .sum()
        )

        if total_apps == 0:
            return None

        return float(
            total_ratings / total_apps
        )

    # ========================================================
    # VISUALIZATION DATA
    # ========================================================

    def get_visualization_dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return a visualization-ready DataFrame.

        This method is used by the export/visualization
        layer when charts need to be generated.

        Returns:
            DataFrame containing category rating statistics.
        """

        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        return dataframe[
            [
                "category",
                "app_count",
                "rated_app_count",
                "average_rating",
                "minimum_rating",
                "maximum_rating",
                "median_rating",
                "rating_stddev",
            ]
        ].copy()

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        """
        Safely convert a value to float.

        NaN and infinite values are converted to None,
        which is appropriate for JSON/API responses.
        """

        if value is None:
            return None

        try:

            converted = float(value)

            if pd.isna(converted):
                return None

            if not pd.api.types.is_number(converted):
                return None

            return converted

        except (
            TypeError,
            ValueError,
        ):
            return None