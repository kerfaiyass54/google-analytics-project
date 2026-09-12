from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sqlalchemy import text

from database.connection import engine


class ReviewCountsAnalysis:
    """
    EDA: Review count analysis.

    Provides:
        - total reviews
        - average reviews
        - median reviews
        - minimum reviews
        - maximum reviews
        - reviews by category
        - top reviewed applications
        - reviews vs installs
        - logarithmic review values
        - review/install ratio
        - Pearson correlation
        - visualization-ready DataFrame
    """

    QUERY = """
        SELECT
            app,
            category,
            rating,
            reviews,
            installs,
            type
        FROM google_play_apps
        WHERE reviews IS NOT NULL
    """

    def run(self) -> dict:

        dataframe = self._load_data()

        if dataframe.empty:
            return {
                "analyzed_at": self._timestamp(),
                "statistics": {
                    "app_count": 0,
                    "average_reviews": None,
                    "median_reviews": None,
                    "minimum_reviews": None,
                    "maximum_reviews": None,
                    "total_reviews": 0,
                },
                "categories": [],
                "top_applications": [],
                "reviews_vs_installs": [],
                "correlation_reviews_installs": None,
            }

        dataframe = self._prepare_data(
            dataframe
        )

        correlation = (
            self._calculate_correlation(
                dataframe
            )
        )

        return {
            "analyzed_at": self._timestamp(),

            "statistics": {
                "app_count": int(
                    len(dataframe)
                ),
                "average_reviews": (
                    self._safe_float(
                        dataframe[
                            "reviews"
                        ].mean()
                    )
                ),
                "median_reviews": (
                    self._safe_float(
                        dataframe[
                            "reviews"
                        ].median()
                    )
                ),
                "minimum_reviews": (
                    int(
                        dataframe[
                            "reviews"
                        ].min()
                    )
                ),
                "maximum_reviews": (
                    int(
                        dataframe[
                            "reviews"
                        ].max()
                    )
                ),
                "total_reviews": (
                    int(
                        dataframe[
                            "reviews"
                        ].sum()
                    )
                ),
            },

            "categories": (
                self._build_category_statistics(
                    dataframe
                )
            ),

            "top_applications": (
                self._build_top_applications(
                    dataframe
                )
            ),

            "reviews_vs_installs": (
                self._build_reviews_vs_installs(
                    dataframe
                )
            ),

            "correlation_reviews_installs": (
                correlation
            ),
        }

    def get_visualization_dataframe(
        self,
    ) -> pd.DataFrame:

        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        dataframe = self._prepare_data(
            dataframe
        )

        if dataframe.empty:
            return dataframe

        dataframe["log_reviews"] = np.log10(
            dataframe["reviews"] + 1
        )

        dataframe["review_rank"] = (
            dataframe["reviews"]
            .rank(
                method="min",
                ascending=False,
            )
            .astype(int)
        )

        dataframe["review_install_ratio"] = np.where(
            dataframe["installs_numeric"] > 0,
            dataframe["reviews"]
            / dataframe["installs_numeric"],
            np.nan,
        )

        return dataframe[
            [
                "app",
                "category",
                "rating",
                "reviews",
                "installs",
                "installs_numeric",
                "type",
                "log_reviews",
                "review_rank",
                "review_install_ratio",
            ]
        ].copy()

    def get_reviews_installs_correlation(
        self,
    ) -> float | None:

        dataframe = self.get_visualization_dataframe()

        if dataframe.empty:
            return None

        return self._calculate_correlation(
            dataframe
        )

    def _load_data(self) -> pd.DataFrame:

        with engine.connect() as connection:
            return pd.read_sql(
                text(self.QUERY),
                connection,
            )

    @staticmethod
    def _prepare_data(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        dataframe = dataframe.copy()

        dataframe["reviews"] = pd.to_numeric(
            dataframe["reviews"],
            errors="coerce",
        )

        dataframe["rating"] = pd.to_numeric(
            dataframe["rating"],
            errors="coerce",
        )

        dataframe["installs_numeric"] = (
            dataframe["installs"]
            .apply(
                ReviewCountsAnalysis
                ._parse_installs
            )
        )

        dataframe = dataframe[
            dataframe["reviews"].notna()
        ]

        dataframe = dataframe[
            dataframe["reviews"] >= 0
        ]

        dataframe = dataframe.sort_values(
            "reviews",
            ascending=False,
        )

        return dataframe.reset_index(
            drop=True
        )

    @staticmethod
    def _parse_installs(
        value,
    ) -> int | None:

        if value is None:
            return None

        if pd.isna(value):
            return None

        value = str(value).strip()

        value = (
            value
            .replace(",", "")
            .replace("+", "")
            .strip()
        )

        if not value.isdigit():
            return None

        return int(value)

    @staticmethod
    def _build_category_statistics(
        dataframe: pd.DataFrame,
    ) -> list[dict]:

        grouped = (
            dataframe
            .groupby("category")[
                "reviews"
            ]
            .agg(
                [
                    "count",
                    "mean",
                    "median",
                    "sum",
                    "max",
                ]
            )
            .reset_index()
            .sort_values(
                "sum",
                ascending=False,
            )
        )

        result = []

        for _, row in grouped.iterrows():

            result.append(
                {
                    "category": str(
                        row["category"]
                    ),
                    "app_count": int(
                        row["count"]
                    ),
                    "average_reviews": (
                        ReviewCountsAnalysis
                        ._safe_float(
                            row["mean"]
                        )
                    ),
                    "median_reviews": (
                        ReviewCountsAnalysis
                        ._safe_float(
                            row["median"]
                        )
                    ),
                    "total_reviews": int(
                        row["sum"]
                    ),
                    "maximum_reviews": int(
                        row["max"]
                    ),
                }
            )

        return result

    @staticmethod
    def _build_top_applications(
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> list[dict]:

        result = []

        for _, row in dataframe.head(
            limit
        ).iterrows():

            result.append(
                {
                    "app": str(
                        row["app"]
                    ),
                    "category": str(
                        row["category"]
                    ),
                    "rating": (
                        ReviewCountsAnalysis
                        ._safe_float(
                            row["rating"]
                        )
                    ),
                    "reviews": int(
                        row["reviews"]
                    ),
                    "installs": str(
                        row["installs"]
                    ),
                    "type": str(
                        row["type"]
                    ),
                }
            )

        return result

    @staticmethod
    def _build_reviews_vs_installs(
        dataframe: pd.DataFrame,
        limit: int = 1000,
    ) -> list[dict]:

        valid = dataframe[
            dataframe[
                "installs_numeric"
            ].notna()
        ].head(limit)

        result = []

        for _, row in valid.iterrows():

            result.append(
                {
                    "app": str(
                        row["app"]
                    ),
                    "category": str(
                        row["category"]
                    ),
                    "rating": (
                        ReviewCountsAnalysis
                        ._safe_float(
                            row["rating"]
                        )
                    ),
                    "reviews": int(
                        row["reviews"]
                    ),
                    "installs": str(
                        row["installs"]
                    ),
                    "installs_numeric": int(
                        row[
                            "installs_numeric"
                        ]
                    ),
                    "type": str(
                        row["type"]
                    ),
                }
            )

        return result

    @staticmethod
    def _calculate_correlation(
        dataframe: pd.DataFrame,
    ) -> float | None:

        if dataframe.empty:
            return None

        if "installs_numeric" not in dataframe:
            return None

        valid = dataframe[
            [
                "reviews",
                "installs_numeric",
            ]
        ].dropna()

        valid = valid[
            valid["reviews"] >= 0
        ]

        valid = valid[
            valid["installs_numeric"] >= 0
        ]

        if len(valid) < 2:
            return None

        log_reviews = np.log10(
            valid["reviews"] + 1
        )

        log_installs = np.log10(
            valid["installs_numeric"] + 1
        )

        correlation = (
            log_reviews.corr(
                log_installs
            )
        )

        return ReviewCountsAnalysis._safe_float(
            correlation
        )

    @staticmethod
    def _safe_float(
        value,
    ) -> float | None:

        if value is None:
            return None

        try:
            value = float(value)

            if not np.isfinite(value):
                return None

            return round(value, 4)

        except (TypeError, ValueError):
            return None

    @staticmethod
    def _timestamp() -> datetime:
        return datetime.now(timezone.utc)