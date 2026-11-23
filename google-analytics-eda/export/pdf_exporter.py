from __future__ import annotations

import io
import math
from threading import Lock
from collections.abc import Mapping
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from schema.eda_document import EdaDocument


_PDF_RENDER_LOCK = Lock()


class PdfExporter:
    """Create a multi-page analytical PDF with charts rendered by Matplotlib."""

    @staticmethod
    def export(eda: EdaDocument) -> bytes:
        # Matplotlib uses shared process-level state; serialize PDF rendering
        # to avoid cross-request interference when FastAPI handles exports in threads.
        with _PDF_RENDER_LOCK:
            output = io.BytesIO()
            with PdfPages(output) as pdf:
                PdfExporter._add_cover(pdf, eda)
                PdfExporter._ratings_page(pdf, eda.ratings_by_category)
                PdfExporter._free_paid_page(pdf, eda.free_vs_paid)
                PdfExporter._install_page(pdf, eda.install_distribution)
                PdfExporter._reviews_page(pdf, eda.review_counts)
            return output.getvalue()

    @staticmethod
    def _rows(data: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
        rows = data.get(key, [])
        return [row for row in rows if isinstance(row, Mapping)] if isinstance(rows, list) else []

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _add_cover(pdf: PdfPages, eda: EdaDocument) -> None:
        figure = plt.figure(figsize=(8.27, 11.69))
        try:
            figure.text(0.5, 0.82, "Google Play Store", ha="center", fontsize=23, weight="bold")
            figure.text(0.5, 0.75, "Exploratory Data Analysis Report", ha="center", fontsize=17)
            figure.text(0.5, 0.65, f"Generated: {eda.date.isoformat()}", ha="center", fontsize=10)
            figure.text(0.5, 0.61, f"EDA ID: {eda.eda_id or 'N/A'}", ha="center", fontsize=10)
            figure.text(0.5, 0.57, f"Owner: {eda.email}", ha="center", fontsize=10)
            figure.text(0.5, 0.35, "Report sections", ha="center", fontsize=13, weight="bold")
            figure.text(0.5, 0.30, "Ratings by Category • Free vs Paid • Install Distribution • Review Analysis", ha="center", fontsize=10)
            figure.axis("off")
            pdf.savefig(figure, bbox_inches="tight")
        finally:
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
        rows = [
            row for row in PdfExporter._rows(data, "categories")
            if PdfExporter._number(row.get("average_rating")) is not None
        ]
        figure, axis = PdfExporter._new_page("Ratings by Category", "Average rating by app category")
        try:
            if rows:
                rows = sorted(rows, key=lambda row: PdfExporter._number(row.get("average_rating")) or 0)[-20:]
                labels = [str(row.get("category", "")) for row in rows]
                values = [PdfExporter._number(row.get("average_rating")) or 0 for row in rows]
                axis.barh(labels, values)
                axis.set_xlim(0, 5)
                axis.set_xlabel("Average rating (1–5)")
                axis.grid(axis="x", alpha=0.25)
            else:
                axis.text(0.5, 0.5, "No category rating data available", ha="center", va="center")
                axis.axis("off")
            figure.tight_layout(rect=(0, 0, 1, 0.9))
            pdf.savefig(figure)
        finally:
            plt.close(figure)

    @staticmethod
    def _free_paid_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        rows = PdfExporter._rows(data, "applications")
        figure, axis = PdfExporter._new_page("Free vs Paid Applications")
        try:
            if rows:
                labels = [str(row.get("type", "")) for row in rows]
                counts = [max(0, int(PdfExporter._number(row.get("app_count")) or 0)) for row in rows]
                axis.bar(labels, counts)
                axis.set_ylabel("Application count")
                axis.grid(axis="y", alpha=0.25)
                free_pct = PdfExporter._number(data.get("free_percentage")) or 0
                paid_pct = PdfExporter._number(data.get("paid_percentage")) or 0
                axis.text(0.02, 0.96, f"Free: {free_pct:g}%  |  Paid: {paid_pct:g}%", transform=axis.transAxes, va="top")
            else:
                axis.text(0.5, 0.5, "No free/paid comparison data available", ha="center", va="center")
                axis.axis("off")
            figure.tight_layout(rect=(0, 0, 1, 0.9))
            pdf.savefig(figure)
        finally:
            plt.close(figure)

    @staticmethod
    def _install_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        rows = [
            row for row in PdfExporter._rows(data, "categories")
            if PdfExporter._number(row.get("average_installs")) is not None
        ]
        figure, axis = PdfExporter._new_page("Install Distribution", "Average installs by category (top categories)")
        try:
            if rows:
                rows = sorted(rows, key=lambda row: PdfExporter._number(row.get("average_installs")) or 0)[-20:]
                labels = [str(row.get("category", "")) for row in rows]
                values = [PdfExporter._number(row.get("average_installs")) or 0 for row in rows]
                axis.barh(labels, values)
                axis.set_xlabel("Average installs")
                axis.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
                axis.grid(axis="x", alpha=0.25)
            else:
                axis.text(0.5, 0.5, "No install category data available", ha="center", va="center")
                axis.axis("off")
            figure.tight_layout(rect=(0, 0, 1, 0.9))
            pdf.savefig(figure)
        finally:
            plt.close(figure)

    @staticmethod
    def _reviews_page(pdf: PdfPages, data: Mapping[str, Any]) -> None:
        category_rows = PdfExporter._rows(data, "categories")
        points = PdfExporter._rows(data, "reviews_vs_installs")
        figure, axes = plt.subplots(1, 2, figsize=(11.69, 8.27))
        figure.suptitle("Review Analysis", fontsize=16, weight="bold")
        try:
            category_rows = sorted(
                category_rows,
                key=lambda row: PdfExporter._number(row.get("total_reviews")) or 0,
            )[-15:]
            if category_rows:
                axes[0].barh(
                    [str(row.get("category", "")) for row in category_rows],
                    [max(0, PdfExporter._number(row.get("total_reviews")) or 0) for row in category_rows],
                )
                axes[0].set_title("Total reviews by category (top 15)")
                axes[0].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
                axes[0].grid(axis="x", alpha=0.25)
            else:
                axes[0].text(0.5, 0.5, "No category review data", ha="center", va="center")
                axes[0].axis("off")

            # Log axes require strictly positive values. Exclude zero and malformed
            # records so a valid EDA export does not fail during PDF rendering.
            valid = []
            for item in points:
                installs = PdfExporter._number(item.get("installs_numeric"))
                reviews = PdfExporter._number(item.get("reviews"))
                if installs is not None and reviews is not None and installs > 0 and reviews > 0:
                    valid.append((installs, reviews))

            if valid:
                axes[1].scatter(
                    [item[0] for item in valid],
                    [item[1] for item in valid],
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
                axes[1].text(0.5, 0.5, "No positive reviews/installs data", ha="center", va="center")
                axes[1].axis("off")

            figure.tight_layout(rect=(0, 0, 1, 0.9))
            pdf.savefig(figure)
        finally:
            plt.close(figure)
