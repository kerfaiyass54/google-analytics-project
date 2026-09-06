"""
Visualizations for EDA 02 - Free vs Paid Applications.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd


# ============================================================
# Application Distribution
# ============================================================

def plot_free_paid_distribution(
    df: pd.DataFrame
) -> None:
    """
    Plot the number of free and paid applications.
    """

    if df.empty:
        raise ValueError(
            "No data available for visualization."
        )

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=df,
        x="type",
        y="app_count"
    )

    plt.title(
        "Free vs Paid Applications"
    )

    plt.xlabel(
        "Application Type"
    )

    plt.ylabel(
        "Number of Applications"
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# Percentage Distribution
# ============================================================

def plot_free_paid_percentage(
    df: pd.DataFrame
) -> None:
    """
    Plot the percentage distribution of free and paid apps.
    """

    if df.empty:
        raise ValueError(
            "No data available for visualization."
        )

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=df,
        x="type",
        y="percentage"
    )

    plt.title(
        "Free vs Paid Application Percentage"
    )

    plt.xlabel(
        "Application Type"
    )

    plt.ylabel(
        "Percentage (%)"
    )

    plt.ylim(0, 100)

    plt.tight_layout()

    plt.show()


# ============================================================
# Rating Comparison
# ============================================================

def plot_rating_comparison(
    df: pd.DataFrame
) -> None:
    """
    Compare average ratings between free and paid apps.
    """

    if df.empty:
        raise ValueError(
            "No rating data available."
        )

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=df,
        x="type",
        y="average_rating"
    )

    plt.title(
        "Average Rating: Free vs Paid"
    )

    plt.xlabel(
        "Application Type"
    )

    plt.ylabel(
        "Average Rating"
    )

    plt.ylim(0, 5)

    plt.tight_layout()

    plt.show()


# ============================================================
# Review Comparison
# ============================================================

def plot_review_comparison(
    df: pd.DataFrame
) -> None:
    """
    Compare average review counts between free and paid apps.
    """

    if df.empty:
        raise ValueError(
            "No review data available."
        )

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=df,
        x="type",
        y="average_reviews"
    )

    plt.title(
        "Average Reviews: Free vs Paid"
    )

    plt.xlabel(
        "Application Type"
    )

    plt.ylabel(
        "Average Number of Reviews"
    )

    plt.yscale("log")

    plt.tight_layout()

    plt.show()