"""
EDA 02 — Free vs Paid Applications.

This module analyzes differences between free and paid
Google Play applications.

Responsibilities:
    - Retrieve free/paid statistics from PostgreSQL
    - Build a Pandas DataFrame
    - Calculate comparison statistics
    - Prepare visualization-ready data
    - Return a validated API response

Visualization generation is intentionally handled by
the export/visualization layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import text

from database import engine
from queries import GET_FREE_PAID_DISTRIBUTION
from schema.eda import (
    FreePaidStatistics,
    FreeVsPaidResponse,
)


class FreeVsPaidAnalysis:
    """
    Performs EDA 02: comparison between free and paid
    applications.
    """

    # ========================================================
    # PUBLIC API
    # ========================================================

    def run(self) -> FreeVsPaidResponse:
        """
        Execute the complete free-vs-paid analysis.

        Returns:
            Validated FreeVsPaidResponse.
        """

        dataframe = self._load_data()

        return self._build_response(dataframe)

    # ========================================================
    # DATA LOADING
    # ========================================================

    def _load_data(self) -> pd.DataFrame:
        """
        Load free/paid statistics from PostgreSQL.

        Returns:
            DataFrame containing free/paid statistics.
        """

        with engine.connect() as connection:

            dataframe = pd.read_sql(
                text(GET_FREE_PAID_DISTRIBUTION),
                connection,
            )

        return self._prepare_dataframe(
            dataframe
        )

    # ========================================================
    # DATA PREPARATION
    # ========================================================

    @staticmethod
    def _prepare_dataframe(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize the DataFrame returned by PostgreSQL.

        Args:
            dataframe:
                Raw PostgreSQL result.

        Returns:
            Clean analysis DataFrame.
        """

        if dataframe.empty:
            return dataframe

        dataframe = dataframe.copy()

        # ----------------------------------------------------
        # Normalize type
        # ----------------------------------------------------

        dataframe["type"] = (
            dataframe["type"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # ----------------------------------------------------
        # Numeric columns
        # ----------------------------------------------------

        numeric_columns = [
            "app_count",
            "rated_app_count",
            "average_rating",
            "median_rating",
            "average_reviews",
            "median_reviews",
            "total_reviews",
            "average_price",
            "minimum_price",
            "maximum_price",
        ]

        for column in numeric_columns:

            if column in dataframe.columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )

        # ----------------------------------------------------
        # Remove invalid application types
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["type"].isin(
                {"FREE", "PAID"}
            )
        ]

        # ----------------------------------------------------
        # Ensure predictable ordering
        # ----------------------------------------------------

        type_order = {
            "FREE": 0,
            "PAID": 1,
        }

        dataframe["_type_order"] = (
            dataframe["type"]
            .map(type_order)
        )

        dataframe = dataframe.sort_values(
            "_type_order"
        )

        dataframe = dataframe.drop(
            columns="_type_order"
        )

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
    ) -> FreeVsPaidResponse:
        """
        Build the validated API response.
        """

        analyzed_at = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------------
        # Empty dataset
        # ----------------------------------------------------

        if dataframe.empty:

            return FreeVsPaidResponse(
                analyzed_at=analyzed_at,
                free_applications=0,
                paid_applications=0,
                free_percentage=0.0,
                paid_percentage=0.0,
                average_rating_difference=None,
                average_reviews_difference=None,
                applications=[],
            )

        # ----------------------------------------------------
        # Application counts
        # ----------------------------------------------------

        free_applications = self._get_count(
            dataframe,
            "FREE",
        )

        paid_applications = self._get_count(
            dataframe,
            "PAID",
        )

        total_applications = (
            free_applications
            + paid_applications
        )

        # ----------------------------------------------------
        # Percentages
        # ----------------------------------------------------

        if total_applications > 0:

            free_percentage = (
                free_applications
                / total_applications
                * 100
            )

            paid_percentage = (
                paid_applications
                / total_applications
                * 100
            )

        else:

            free_percentage = 0.0
            paid_percentage = 0.0

        # ----------------------------------------------------
        # Average rating difference
        # ----------------------------------------------------

        free_rating = self._get_value(
            dataframe,
            "FREE",
            "average_rating",
        )

        paid_rating = self._get_value(
            dataframe,
            "PAID",
            "average_rating",
        )

        average_rating_difference = (
            self._difference(
                free_rating,
                paid_rating,
            )
        )

        # ----------------------------------------------------
        # Average reviews difference
        # ----------------------------------------------------

        free_reviews = self._get_value(
            dataframe,
            "FREE",
            "average_reviews",
        )

        paid_reviews = self._get_value(
            dataframe,
            "PAID",
            "average_reviews",
        )

        average_reviews_difference = (
            self._difference(
                free_reviews,
                paid_reviews,
            )
        )

        # ----------------------------------------------------
        # Detailed statistics
        # ----------------------------------------------------

        applications = [
            self._to_statistics(row)
            for _, row in dataframe.iterrows()
        ]

        return FreeVsPaidResponse(
            analyzed_at=analyzed_at,

            free_applications=(
                free_applications
            ),

            paid_applications=(
                paid_applications
            ),

            free_percentage=(
                self._round(
                    free_percentage
                )
            ),

            paid_percentage=(
                self._round(
                    paid_percentage
                )
            ),

            average_rating_difference=(
                self._round_optional(
                    average_rating_difference
                )
            ),

            average_reviews_difference=(
                self._round_optional(
                    average_reviews_difference
                )
            ),

            applications=applications,
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    @staticmethod
    def _get_count(
        dataframe: pd.DataFrame,
        application_type: str,
    ) -> int:
        """
        Retrieve the number of applications of a type.
        """

        rows = dataframe[
            dataframe["type"]
            == application_type
        ]

        if rows.empty:
            return 0

        value = rows.iloc[0]["app_count"]

        if pd.isna(value):
            return 0

        return int(value)

    @staticmethod
    def _get_value(
        dataframe: pd.DataFrame,
        application_type: str,
        column: str,
    ) -> float | None:
        """
        Retrieve a numerical value for an application type.
        """

        rows = dataframe[
            dataframe["type"]
            == application_type
        ]

        if rows.empty:
            return None

        value = rows.iloc[0][column]

        if pd.isna(value):
            return None

        return float(value)

    @staticmethod
    def _difference(
        first: float | None,
        second: float | None,
    ) -> float | None:
        """
        Calculate second - first.

        For example:

            paid average rating
            -
            free average rating
        """

        if first is None or second is None:
            return None

        return second - first

    # ========================================================
    # DATA MAPPING
    # ========================================================

    @staticmethod
    def _to_statistics(
        row: pd.Series,
    ) -> FreePaidStatistics:
        """
        Convert one DataFrame row into a Pydantic model.
        """

        return FreePaidStatistics(
            type=str(
                row["type"]
            ),

            app_count=int(
                row["app_count"]
            ),

            rated_app_count=int(
                row["rated_app_count"]
            ),

            average_rating=(
                FreeVsPaidAnalysis._safe_float(
                    row["average_rating"]
                )
            ),

            median_rating=(
                FreeVsPaidAnalysis._safe_float(
                    row["median_rating"]
                )
            ),

            average_reviews=(
                FreeVsPaidAnalysis._safe_float(
                    row["average_reviews"]
                )
            ),

            median_reviews=(
                FreeVsPaidAnalysis._safe_float(
                    row["median_reviews"]
                )
            ),

            total_reviews=int(
                row["total_reviews"]
            ),

            average_price=(
                FreeVsPaidAnalysis._safe_float(
                    row["average_price"]
                )
            ),

            minimum_price=(
                FreeVsPaidAnalysis._safe_float(
                    row["minimum_price"]
                )
            ),

            maximum_price=(
                FreeVsPaidAnalysis._safe_float(
                    row["maximum_price"]
                )
            ),
        )

    # ========================================================
    # VISUALIZATION DATA
    # ========================================================

    def get_visualization_dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return visualization-ready data.

        This DataFrame is intended for the export layer.

        Example visualizations:

            - Free vs Paid count
            - Free vs Paid percentage
            - Average rating comparison
            - Average review comparison
            - Paid application price distribution
        """

        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        visualization_dataframe = dataframe[
            [
                "type",
                "app_count",
                "rated_app_count",
                "average_rating",
                "median_rating",
                "average_reviews",
                "median_reviews",
                "total_reviews",
                "average_price",
                "minimum_price",
                "maximum_price",
            ]
        ].copy()

        # ----------------------------------------------------
        # Percentage
        # ----------------------------------------------------

        total = (
            visualization_dataframe[
                "app_count"
            ].sum()
        )

        if total > 0:

            visualization_dataframe[
                "percentage"
            ] = (
                visualization_dataframe[
                    "app_count"
                ]
                / total
                * 100
            )

        else:

            visualization_dataframe[
                "percentage"
            ] = 0.0

        # ----------------------------------------------------
        # Difference columns
        # ----------------------------------------------------

        visualization_dataframe[
            "rating_difference_from_free"
        ] = (
            visualization_dataframe[
                "average_rating"
            ]
            -
            visualization_dataframe.loc[
                visualization_dataframe["type"]
                == "FREE",
                "average_rating",
            ].iloc[0]
            if (
                "FREE"
                in visualization_dataframe[
                    "type"
                ].values
            )
            else None
        )

        return visualization_dataframe.reset_index(
            drop=True
        )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        """
        Safely convert a value to float.

        NaN values become None.
        """

        if value is None:
            return None

        try:

            converted = float(value)

            if pd.isna(converted):
                return None

            return converted

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _round(
        value: float,
        digits: int = 2,
    ) -> float:
        """
        Round a numerical result.
        """

        return round(
            float(value),
            digits,
        )

    @staticmethod
    def _round_optional(
        value: float | None,
        digits: int = 2,
    ) -> float | None:
        """
        Round an optional numerical result.
        """

        if value is None:
            return None

        return round(
            float(value),
            digits,
        )