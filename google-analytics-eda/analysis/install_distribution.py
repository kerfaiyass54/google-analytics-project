from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sqlalchemy import text

from database.connection import engine


class InstallDistributionAnalysis:
    """
    EDA: Distribution of application installations.

    Provides:
        - total applications
        - total installs
        - average installs
        - median installs
        - install distribution
        - installations by category
        - top installed applications
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
        WHERE installs IS NOT NULL
          AND installs <> ''
    """

    def run(self) -> dict:
        dataframe = self._load_data()

        if dataframe.empty:
            return {
                "analyzed_at": self._timestamp(),
                "total_applications": 0,
                "total_installs": 0,
                "average_installs": None,
                "median_installs": None,
                "distribution": [],
                "categories": [],
                "top_applications": [],
            }

        dataframe = self._prepare_data(
            dataframe
        )

        if dataframe.empty:
            return {
                "analyzed_at": self._timestamp(),
                "total_applications": 0,
                "total_installs": 0,
                "average_installs": None,
                "median_installs": None,
                "distribution": [],
                "categories": [],
                "top_applications": [],
            }

        return {
            "analyzed_at": self._timestamp(),

            "total_applications": int(
                len(dataframe)
            ),

            "total_installs": int(
                dataframe[
                    "installs_numeric"
                ].sum()
            ),

            "average_installs": self._safe_float(
                dataframe[
                    "installs_numeric"
                ].mean()
            ),

            "median_installs": self._safe_float(
                dataframe[
                    "installs_numeric"
                ].median()
            ),

            "distribution": (
                self._build_distribution(
                    dataframe
                )
            ),

            "categories": (
                self._build_categories(
                    dataframe
                )
            ),

            "top_applications": (
                self._build_top_applications(
                    dataframe
                )
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

        dataframe["log_installs"] = np.log10(
            dataframe[
                "installs_numeric"
            ]
            + 1
        )

        dataframe["install_rank"] = (
            dataframe[
                "installs_numeric"
            ]
            .rank(
                method="min",
                ascending=False,
            )
            .astype(int)
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
                "log_installs",
                "install_rank",
            ]
        ].copy()

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

        dataframe["installs_numeric"] = (
            dataframe["installs"]
            .apply(
                InstallDistributionAnalysis
                ._parse_installs
            )
        )

        dataframe["rating"] = pd.to_numeric(
            dataframe["rating"],
            errors="coerce",
        )

        dataframe["reviews"] = pd.to_numeric(
            dataframe["reviews"],
            errors="coerce",
        )

        dataframe = dataframe[
            dataframe["installs_numeric"]
            .notna()
        ]

        dataframe = dataframe[
            dataframe["installs_numeric"]
            >= 0
        ]

        dataframe = dataframe.sort_values(
            "installs_numeric",
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

        if not value:
            return None

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
    def _build_distribution(
        dataframe: pd.DataFrame,
    ) -> list[dict]:

        grouped = (
            dataframe
            .groupby(
                [
                    "installs",
                    "installs_numeric",
                ]
            )
            .size()
            .reset_index(
                name="app_count"
            )
            .sort_values(
                "installs_numeric"
            )
        )

        total = len(dataframe)

        result = []

        for _, row in grouped.iterrows():

            percentage = (
                row["app_count"]
                / total
                * 100
                if total > 0
                else 0.0
            )

            result.append(
                {
                    "installs": str(
                        row["installs"]
                    ),
                    "installs_numeric": int(
                        row[
                            "installs_numeric"
                        ]
                    ),
                    "app_count": int(
                        row["app_count"]
                    ),
                    "percentage": round(
                        percentage,
                        2,
                    ),
                }
            )

        return result

    @staticmethod
    def _build_categories(
        dataframe: pd.DataFrame,
    ) -> list[dict]:

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
            .sort_values(
                "mean",
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
                    "average_installs": (
                        InstallDistributionAnalysis
                        ._safe_float(
                            row["mean"]
                        )
                    ),
                    "median_installs": (
                        InstallDistributionAnalysis
                        ._safe_float(
                            row["median"]
                        )
                    ),
                    "minimum_installs": int(
                        row["min"]
                    ),
                    "maximum_installs": int(
                        row["max"]
                    ),
                    "total_installs": int(
                        row["sum"]
                    ),
                }
            )

        return result

    @staticmethod
    def _build_top_applications(
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> list[dict]:

        top = dataframe.head(limit)

        result = []

        for _, row in top.iterrows():

            result.append(
                {
                    "app": str(
                        row["app"]
                    ),
                    "category": str(
                        row["category"]
                    ),
                    "rating": (
                        InstallDistributionAnalysis
                        ._safe_float(
                            row["rating"]
                        )
                    ),
                    "reviews": (
                        int(row["reviews"])
                        if pd.notna(
                            row["reviews"]
                        )
                        else 0
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