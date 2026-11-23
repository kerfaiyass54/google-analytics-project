from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile

from export.pdf_exporter import ChartZipExporter
from schema.eda_document import EdaDocument


def _eda_with_edge_cases() -> EdaDocument:
    return EdaDocument(
        eda_id="test-eda",
        email="test@example.com",
        date=datetime.now(timezone.utc),
        ratings_by_category={"categories": [{"category": "Tools", "average_rating": 4.2}]},
        free_vs_paid={"applications": [{"type": "FREE", "app_count": 5}], "free_percentage": 100, "paid_percentage": 0},
        install_distribution={"categories": [{"category": "Tools", "average_installs": 100}]},
        review_counts={
            "categories": [{"category": "Tools", "total_reviews": 10}],
            "reviews_vs_installs": [
                {"installs_numeric": 0, "reviews": 0},
                {"installs_numeric": 10, "reviews": 0},
                {"installs_numeric": None, "reviews": 5},
                {"installs_numeric": 10, "reviews": 5},
                {"installs_numeric": "not-a-number", "reviews": 20},
            ],
        },
    )


EXPECTED_CHARTS = {
    "ratings_by_category.png",
    "free_vs_paid_apps.png",
    "average_installs_by_category.png",
    "reviews_analysis.png",
}


def test_chart_zip_export_handles_zero_and_invalid_values():
    content = ChartZipExporter.export(_eda_with_edge_cases())
    with ZipFile(BytesIO(content)) as archive:
        assert set(archive.namelist()) == EXPECTED_CHARTS
        assert all(archive.read(name).startswith(b"\\x89PNG") for name in EXPECTED_CHARTS)


def test_chart_zip_export_handles_empty_analysis_sections():
    eda = _eda_with_edge_cases()
    eda.ratings_by_category = {}
    eda.free_vs_paid = {}
    eda.install_distribution = {}
    eda.review_counts = {}
    content = ChartZipExporter.export(eda)
    with ZipFile(BytesIO(content)) as archive:
        assert set(archive.namelist()) == EXPECTED_CHARTS
        assert all(len(archive.read(name)) > 100 for name in EXPECTED_CHARTS)
