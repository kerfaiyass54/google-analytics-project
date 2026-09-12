from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from database.connection import engine


class FreeVsPaidAnalysis:
    """
    EDA: Comparison between free and paid applications.

    Provides:
        - number of free applications
        - number of paid applications
        - percentage distribution
        - average rating
        - average reviews
        - total reviews
        - average price
        - visualization-ready DataFrame
    """

    QUERY = """
        SELECT
            type,
            COUNT(*) AS app_count,
            AVG(rating) AS average_rating,
            AVG(reviews) AS average_reviews,
            SUM(reviews) AS total_reviews,
            AVG(price) AS average_price,
            MIN(price) AS minimum_price,
            MAX(price) AS maximum_price
        FROM google_play_apps
        GROUP BY type
        ORDER BY type
    """

    def run(self) -> dict:
        dataframe = self._load_data()

        if dataframe.empty:
            return {
                "analyzed_at": self._timestamp(),
                "free_applications": 0,
                "paid_applications": 0,
                "free_percentage": 0.0,
                "paid_percentage": 0.0,
                "applications": [],
            }

        dataframe = self._prepare_data(dataframe)

        total = int(dataframe["app_count"].sum())

        free_count = self._get_count(
            dataframe,
            "FREE",
        )

        paid_count = self._get_count(
            dataframe,
            "PAID",
        )

        free_percentage = (
            free_count / total * 100
            if total > 0
            else 0.0
        )

        paid_percentage = (
            paid_count / total * 100
            if total > 0
            else 0.0
        )

        applications = []

        for _, row in dataframe.iterrows():

            applications.append(
                {
                    "type": row["type"],
                    "app_count": int(
                        row["app_count"]
                    ),
                    "percentage": round(
                        (
                            row["app_count"]
                            / total
                            * 100
                        )
                        if total > 0
                        else 0.0,
                        2,
                    ),
                    "average_rating": self._safe_float(
                        row["average_rating"]
                    ),
                    "average_reviews": self._safe_float(
                        row["average_reviews"]
                    ),
                    "total_reviews": int(
                        row["total_reviews"]
                    ),
                    "average_price": self._safe_float(
                        row["average_price"]
                    ),
                    "minimum_price": self._safe_float(
                        row["minimum_price"]
                    ),
                    "maximum_price": self._safe_float(
                        row["maximum_price"]
                    ),
                }
            )

        return {
            "analyzed_at": self._timestamp(),
            "free_applications": free_count,
            "paid_applications": paid_count,
            "free_percentage": round(
                free_percentage,
                2,
            ),
            "paid_percentage": round(
                paid_percentage,
                2,
            ),
            "applications": applications,
        }

    def get_visualization_dataframe(self) -> pd.DataFrame:
        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        dataframe = self._prepare_data(dataframe)

        total = dataframe["app_count"].sum()

        dataframe["percentage"] = (
            dataframe["app_count"]
            / total
            * 100
            if total > 0
            else 0
        )

        return dataframe[
            [
                "type",
                "app_count",
                "percentage",
                "average_rating",
                "average_reviews",
                "total_reviews",
                "average_price",
                "minimum_price",
                "maximum_price",
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

        dataframe["type"] = (
            dataframe["type"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        numeric_columns = [
            "app_count",
            "average_rating",
            "average_reviews",
            "total_reviews",
            "average_price",
            "minimum_price",
            "maximum_price",
        ]

        for column in numeric_columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

        dataframe = dataframe[
            dataframe["type"].isin(
                ["FREE", "PAID"]
            )
        ]

        return dataframe.reset_index(drop=True)

    @staticmethod
    def _get_count(
        dataframe: pd.DataFrame,
        application_type: str,
    ) -> int:

        rows = dataframe[
            dataframe["type"]
            == application_type
        ]

        if rows.empty:
            return 0

        return int(
            rows.iloc[0]["app_count"]
        )

    @staticmethod
    def _safe_float(
        value,
    ) -> float | None:

        if value is None:
            return None

        try:
            value = float(value)

            if pd.isna(value):
                return None

            return round(value, 4)

        except (TypeError, ValueError):
            return None

    @staticmethod
    def _timestamp() -> datetime:
        return datetime.now(timezone.utc)