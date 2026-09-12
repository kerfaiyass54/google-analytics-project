from __future__ import annotations

import io
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from schema.eda_document import EdaDocument


class PdfExporter:

    @staticmethod
    def export(
        eda: EdaDocument,
    ) -> bytes:

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        body_style = styles["BodyText"]

        elements = []

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------

        elements.append(
            Paragraph(
                "Google Play Store — EDA Analysis",
                title_style,
            )
        )

        elements.append(
            Spacer(
                1,
                8 * mm,
            )
        )

        # --------------------------------------------------------
        # Metadata
        # --------------------------------------------------------

        metadata = [
            ["EDA ID", eda.eda_id or ""],
            ["Email", eda.email],
            ["Date", eda.date.isoformat()],
        ]

        metadata_table = Table(
            metadata,
            colWidths=[
                35 * mm,
                140 * mm,
            ],
        )

        metadata_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        None,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        elements.append(
            metadata_table
        )

        elements.append(
            Spacer(
                1,
                8 * mm,
            )
        )

        # --------------------------------------------------------
        # Analysis sections
        # --------------------------------------------------------

        sections = [
            (
                "Ratings by category",
                eda.ratings_by_category,
            ),
            (
                "Free vs paid",
                eda.free_vs_paid,
            ),
            (
                "Install distribution",
                eda.install_distribution,
            ),
            (
                "Review counts",
                eda.review_counts,
            ),
        ]

        for title, data in sections:

            elements.append(
                Paragraph(
                    title,
                    heading_style,
                )
            )

            elements.append(
                Spacer(
                    1,
                    3 * mm,
                )
            )

            formatted_data = json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            )

            elements.append(
                Paragraph(
                    formatted_data
                    .replace(
                        "\n",
                        "<br/>",
                    )
                    .replace(
                        " ",
                        "&nbsp;",
                    ),
                    body_style,
                )
            )

            elements.append(
                Spacer(
                    1,
                    6 * mm,
                )
            )

        document.build(
            elements
        )

        return buffer.getvalue()