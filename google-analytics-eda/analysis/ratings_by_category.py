from __future__ import annotations

from datetime import datetime, timezone
import math

import pandas as pd
from sqlalchemy import text

from database.connection import engine


class RatingsByCategoryAnalysis:
    """
    EDA: Application ratings grouped by category.

    Only ratings within the expected Google Play range (1.0–5.0)
    participate in rating statistics. Apps with invalid/missing ratings
    remain included in app_count, but not rated_app_count.
    """

    QUERY = """
        SELECT
            category,
            COUNT(*) AS app_count,
            COUNT(*) FILTER (
                WHERE rating BETWEEN 1.0 AND 5.0
            ) AS rated_app_count,
            AVG(rating) FILTER (
                WHERE rating BETWEEN 1.0 AND 5.0
            ) AS average_rating,
            MIN(rating) FILTER (
                WHERE rating BETWEEN 1.0 AND 5.0
            ) AS minimum_rating,
            MAX(rating) FILTER (
                WHERE rating BETWEEN 1.0 AND 5.0
            ) AS maximum_rating
        FROM google_play_apps
        GROUP BY category
        ORDER BY average_rating DESC NULLS LAST
    """

    VALID_RATING_FILTER = """
        rating BETWEEN 1.0 AND 5.0
    """

    def run(self) -> dict:
        dataframe = self._load_data()

        if dataframe.empty:
            return {
                "analyzed_at": self._timestamp(),
                "total_categories": 0,
                "total_rated_applications": 0,
                "overall_average_rating": None,
                "categories": [],
            }

        dataframe = self._prepare_data(dataframe)
        categories = []

        for _, row in dataframe.iterrows():
            categories.append(
                {
                    "category": row["category"],
                    "app_count": int(row["app_count"]),
                    "rated_app_count": int(row["rated_app_count"]),
                    "average_rating": self._safe_float(row["average_rating"]),
                    "minimum_rating": self._safe_float(row["minimum_rating"]),
                    "maximum_rating": self._safe_float(row["maximum_rating"]),
                    "median_rating": self._calculate_median(row["category"]),
                }
            )

        return {
            "analyzed_at": self._timestamp(),
            "total_categories": len(categories),
            "total_rated_applications": int(dataframe["rated_app_count"].sum()),
            "overall_average_rating": self._calculate_overall_average(),
            "categories": categories,
        }

    def get_visualization_dataframe(self) -> pd.DataFrame:
        dataframe = self._load_data()

        if dataframe.empty:
            return dataframe

        dataframe = self._prepare_data(dataframe)

        return dataframe[
            [
                "category",
                "app_count",
                "rated_app_count",
                "average_rating",
                "minimum_rating",
                "maximum_rating",
            ]
        ].copy()

    def _load_data(self) -> pd.DataFrame:
        with engine.connect() as connection:
            return pd.read_sql(text(self.QUERY), connection)

    @staticmethod
    def _prepare_data(dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.copy()

        dataframe["category"] = (
            dataframe["category"].astype("string").str.strip()
        )

        numeric_columns = [
            "app_count",
            "rated_app_count",
            "average_rating",
            "minimum_rating",
            "maximum_rating",
        ]

        for column in numeric_columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

        dataframe = dataframe[
            dataframe["category"].notna()
            & (dataframe["category"] != "")
        ]

        return dataframe.reset_index(drop=True)

    @staticmethod
    def _calculate_median(category: str) -> float | None:
        query = """
            SELECT rating
            FROM google_play_apps
            WHERE category = :category
              AND rating BETWEEN 1.0 AND 5.0
            ORDER BY rating
        """

        with engine.connect() as connection:
            dataframe = pd.read_sql(
                text(query),
                connection,
                params={"category": category},
            )

        if dataframe.empty:
            return None

        return RatingsByCategoryAnalysis._safe_float(
            dataframe["rating"].median()
        )

    @staticmethod
    def _calculate_overall_average() -> float | None:
        query = """
            SELECT AVG(rating)
            FROM google_play_apps
            WHERE rating BETWEEN 1.0 AND 5.0
        """

        with engine.connect() as connection:
            result = connection.execute(text(query)).scalar()

        return RatingsByCategoryAnalysis._safe_float(result)

    @staticmethod
    def _safe_float(value) -> float | None:
        if value is None:
            return None

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if not math.isfinite(number):
            return None

        return round(number, 4)

    @staticmethod
    def _timestamp() -> datetime:
        return datetime.now(timezone.utc)
