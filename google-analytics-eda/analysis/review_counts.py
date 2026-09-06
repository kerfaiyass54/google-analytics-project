"""
EDA 04 — Review Counts.

Analyzes the number of reviews received by Google Play
applications.

Responsibilities:
    - Retrieve review statistics from PostgreSQL
    - Analyze reviews by category
    - Identify top-reviewed applications
    - Analyze reviews vs installs
    - Prepare visualization-ready data
    - Return a validated ReviewCountsResponse

The visualization layer is responsible for generating
charts and exported files.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import text

from database import engine
from queries import (
    GET_REVIEW_STATISTICS,
    GET_REVIEWS_BY_CATEGORY,
    GET_TOP_REVIEWED_APPS,
    GET_REVIEWS_VS_INSTALLS,
)
from schema.eda import (
    ReviewCategoryStatistics,
    ReviewCountsResponse,
    ReviewStatistics,
    ReviewsVsInstalls,
    TopReviewedApplication,
)


class ReviewCountsAnalysis:
    """
    Performs EDA 04: Review Counts.
    """

    # ========================================================
    # PUBLIC API
    # ========================================================

    def run(self) -> ReviewCountsResponse:
        """
        Execute the complete review-count analysis.

        Returns:
            ReviewCountsResponse.
        """

        statistics_dataframe = (
            self._load_review_statistics()
        )

        category_dataframe = (
            self._load_reviews_by_category()
        )

        top_apps_dataframe = (
            self._load_top_reviewed_apps()
        )

        reviews_vs_installs_dataframe = (
            self._load_reviews_vs_installs()
        )

        return self._build_response(
            statistics_dataframe=statistics_dataframe,
            category_dataframe=category_dataframe,
            top_apps_dataframe=top_apps_dataframe,
            reviews_vs_installs_dataframe=(
                reviews_vs_installs_dataframe
            ),
        )

    # ========================================================
    # DATABASE
    # ========================================================

    @staticmethod
    def _load_review_statistics() -> pd.DataFrame:
        """
        Load global review statistics.
        """

        with engine.connect() as connection:

            return pd.read_sql(
                text(GET_REVIEW_STATISTICS),
                connection,
            )

    @staticmethod
    def _load_reviews_by_category() -> pd.DataFrame:
        """
        Load review statistics grouped by category.
        """

        with engine.connect() as connection:

            return pd.read_sql(
                text(GET_REVIEWS_BY_CATEGORY),
                connection,
            )

    @staticmethod
    def _load_top_reviewed_apps(
        limit: int = 10,
    ) -> pd.DataFrame:
        """
        Load the top-reviewed applications.
        """

        with engine.connect() as connection:

            return pd.read_sql(
                text(GET_TOP_REVIEWED_APPS),
                connection,
                params={
                    "limit": limit,
                },
            )

    @staticmethod
    def _load_reviews_vs_installs() -> pd.DataFrame:
        """
        Load reviews and installation information.
        """

        with engine.connect() as connection:

            return pd.read_sql(
                text(GET_REVIEWS_VS_INSTALLS),
                connection,
            )

    # ========================================================
    # RESPONSE
    # ========================================================

    def _build_response(
        self,
        statistics_dataframe: pd.DataFrame,
        category_dataframe: pd.DataFrame,
        top_apps_dataframe: pd.DataFrame,
        reviews_vs_installs_dataframe: pd.DataFrame,
    ) -> ReviewCountsResponse:
        """
        Build the complete ReviewCountsResponse.
        """

        analyzed_at = datetime.now(
            timezone.utc
        )

        statistics = (
            self._build_global_statistics(
                statistics_dataframe
            )
        )

        categories = (
            self._build_category_statistics(
                category_dataframe
            )
        )

        top_applications = (
            self._build_top_applications(
                top_apps_dataframe
            )
        )

        reviews_vs_installs = (
            self._build_reviews_vs_installs(
                reviews_vs_installs_dataframe
            )
        )

        return ReviewCountsResponse(
            analyzed_at=analyzed_at,

            statistics=statistics,

            categories=categories,

            top_applications=(
                top_applications
            ),

            reviews_vs_installs=(
                reviews_vs_installs
            ),
        )

    # ========================================================
    # GLOBAL STATISTICS
    # ========================================================

    @staticmethod
    def _build_global_statistics(
        dataframe: pd.DataFrame,
    ) -> ReviewStatistics:
        """
        Build global review statistics from SQL results.

        Expected SQL columns:

            app_count
            average_reviews
            median_reviews
            minimum_reviews
            maximum_reviews
            review_stddev
            total_reviews
        """

        if dataframe.empty:

            return ReviewStatistics(
                app_count=0,
                average_reviews=None,
                median_reviews=None,
                minimum_reviews=None,
                maximum_reviews=None,
                review_stddev=None,
                total_reviews=0,
            )

        row = dataframe.iloc[0]

        return ReviewStatistics(
            app_count=(
                ReviewCountsAnalysis._safe_int(
                    row.get("app_count")
                )
                or 0
            ),

            average_reviews=(
                ReviewCountsAnalysis._safe_float(
                    row.get(
                        "average_reviews"
                    )
                )
            ),

            median_reviews=(
                ReviewCountsAnalysis._safe_float(
                    row.get(
                        "median_reviews"
                    )
                )
            ),

            minimum_reviews=(
                ReviewCountsAnalysis._safe_int(
                    row.get(
                        "minimum_reviews"
                    )
                )
            ),

            maximum_reviews=(
                ReviewCountsAnalysis._safe_int(
                    row.get(
                        "maximum_reviews"
                    )
                )
            ),

            review_stddev=(
                ReviewCountsAnalysis._safe_float(
                    row.get(
                        "review_stddev"
                    )
                )
            ),

            total_reviews=(
                ReviewCountsAnalysis._safe_int(
                    row.get(
                        "total_reviews"
                    )
                )
                or 0
            ),
        )

    # ========================================================
    # REVIEWS BY CATEGORY
    # ========================================================

    @staticmethod
    def _build_category_statistics(
        dataframe: pd.DataFrame,
    ) -> list[
        ReviewCategoryStatistics
    ]:
        """
        Convert category-level SQL results into
        ReviewCategoryStatistics objects.
        """

        if dataframe.empty:
            return []

        result = []

        for _, row in dataframe.iterrows():

            result.append(
                ReviewCategoryStatistics(
                    category=str(
                        row.get(
                            "category",
                            ""
                        )
                    ),

                    app_count=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "app_count"
                            )
                        )
                        or 0
                    ),

                    average_reviews=(
                        ReviewCountsAnalysis._safe_float(
                            row.get(
                                "average_reviews"
                            )
                        )
                    ),

                    median_reviews=(
                        ReviewCountsAnalysis._safe_float(
                            row.get(
                                "median_reviews"
                            )
                        )
                    ),

                    total_reviews=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "total_reviews"
                            )
                        )
                        or 0
                    ),

                    maximum_reviews=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "maximum_reviews"
                            )
                        )
                    ),
                )
            )

        return result

    # ========================================================
    # TOP REVIEWED APPLICATIONS
    # ========================================================

    @staticmethod
    def _build_top_applications(
        dataframe: pd.DataFrame,
    ) -> list[
        TopReviewedApplication
    ]:
        """
        Convert top-reviewed application query results
        into TopReviewedApplication objects.
        """

        if dataframe.empty:
            return []

        result = []

        for _, row in dataframe.iterrows():

            result.append(
                TopReviewedApplication(
                    app=str(
                        row.get(
                            "app",
                            ""
                        )
                    ),

                    category=str(
                        row.get(
                            "category",
                            ""
                        )
                    ),

                    rating=(
                        ReviewCountsAnalysis._safe_float(
                            row.get(
                                "rating"
                            )
                        )
                    ),

                    reviews=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "reviews"
                            )
                        )
                        or 0
                    ),

                    installs=str(
                        row.get(
                            "installs",
                            ""
                        )
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
    # REVIEWS VS INSTALLS
    # ========================================================

    @staticmethod
    def _build_reviews_vs_installs(
        dataframe: pd.DataFrame,
        limit: int = 1000,
    ) -> list[
        ReviewsVsInstalls
    ]:
        """
        Convert reviews-vs-installs query results into
        ReviewsVsInstalls objects.
        """

        if dataframe.empty:
            return []

        dataframe = dataframe.copy()

        # ----------------------------------------------------
        # Normalize numeric values
        # ----------------------------------------------------

        dataframe["reviews"] = pd.to_numeric(
            dataframe["reviews"],
            errors="coerce",
        )

        dataframe[
            "installs_numeric"
        ] = pd.to_numeric(
            dataframe[
                "installs_numeric"
            ],
            errors="coerce",
        )

        dataframe["rating"] = pd.to_numeric(
            dataframe["rating"],
            errors="coerce",
        )

        # ----------------------------------------------------
        # Remove invalid observations
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["reviews"].notna()
            &
            dataframe[
                "installs_numeric"
            ].notna()
        ]

        # ----------------------------------------------------
        # Highest-review applications first
        # ----------------------------------------------------

        dataframe = (
            dataframe
            .sort_values(
                by="reviews",
                ascending=False,
            )
            .head(limit)
        )

        result = []

        for _, row in dataframe.iterrows():

            result.append(
                ReviewsVsInstalls(
                    app=str(
                        row.get(
                            "app",
                            ""
                        )
                    ),

                    category=str(
                        row.get(
                            "category",
                            ""
                        )
                    ),

                    rating=(
                        ReviewCountsAnalysis._safe_float(
                            row.get(
                                "rating"
                            )
                        )
                    ),

                    reviews=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "reviews"
                            )
                        )
                        or 0
                    ),

                    installs=str(
                        row.get(
                            "installs",
                            ""
                        )
                    ),

                    installs_numeric=(
                        ReviewCountsAnalysis._safe_int(
                            row.get(
                                "installs_numeric"
                            )
                        )
                        or 0
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
        Return a visualization-ready DataFrame.

        This DataFrame is intended for the export layer.

        It contains:

            app
            category
            rating
            reviews
            installs
            installs_numeric
            type
            log_reviews
            log_installs
            review_rank
            review_install_ratio
        """

        dataframe = (
            self._load_reviews_vs_installs()
        )

        if dataframe.empty:
            return dataframe

        dataframe = dataframe.copy()

        # ----------------------------------------------------
        # Numeric conversion
        # ----------------------------------------------------

        dataframe["reviews"] = pd.to_numeric(
            dataframe["reviews"],
            errors="coerce",
        )

        dataframe["rating"] = pd.to_numeric(
            dataframe["rating"],
            errors="coerce",
        )

        dataframe[
            "installs_numeric"
        ] = pd.to_numeric(
            dataframe[
                "installs_numeric"
            ],
            errors="coerce",
        )

        # ----------------------------------------------------
        # Remove invalid review values
        # ----------------------------------------------------

        dataframe = dataframe[
            dataframe["reviews"].notna()
            &
            (
                dataframe["reviews"]
                >= 0
            )
        ]

        # ----------------------------------------------------
        # Logarithmic review scale
        # ----------------------------------------------------

        dataframe["log_reviews"] = (
            np.log10(
                1
                + dataframe["reviews"]
            )
        )

        # ----------------------------------------------------
        # Logarithmic install scale
        # ----------------------------------------------------

        if "installs_numeric" in (
            dataframe.columns
        ):

            dataframe["log_installs"] = (
                np.log10(
                    1
                    + dataframe[
                        "installs_numeric"
                    ]
                )
            )

        # ----------------------------------------------------
        # Review ranking
        # ----------------------------------------------------

        dataframe["review_rank"] = (
            dataframe["reviews"]
            .rank(
                method="min",
                ascending=False,
            )
            .astype(int)
        )

        # ----------------------------------------------------
        # Review / install ratio
        # ----------------------------------------------------
        #
        # IMPORTANT:
        #
        # This is an analytical indicator, NOT a true
        # conversion rate.
        #
        # Google Play install values are lower bounds:
        #
        #     1,000+
        #     10,000+
        #
        # Therefore the ratio should not be interpreted
        # as an exact percentage of users who reviewed.
        # ----------------------------------------------------

        if "installs_numeric" in (
            dataframe.columns
        ):

            dataframe[
                "review_install_ratio"
            ] = np.where(
                dataframe[
                    "installs_numeric"
                ] > 0,

                dataframe["reviews"]
                /
                dataframe[
                    "installs_numeric"
                ],

                np.nan,
            )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        dataframe = (
            dataframe
            .sort_values(
                by="reviews",
                ascending=False,
            )
            .reset_index(
                drop=True
            )
        )

        return dataframe

    # ========================================================
    # CORRELATION
    # ========================================================

    def get_reviews_installs_correlation(
        self,
    ) -> float | None:
        """
        Calculate the Pearson correlation between
        reviews and installs using logarithmic values.

        This method is useful to the export layer when
        generating analytical visualizations.

        Returns:
            Correlation between log(reviews) and
            log(installs), or None if insufficient data.
        """

        dataframe = (
            self.get_visualization_dataframe()
        )

        if dataframe.empty:
            return None

        required_columns = {
            "reviews",
            "installs_numeric",
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        valid_dataframe = dataframe[
            [
                "reviews",
                "installs_numeric",
            ]
        ].dropna()

        if len(valid_dataframe) < 2:
            return None

        log_reviews = np.log10(
            1
            + valid_dataframe[
                "reviews"
            ]
        )

        log_installs = np.log10(
            1
            + valid_dataframe[
                "installs_numeric"
            ]
        )

        correlation = (
            log_reviews.corr(
                log_installs
            )
        )

        return (
            ReviewCountsAnalysis._safe_float(
                correlation
            )
        )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_int(
        value: Any,
    ) -> int | None:
        """
        Safely convert a value to integer.

        Invalid, NaN and infinite values return None.
        """

        if value is None:
            return None

        try:

            converted = float(value)

            if not np.isfinite(
                converted
            ):
                return None

            return int(converted)

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        """
        Safely convert a value to float.

        Invalid, NaN and infinite values return None.
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