from __future__ import annotations

import io
from collections.abc import Mapping
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from schema.eda_document import EdaDocument


class PdfExporter:
    """Create a multi-page analytical PDF with charts rendered by Matplotlib."""

    @staticmethod
    def export(eda: EdaDocument) -> bytes:
        output = io.BytesIO()
        sections = [
            ("Ratings by Category", eda.ratings_by_category),
            ("Free vs Paid", eda.free_vs_paid),
            ("Install Distribution", eda.install_distribution),
            ("Review Analysis", eda.review_counts),
        ]

        with PdfPages(output) as pdf:
            PdfExporter._add_cover(pdf, eda)
            PdfExporter._ratings_page(pdf, eda.ratings_by_category)
            PdfExporter._free_paid_page(pdf, eda.free_vs_paid)
            PdfExporter._install_page(pdf, eda.install_distribution)
            PdfExporter._reviews_page(pdf, eda.review_counts)

        return output.getvalue()

    @staticmethod
    def _add_cover(pdf: PdfPages, eda: EdaDocument) -> None:
        figure = plt.figure(figsize=(8.27, 11.69))
        figure.text(0.5, 0.82, "Google Play Store", ha="center", fontsize=23, weight="bold")
        figure.text(0.5, 0.75, "Exploratory Data Analysis Report", ha="center", fontsize=17)
        figure.text(0.5, 0.65, f"Generated: {eda.date.isoformat()}", ha="center", fontsize=10)
        figure.text(0.5, 0.61, f"EDA ID: {eda.eda_id or 'N/A'}", ha="center", fontsize=10)
        figure.text(0.5, 0.57, f"Owner: {eda.email}", ha="center", fontsize=10)
        figure.text(0.5, 0.35, "Report sections", ha="center", fontsize=13, weight="bold")
        figure.text(0.5, 0.30, "Ratings by Category • Free vs Paid • Install Distribution • Review Analysis", ha="center", fontsize=10)
        figure.axis("off")
        pdf.savefig(figure, bbox_inches="tight")
        plt.close(figure)

    @staticmethod
    def _new_page(title: str, subtitle: str = ""):
        figure, axis = plt.subplots(figsize=(11.69, 8.27))
        figure.suptitle(title, fontsize=16, weight="bold")
        if subtitle:
            figure.text(0.5, 0.92, subtitle, ha="center", fontsize=9)
        return figure, axis

    @staticmethod
    def _ratings_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        rows = data.get("categories", [])
        rows = [row for row in rows if row.get("average_rating") is not None]
        figure, axis = PdfExporter._new_page("Ratings by Category", "Average rating by app category")
        if rows:
            rows = sorted(rows, key=lambda row: row.get("average_rating", 0))[-20:]
            labels = [str(row.get("category", "")) for row in rows]
            values = [float(row.get("average_rating", 0)) for row in rows]
            axis.barh(labels, values)
            axis.set_xlim(0, 5)
            axis.set_xlabel("Average rating (1–5)")
            axis.grid(axis="x", alpha=0.25)
        else:
            axis.text(0.5, 0.5, "No category rating data available", ha="center", va="center")
            axis.axis("off")
        figure.tight_layout(rect=(0, 0, 1, 0.9))
        pdf.savefig(figure)
        plt.close(figure)

    @staticmethod
    def _free_paid_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        rows = data.get("applications", [])
        figure, axis = PdfExporter._new_page("Free vs Paid Applications")
        if rows:
            labels = [str(row.get("type", "")) for row in rows]
            counts = [int(row.get("app_count", 0) or 0) for row in rows]
            axis.bar(labels, counts)
            axis.set_ylabel("Application count")
            axis.grid(axis="y", alpha=0.25)
            axis.text(0.02, 0.96, f"Free: {data.get('free_percentage', 0)}%  |  Paid: {data.get('paid_percentage', 0)}%", transform=axis.transAxes, va="top")
        else:
            axis.text(0.5, 0.5, "No free/paid comparison data available", ha="center", va="center")
            axis.axis("off")
        figure.tight_layout(rect=(0, 0, 1, 0.9))
        pdf.savefig(figure)
        plt.close(figure)

    @staticmethod
    def _install_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        rows = data.get("categories", [])
        rows = [row for row in rows if row.get("average_installs") is not None]
        figure, axis = PdfExporter._new_page("Install Distribution", "Average installs by category (top categories)")
        if rows:
            rows = sorted(rows, key=lambda row: row.get("average_installs", 0))[-20:]
            labels = [str(row.get("category", "")) for row in rows]
            values = [float(row.get("average_installs", 0)) for row in rows]
            axis.barh(labels, values)
            axis.set_xlabel("Average installs")
            axis.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
            axis.grid(axis="x", alpha=0.25)
        else:
            axis.text(0.5, 0.5, "No install category data available", ha="center", va="center")
            axis.axis("off")
        figure.tight_layout(rect=(0, 0, 1, 0.9))
        pdf.savefig(figure)
        plt.close(figure)

    @staticmethod
    def _reviews_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        category_rows = data.get("categories", [])
        points = data.get("reviews_vs_installs", [])
        figure, axes = plt.subplots(1, 2, figsize=(11.69, 8.27))
        figure.suptitle("Review Analysis", fontsize=16, weight="bold")

        category_rows = sorted(category_rows, key=lambda row: row.get("total_reviews", 0))[-15:]
        if category_rows:
            axes[0].barh(
                [str(row.get("category", "")) for row in category_rows],
                [int(row.get("total_reviews", 0) or 0) for row in category_rows],
            )
            axes[0].set_title("Total reviews by category (top 15)")
            axes[0].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
            axes[0].grid(axis="x", alpha=0.25)
        else:
            axes[0].text(0.5, 0.5, "No category review data", ha="center", va="center")
            axes[0].axis("off")

        valid = [
            item for item in points
            if item.get("installs_numeric") is not None and item.get("reviews") is not None
        ]
        if valid:
            axes[1].scatter(
                [float(item["installs_numeric"]) for item in valid],
                [float(item["reviews"]) for item in valid],
                alpha=0.45,
                s=12,
            )
            axes[1].set_title("Reviews vs Installs")
            axes[1].set_xlabel("Installs")
            axes[1].set_ylabel("Reviews")
            axes[1].set_xscale("log")
            axes[1].set_yscale("log")
            axes[1].grid(alpha=0.25)
        else:
            axes[1].text(0.5, 0.5, "No reviews/installs data", ha="center", va="center")
            axes[1].axis("off")

        figure.tight_layout(rect=(0, 0, 1, 0.9))
        pdf.savefig(figure)
        plt.close(figure)
