from __future__ import annotations

from analysis.ratings_by_category import RatingsByCategoryAnalysis
from analysis.free_vs_paid import FreeVsPaidAnalysis


def test_ratings_safe_float_rejects_non_finite_values() -> None:
    assert RatingsByCategoryAnalysis._safe_float(float("nan")) is None
    assert RatingsByCategoryAnalysis._safe_float(float("inf")) is None
    assert RatingsByCategoryAnalysis._safe_float(float("-inf")) is None


def test_ratings_safe_float_keeps_valid_numbers() -> None:
    assert RatingsByCategoryAnalysis._safe_float(4.23456) == 4.2346
    assert RatingsByCategoryAnalysis._safe_float(None) is None
    assert RatingsByCategoryAnalysis._safe_float("not-a-number") is None


def test_free_paid_safe_float_rejects_non_finite_values() -> None:
    assert FreeVsPaidAnalysis._safe_float(float("nan")) is None
    assert FreeVsPaidAnalysis._safe_float(float("inf")) is None
    assert FreeVsPaidAnalysis._safe_float(float("-inf")) is None


def test_rating_queries_exclude_values_outside_valid_range() -> None:
    normalized_category_query = " ".join(
        RatingsByCategoryAnalysis.QUERY.lower().split()
    )
    normalized_free_paid_query = " ".join(
        FreeVsPaidAnalysis.QUERY.lower().split()
    )

    assert "rating between 1.0 and 5.0" in normalized_category_query
    assert "rating between 1.0 and 5.0" in normalized_free_paid_query
    assert "nulls last" in normalized_category_query
