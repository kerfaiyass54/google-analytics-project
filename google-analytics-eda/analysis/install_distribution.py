"""
EDA 03 — Install Distribution.

Analyzes the distribution of Google Play application
install counts.

Responsibilities:
    - Retrieve install statistics from PostgreSQL
    - Convert install strings to numeric values
    - Build a Pandas DataFrame
    - Calculate global statistics
    - Analyze installations by category
    - Identify top-installed applications
    - Prepare visualization-ready data
    - Return a validated API response

The original Installs value is preserved for presentation,
while installs_numeric is used for calculations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import text

from database import engine
from queries import GET_INSTALL_DISTRIBUTION
from schema.eda import (
    InstallCategoryStatistics,
    InstallDistributionItem,
    InstallDistributionResponse,
    TopInstalledApplication,
)


class InstallDistributionAnalysis:
    """
    Performs EDA 03: install distribution analysis.
    """

    # ========================================================
    # PUBLIC API
    # ========================================================

    def run(self) -> InstallDistributionResponse:
        """
        Execute the complete install distribution analysis.

        Returns:
            Validated InstallDistributionResponse.
        """

        dataframe = self._load_data()

        return self._build_response(
            dataframe
        )

    # ========================================================
    # DATA LOADING
    # ========================================================

    def _load_data(self) -> pd.DataFrame:
        """
        Load application installation data from PostgreSQL.
        """

        with engine.connect() as connection:

            dataframe = pd.read_sql(
                text(GET_INSTALL_DISTRIBUTION),
                connection,
            )

        return self._prepare_dataframe(
            dataframe
        )

    # ========================================================
    # DATA PREPARATION
    # ========================================================

    @classmethod
    def _prepare_dataframe(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize installation data.

        The original install string is preserved.

        Example:

            1,000+ -> 1000
            10,000+ -> 10000
            1,000,000+ -> 1000000

        Invalid installation values are removed.
        """

        if dataframe.empty:
            return dataframe

        dataframe = dataframe.copy()

        # ----------------------------------------------------
        # Clean string columns
        # ----------------------------------------------------

        string_columns = [
            "app",
            "category",
            "installs",
            "type",
        ]

        for column in string_columns:

            if column in dataframe.columns:

                dataframe[column] = (
                    dataframe[column]
                    .astype("string")
                    .str.strip()
                )

        # ----------------------------------------------------
        # Convert installs to numeric
        # ----------------------------------------------------

        dataframe["installs_numeric"] = (
            dataframe["installs"]
            .apply(
                cls._parse_install_value
            )
        )

        # ----------------------------------------------------
        # Convert numerical columns
        # ----------------------------------------------------

        numeric_columns = [
            "rating",
            "reviews",
        ]

        for column in numeric_columns:

            if column in dataframe.columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )

        # ----------------------------------------------------
        # Remove invalid rows
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["app"].notna()
            &
            dataframe["category"].notna()
            &
            dataframe["installs"].notna()
            &
            dataframe["installs_numeric"].notna()
        ]

        # ----------------------------------------------------
        # Normalize category
        # ----------------------------------------------------

        dataframe["category"] = (
            dataframe["category"]
            .astype(str)
            .str.strip()
        )

        dataframe = dataframe[
            dataframe["category"] != ""
        ]

        # ----------------------------------------------------
        # Normalize type
        # ----------------------------------------------------

        if "type" in dataframe.columns:

            dataframe["type"] = (
                dataframe["type"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        # ----------------------------------------------------
        # Ensure integer installation values
        # ----------------------------------------------------

        dataframe["installs_numeric"] = (
            dataframe["installs_numeric"]
            .astype("int64")
        )

        # ----------------------------------------------------
        # Sort by installations
        # ----------------------------------------------------

        dataframe = dataframe.sort_values(
            by="installs_numeric",
            ascending=False,
        )

        return dataframe.reset_index(
            drop=True
        )

    # ========================================================
    # INSTALL PARSER
    # ========================================================

    @staticmethod
    def _parse_install_value(
        value: Any,
    ) -> int | None:
        """
        Convert a Google Play install string to an integer.

        Examples:

            '1,000+'       -> 1000
            '10,000+'      -> 10000
            '1,000,000+'   -> 1000000

        Invalid values return None.
        """

        if value is None:
            return None

        if pd.isna(value):
            return None

        value = str(value).strip()

        if not value:
            return None

        # ----------------------------------------------------
        # Expected Google Play format
        # ----------------------------------------------------

        cleaned = (
            value
            .replace(",", "")
            .replace("+", "")
            .strip()
        )

        # ----------------------------------------------------
        # Validate numeric content
        # ----------------------------------------------------

        if not cleaned.isdigit():
            return None

        try:
            return int(cleaned)

        except ValueError:
            return None

    # ========================================================
    # RESPONSE
    # ========================================================

    def _build_response(
        self,
        dataframe: pd.DataFrame,
    ) -> InstallDistributionResponse:
        """
        Build the complete API response.
        """

        analyzed_at = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------------
        # Empty dataset
        # ----------------------------------------------------

        if dataframe.empty:

            return InstallDistributionResponse(
                analyzed_at=analyzed_at,
                total_applications=0,
                total_installs=0,
                average_installs=None,
                median_installs=None,
                distribution=[],
                categories=[],
                top_applications=[],
            )

        # ----------------------------------------------------
        # Global statistics
        # ----------------------------------------------------

        total_applications = len(
            dataframe
        )

        total_installs = int(
            dataframe[
                "installs_numeric"
            ].sum()
        )

        average_installs = float(
            dataframe[
                "installs_numeric"
            ].mean()
        )

        median_installs = float(
            dataframe[
                "installs_numeric"
            ].median()
        )

        # ----------------------------------------------------
        # Distribution
        # ----------------------------------------------------

        distribution = (
            self._build_distribution(
                dataframe
            )
        )

        # ----------------------------------------------------
        # Category statistics
        # ----------------------------------------------------

        categories = (
            self._build_category_statistics(
                dataframe
            )
        )

        # ----------------------------------------------------
        # Top applications
        # ----------------------------------------------------

        top_applications = (
            self._build_top_applications(
                dataframe
            )
        )

        return InstallDistributionResponse(
            analyzed_at=analyzed_at,

            total_applications=(
                total_applications
            ),

            total_installs=(
                total_installs
            ),

            average_installs=(
                self._safe_float(
                    average_installs
                )
            ),

            median_installs=(
                self._safe_float(
                    median_installs
                )
            ),

            distribution=distribution,

            categories=categories,

            top_applications=(
                top_applications
            ),
        )

    # ========================================================
    # DISTRIBUTION
    # ========================================================

    @staticmethod
    def _build_distribution(
        dataframe: pd.DataFrame,
    ) -> list[
        InstallDistributionItem
    ]:
        """
        Build install-bucket distribution.

        The original Google Play install labels are retained.
        """

        distribution_dataframe = (
            dataframe
            .groupby(
                [
                    "installs",
                    "installs_numeric",
                ],
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "app_count"
                }
            )
        )

        total = len(dataframe)

        if total > 0:

            distribution_dataframe[
                "percentage"
            ] = (
                distribution_dataframe[
                    "app_count"
                ]
                / total
                * 100
            )

        else:

            distribution_dataframe[
                "percentage"
            ] = 0.0

        distribution_dataframe = (
            distribution_dataframe
            .sort_values(
                "installs_numeric"
            )
            .reset_index(
                drop=True
            )
        )

        return [
            InstallDistributionItem(
                installs=str(
                    row["installs"]
                ),

                installs_numeric=int(
                    row["installs_numeric"]
                ),

                app_count=int(
                    row["app_count"]
                ),

                percentage=round(
                    float(
                        row["percentage"]
                    ),
                    2,
                ),
            )

            for _, row
            in distribution_dataframe.iterrows()
        ]

    # ========================================================
    # CATEGORY STATISTICS
    # ========================================================

    @staticmethod
    def _build_category_statistics(
        dataframe: pd.DataFrame,
    ) -> list[
        InstallCategoryStatistics
    ]:
        """
        Calculate installation statistics by category.
        """

        grouped = (
            dataframe
            .groupby("category")[
                "installs_numeric"
            ]
            .agg(
                [
                    "count",
                    "mean",
                    "median",
                    "min",
                    "max",
                    "sum",
                ]
            )
            .reset_index()
        )

        grouped = grouped.sort_values(
            "mean",
            ascending=False,
        )

        return [
            InstallCategoryStatistics(
                category=str(
                    row["category"]
                ),

                app_count=int(
                    row["count"]
                ),

                average_installs=(
                    InstallDistributionAnalysis
                    ._safe_float(
                        row["mean"]
                    )
                ),

                median_installs=(
                    InstallDistributionAnalysis
                    ._safe_float(
                        row["median"]
                    )
                ),

                minimum_installs=int(
                    row["min"]
                ),

                maximum_installs=int(
                    row["max"]
                ),

                total_installs=int(
                    row["sum"]
                ),
            )

            for _, row in grouped.iterrows()
        ]

    # ========================================================
    # TOP APPLICATIONS
    # ========================================================

    @staticmethod
    def _build_top_applications(
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> list[
        TopInstalledApplication
    ]:
        """
        Return the top installed applications.

        Args:
            dataframe:
                Prepared application DataFrame.

            limit:
                Maximum number of applications.
        """

        columns = [
            "app",
            "category",
            "rating",
            "reviews",
            "installs",
            "installs_numeric",
            "type",
        ]

        available_columns = [
            column
            for column in columns
            if column in dataframe.columns
        ]

        top_dataframe = (
            dataframe[
                available_columns
            ]
            .head(limit)
        )

        result = []

        for _, row in top_dataframe.iterrows():

            result.append(
                TopInstalledApplication(
                    app=str(
                        row["app"]
                    ),

                    category=str(
                        row["category"]
                    ),

                    rating=(
                        InstallDistributionAnalysis
                        ._safe_float(
                            row.get("rating")
                        )
                    ),

                    reviews=int(
                        row.get(
                            "reviews",
                            0
                        )
                    ),

                    installs=str(
                        row["installs"]
                    ),

                    installs_numeric=int(
                        row["installs_numeric"]
                    ),

                    type=str(
                        row.get(
                            "type",
                            ""
                        )
                    ),
                )
            )

        return result

    # ========================================================
    # VISUALIZATION DATA
    # ========================================================

    def get_visualization_dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return application-level data ready for visualization.

        This DataFrame is used by the export layer.

        Potential visualizations:

            - Install distribution
            - Install distribution by category
            - Top 10 installed applications
            - Rating vs installs
            - Reviews vs installs
        """

        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        columns = [
            "app",
            "category",
            "rating",
            "reviews",
            "installs",
            "installs_numeric",
            "type",
        ]

        available_columns = [
            column
            for column in columns
            if column in dataframe.columns
        ]

        visualization_dataframe = (
            dataframe[
                available_columns
            ].copy()
        )

        # ----------------------------------------------------
        # Logarithmic install value
        # ----------------------------------------------------
        #
        # Install counts are heavily right-skewed.
        #
        # log10(1 + installs)
        #
        # is useful for scatter plots and distributions.
        # ----------------------------------------------------

        visualization_dataframe[
            "log_installs"
        ] = np.log10(
            1
            + visualization_dataframe[
                "installs_numeric"
            ]
        )

        # ----------------------------------------------------
        # Install rank
        # ----------------------------------------------------

        visualization_dataframe[
            "install_rank"
        ] = (
            visualization_dataframe[
                "installs_numeric"
            ]
            .rank(
                method="min",
                ascending=False,
            )
            .astype(int)
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

        NaN and infinite values become None.
        """

        if value is None:
            return None

        try:

            converted = float(value)

            if not np.isfinite(
                converted
            ):
                return None

            return converted

        except (
            TypeError,
            ValueError,
        ):
            return None