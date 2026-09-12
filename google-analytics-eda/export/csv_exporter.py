from __future__ import annotations

import csv
import io

from schema.eda_document import EdaDocument


class CsvExporter:

    @staticmethod
    def export(
        eda: EdaDocument,
    ) -> bytes:

        output = io.StringIO(
            newline=""
        )

        writer = csv.writer(
            output
        )

        writer.writerow(
            [
                "Analysis",
                "Data",
            ]
        )

        writer.writerow(
            [
                "Ratings by category",
                str(eda.ratings_by_category),
            ]
        )

        writer.writerow(
            [
                "Free vs paid",
                str(eda.free_vs_paid),
            ]
        )

        writer.writerow(
            [
                "Install distribution",
                str(eda.install_distribution),
            ]
        )

        writer.writerow(
            [
                "Review counts",
                str(eda.review_counts),
            ]
        )

        return output.getvalue().encode(
            "utf-8-sig"
        )