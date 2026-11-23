from datetime import datetime, timezone

from export.pdf_exporter import PdfExporter
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


def test_pdf_export_handles_zero_and_invalid_log_chart_values():
    pdf = PdfExporter.export(_eda_with_edge_cases())

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_pdf_export_handles_empty_analysis_sections():
    eda = _eda_with_edge_cases()
    eda.ratings_by_category = {}
    eda.free_vs_paid = {}
    eda.install_distribution = {}
    eda.review_counts = {}

    pdf = PdfExporter.export(eda)

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
