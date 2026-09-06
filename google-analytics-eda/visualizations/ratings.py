"""
Visualizations for EDA 01 - Ratings by Category.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd


def plot_average_rating_by_category(
    df: pd.DataFrame
) -> None:
    """
    Plot average application rating by category.
    """

    if df.empty:
        raise ValueError(
            "No data available for visualization."
        )

    plt.figure(figsize=(12, 8))

    sns.barplot(
        data=df,
        x="average_rating",
        y="category"
    )

    plt.title(
        "Average Google Play Rating by Category"
    )

    plt.xlabel("Average Rating")

    plt.ylabel("Category")

    plt.xlim(0, 5)

    plt.tight_layout()

    plt.show()