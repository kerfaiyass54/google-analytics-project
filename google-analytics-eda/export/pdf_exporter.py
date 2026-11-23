from __future__ import annotations

import io
import math
import zipfile
from collections.abc import Mapping
from threading import Lock
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from schema.eda_document import EdaDocument

_CHART_EXPORT_LOCK = Lock()


class ChartZipExporter:
    """Generate a ZIP of Matplotlib PNG charts for an EDA document."""

    @staticmethod
    def export(eda: EdaDocument) -> bytes:
        with _CHART_EXPORT_LOCK:
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                ChartZipExporter._ratings(archive, eda.ratings_by_category)
                ChartZipExporter._free_paid(archive, eda.free_vs_paid)
                ChartZipExporter._installs(archive, eda.install_distribution)
                ChartZipExporter._reviews(archive, eda.review_counts)
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
    def _save(archive: zipfile.ZipFile, name: str, figure) -> None:
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", dpi=160, bbox_inches="tight")
        archive.writestr(name, buffer.getvalue())

    @staticmethod
    def _ratings(archive: zipfile.ZipFile, data: Mapping[str, Any]) -> None:
        rows = [r for r in ChartZipExporter._rows(data, "categories") if ChartZipExporter._number(r.get("average_rating")) is not None]
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        try:
            ax.set_title("Ratings by Category")
            if rows:
                rows = sorted(rows, key=lambda r: ChartZipExporter._number(r.get("average_rating")) or 0)[-20:]
                ax.barh([str(r.get("category", "")) for r in rows], [ChartZipExporter._number(r.get("average_rating")) or 0 for r in rows])
                ax.set_xlim(0, 5)
                ax.set_xlabel("Average rating (1–5)")
                ax.grid(axis="x", alpha=0.25)
            else:
                ax.text(0.5, 0.5, "No category rating data available", ha="center", va="center")
                ax.axis("off")
            fig.tight_layout()
            ChartZipExporter._save(archive, "ratings_by_category.png", fig)
        finally:
            plt.close(fig)

    @staticmethod
    def _free_paid(archive: zipfile.ZipFile, data: Mapping[str, Any]) -> None:
        rows = ChartZipExporter._rows(data, "applications")
        fig, ax = plt.subplots(figsize=(10, 6))
        try:
            ax.set_title("Free vs Paid Applications")
            if rows:
                ax.bar([str(r.get("type", "")) for r in rows], [max(0, int(ChartZipExporter._number(r.get("app_count")) or 0)) for r in rows])
                ax.set_ylabel("Application count")
                ax.grid(axis="y", alpha=0.25)
                free = ChartZipExporter._number(data.get("free_percentage")) or 0
                paid = ChartZipExporter._number(data.get("paid_percentage")) or 0
                ax.text(0.02, 0.96, f"Free: {free:g}% | Paid: {paid:g}%", transform=ax.transAxes, va="top")
            else:
                ax.text(0.5, 0.5, "No free/paid comparison data available", ha="center", va="center")
                ax.axis("off")
            fig.tight_layout()
            ChartZipExporter._save(archive, "free_vs_paid_apps.png", fig)
        finally:
            plt.close(fig)

    @staticmethod
    def _installs(archive: zipfile.ZipFile, data: Mapping[str, Any]) -> None:
        rows = [r for r in ChartZipExporter._rows(data, "categories") if ChartZipExporter._number(r.get("average_installs")) is not None]
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        try:
            ax.set_title("Average Installs by Category")
            if rows:
                rows = sorted(rows, key=lambda r: ChartZipExporter._number(r.get("average_installs")) or 0)[-20:]
                ax.barh([str(r.get("category", "")) for r in rows], [ChartZipExporter._number(r.get("average_installs")) or 0 for r in rows])
                ax.set_xlabel("Average installs")
                ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
                ax.grid(axis="x", alpha=0.25)
            else:
                ax.text(0.5, 0.5, "No install category data available", ha="center", va="center")
                ax.axis("off")
            fig.tight_layout()
            ChartZipExporter._save(archive, "average_installs_by_category.png", fig)
        finally:
            plt.close(fig)

    @staticmethod
    def _reviews(archive: zipfile.ZipFile, data: Mapping[str, Any]) -> None:
        categories = ChartZipExporter._rows(data, "categories")
        points = ChartZipExporter._rows(data, "reviews_vs_installs")
        fig, axes = plt.subplots(1, 2, figsize=(11.69, 8.27))
        fig.suptitle("Review Analysis")
        try:
            categories = sorted(categories, key=lambda r: ChartZipExporter._number(r.get("total_reviews")) or 0)[-15:]
            if categories:
                axes[0].barh([str(r.get("category", "")) for r in categories], [max(0, ChartZipExporter._number(r.get("total_reviews")) or 0) for r in categories])
                axes[0].set_title("Reviews by Category (Top 15)")
                axes[0].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
                axes[0].grid(axis="x", alpha=0.25)
            else:
                axes[0].text(0.5, 0.5, "No category review data", ha="center", va="center")
                axes[0].axis("off")
            valid = []
            for item in points:
                installs = ChartZipExporter._number(item.get("installs_numeric"))
                reviews = ChartZipExporter._number(item.get("reviews"))
                if installs is not None and reviews is not None and installs > 0 and reviews > 0:
                    valid.append((installs, reviews))
            if valid:
                axes[1].scatter([p[0] for p in valid], [p[1] for p in valid], alpha=0.45, s=12)
                axes[1].set_title("Reviews vs Installs")
                axes[1].set_xlabel("Installs")
                axes[1].set_ylabel("Reviews")
                axes[1].set_xscale("log")
                axes[1].set_yscale("log")
                axes[1].grid(alpha=0.25)
            else:
                axes[1].text(0.5, 0.5, "No positive reviews/installs data", ha="center", va="center")
                axes[1].axis("off")
            fig.tight_layout()
            ChartZipExporter._save(archive, "reviews_analysis.png", fig)
        finally:
            plt.close(fig)
