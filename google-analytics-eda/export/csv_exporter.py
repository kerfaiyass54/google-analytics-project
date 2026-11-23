from __future__ import annotations

import csv
import io
from collections.abc import Mapping
from typing import Any

from schema.eda_document import EdaDocument


class CsvExporter:

    @staticmethod
    def export(
        eda: EdaDocument,
    ) -> bytes:

        output = io.StringIO(
            newline=""
        )

        writer = csv.writer(output)

        sections = (
            ("Ratings by category", eda.ratings_by_category),
            ("Free vs paid", eda.free_vs_paid),
            ("Install distribution", eda.install_distribution),
            ("Review counts", eda.review_counts),
        )

        for title, data in sections:
            rows = CsvExporter._flatten_mapping(data)
            if not rows:
                writer.writerow(["Analysis", "Key", "Value"])
                writer.writerow([title, "", ""])
                continue

            writer.writerow(["Analysis", "Key", "Value"])
            for key, value in rows:
                writer.writerow([title, key, value])

            writer.writerow([])

        return output.getvalue().encode(
            "utf-8-sig"
        )

    @staticmethod
    def _flatten_mapping(
        data: Mapping[str, Any],
        prefix: str = "",
    ) -> list[tuple[str, Any]]:
        rows: list[tuple[str, Any]] = []

        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else str(key)

            if isinstance(value, Mapping):
                rows.extend(
                    CsvExporter._flatten_mapping(
                        value,
                        prefix=path,
                    )
                )
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    item_path = f"{path}[{index}]"
                    if isinstance(item, Mapping):
                        rows.extend(
                            CsvExporter._flatten_mapping(
                                item,
                                prefix=item_path,
                            )
                        )
                    else:
                        rows.append((item_path, item))
            else:
                rows.append((path, value))

        return rows