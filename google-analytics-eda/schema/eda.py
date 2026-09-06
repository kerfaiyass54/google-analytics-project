"""
Pydantic schemas for the four Google Play Store EDAs.

These schemas define the structure of:
    1. Ratings by category
    2. Free vs paid applications
    3. Install distribution
    4. Review counts

They are used for:
    - FastAPI responses
    - API validation
    - Elasticsearch documents
    - Export/report generation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# COMMON
# ============================================================

class EdaBaseModel(BaseModel):
    """
    Base configuration shared by all EDA schemas.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ============================================================
# EDA 01 — RATINGS BY CATEGORY
# ============================================================

class RatingCategoryStatistics(EdaBaseModel):
    """
    Statistics for one application category.
    """

    category: str

    app_count: int = Field(
        ge=0
    )

    rated_app_count: int = Field(
        ge=0
    )

    average_rating: float | None = None

    minimum_rating: float | None = None

    maximum_rating: float | None = None

    median_rating: float | None = None

    rating_stddev: float | None = None


class RatingsByCategoryResponse(EdaBaseModel):
    """
    Complete result of EDA 01.
    """

    analysis_name: str = (
        "Ratings by Category"
    )

    analyzed_at: datetime

    total_categories: int = Field(
        ge=0
    )

    total_rated_applications: int = Field(
        ge=0
    )

    overall_average_rating: float | None = None

    categories: list[
        RatingCategoryStatistics
    ] = Field(
        default_factory=list
    )


# ============================================================
# EDA 02 — FREE VS PAID
# ============================================================

class FreePaidStatistics(EdaBaseModel):
    """
    Statistics for either FREE or PAID applications.
    """

    type: str

    app_count: int = Field(
        ge=0
    )

    rated_app_count: int = Field(
        ge=0
    )

    average_rating: float | None = None

    median_rating: float | None = None

    average_reviews: float | None = None

    median_reviews: float | None = None

    total_reviews: int = Field(
        default=0,
        ge=0
    )

    average_price: float | None = None

    minimum_price: float | None = None

    maximum_price: float | None = None


class FreeVsPaidResponse(EdaBaseModel):
    """
    Complete result of EDA 02.
    """

    analysis_name: str = (
        "Free vs Paid Applications"
    )

    analyzed_at: datetime

    free_applications: int = Field(
        ge=0
    )

    paid_applications: int = Field(
        ge=0
    )

    free_percentage: float = Field(
        ge=0,
        le=100
    )

    paid_percentage: float = Field(
        ge=0,
        le=100
    )

    average_rating_difference: float | None = None

    average_reviews_difference: float | None = None

    applications: list[
        FreePaidStatistics
    ] = Field(
        default_factory=list
    )


# ============================================================
# EDA 03 — INSTALL DISTRIBUTION
# ============================================================

class InstallDistributionItem(EdaBaseModel):
    """
    One install bucket.
    """

    installs: str

    installs_numeric: int = Field(
        ge=0
    )

    app_count: int = Field(
        ge=0
    )

    percentage: float = Field(
        ge=0,
        le=100
    )


class InstallCategoryStatistics(EdaBaseModel):
    """
    Install statistics for one category.
    """

    category: str

    app_count: int = Field(
        ge=0
    )

    average_installs: float | None = None

    median_installs: float | None = None

    minimum_installs: int | None = Field(
        default=None,
        ge=0
    )

    maximum_installs: int | None = Field(
        default=None,
        ge=0
    )

    total_installs: int = Field(
        default=0,
        ge=0
    )


class TopInstalledApplication(EdaBaseModel):
    """
    Application with the highest installation count.
    """

    app: str

    category: str

    rating: float | None = None

    reviews: int = Field(
        ge=0
    )

    installs: str

    installs_numeric: int = Field(
        ge=0
    )

    type: str


class InstallDistributionResponse(EdaBaseModel):
    """
    Complete result of EDA 03.
    """

    analysis_name: str = (
        "Install Distribution"
    )

    analyzed_at: datetime

    total_applications: int = Field(
        ge=0
    )

    total_installs: int = Field(
        ge=0
    )

    average_installs: float | None = None

    median_installs: float | None = None

    distribution: list[
        InstallDistributionItem
    ] = Field(
        default_factory=list
    )

    categories: list[
        InstallCategoryStatistics
    ] = Field(
        default_factory=list
    )

    top_applications: list[
        TopInstalledApplication
    ] = Field(
        default_factory=list
    )


# ============================================================
# EDA 04 — REVIEW COUNTS
# ============================================================

class ReviewStatistics(EdaBaseModel):
    """
    Global review statistics.
    """

    app_count: int = Field(
        ge=0
    )

    average_reviews: float | None = None

    median_reviews: float | None = None

    minimum_reviews: int | None = Field(
        default=None,
        ge=0
    )

    maximum_reviews: int | None = Field(
        default=None,
        ge=0
    )

    review_stddev: float | None = None

    total_reviews: int = Field(
        default=0,
        ge=0
    )


class ReviewCategoryStatistics(EdaBaseModel):
    """
    Review statistics for one category.
    """

    category: str

    app_count: int = Field(
        ge=0
    )

    average_reviews: float | None = None

    median_reviews: float | None = None

    total_reviews: int = Field(
        default=0,
        ge=0
    )

    maximum_reviews: int | None = Field(
        default=None,
        ge=0
    )


class TopReviewedApplication(EdaBaseModel):
    """
    Application with a high review count.
    """

    app: str

    category: str

    rating: float | None = None

    reviews: int = Field(
        ge=0
    )

    installs: str

    type: str


class ReviewsVsInstalls(EdaBaseModel):
    """
    Data point used to analyze the relationship
    between reviews and installs.
    """

    app: str

    category: str

    rating: float | None = None

    reviews: int = Field(
        ge=0
    )

    installs: str

    installs_numeric: int = Field(
        ge=0
    )

    type: str


class ReviewCountsResponse(EdaBaseModel):
    """
    Complete result of EDA 04.
    """

    analysis_name: str = (
        "Review Counts"
    )

    analyzed_at: datetime

    statistics: ReviewStatistics

    categories: list[
        ReviewCategoryStatistics
    ] = Field(
        default_factory=list
    )

    top_applications: list[
        TopReviewedApplication
    ] = Field(
        default_factory=list
    )

    reviews_vs_installs: list[
        ReviewsVsInstalls
    ] = Field(
        default_factory=list
    )


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

class CompleteEdaAnalysis(EdaBaseModel):
    """
    Complete analysis containing all four EDAs.

    This is the main object returned by the analysis API
    and stored in Elasticsearch.
    """

    analysis_id: str | None = None

    analysis_date: datetime

    ratings_by_category: RatingsByCategoryResponse

    free_vs_paid: FreeVsPaidResponse

    install_distribution: InstallDistributionResponse

    review_counts: ReviewCountsResponse


# ============================================================
# EXPORT RECORD
# ============================================================

class ExportRecord(EdaBaseModel):
    """
    Metadata describing a generated analysis export.
    """

    id: str | None = None

    email: str

    date: datetime

    filename: str


# ============================================================
# PAGINATION
# ============================================================

class EdaAnalysisPage(EdaBaseModel):
    """
    Paginated EDA analysis history.
    """

    content: list[
        CompleteEdaAnalysis
    ] = Field(
        default_factory=list
    )

    page: int = Field(
        ge=0
    )

    size: int = Field(
        ge=1,
        le=100
    )

    total_elements: int = Field(
        ge=0
    )

    total_pages: int = Field(
        ge=0
    )


class ExportPage(EdaBaseModel):
    """
    Paginated export history.
    """

    content: list[
        ExportRecord
    ] = Field(
        default_factory=list
    )

    page: int = Field(
        ge=0
    )

    size: int = Field(
        ge=1,
        le=100
    )

    total_elements: int = Field(
        ge=0
    )

    total_pages: int = Field(
        ge=0
    )