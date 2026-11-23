from __future__ import annotations

import io
from collections.abc import Mapping
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from schema.eda_document import EdaDocument


class ExcelExporter:
    """Create a multi-sheet workbook with clean tables for each EDA section."""

    @staticmethod
    def export(eda: EdaDocument) -> bytes:
        workbook = Workbook()
        overview = workbook.active
        overview.title = "Overview"

        overview.append(["Google Play Store EDA"])
        overview.append(["Generated at", eda.date.isoformat()])
        overview.append(["EDA ID", eda.eda_id or ""])
        overview.append(["Owner", eda.email])
        overview.append([])
        overview.append(["Analysis", "Key metric", "Value"])

        overview_sections = [
            ("Ratings", eda.ratings_by_category),
            ("Free vs Paid", eda.free_vs_paid),
            ("Install Distribution", eda.install_distribution),
            ("Review Analysis", eda.review_counts),
        ]
        for section, data in overview_sections:
            for key, value in ExcelExporter._summary_metrics(data):
                overview.append([section, key, value])

        ExcelExporter._format_table(overview, 6, overview.max_row, "Overview")
        ExcelExporter._format_sheet(overview, table_name="OverviewTable", header_row=6)

        sections = [
            ("Ratings", "Ratings by Category", eda.ratings_by_category),
            ("FreePaid", "Free vs Paid", eda.free_vs_paid),
            ("Installs", "Install Distribution", eda.install_distribution),
            ("Reviews", "Review Analysis", eda.review_counts),
        ]

        for sheet_name, title, data in sections:
            sheet = workbook.create_sheet(sheet_name)
            ExcelExporter._write_section(sheet, title, data)

        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    @staticmethod
    def _summary_metrics(data: Mapping[str, Any]) -> list[tuple[str, Any]]:
        rows: list[tuple[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                continue
            rows.append((key.replace("_", " ").title(), value))
        return rows

    @staticmethod
    def _write_section(sheet, title: str, data: Mapping[str, Any]) -> None:
        sheet.append([title])
        sheet.append(["Generated analysis section"])
        sheet.append([])
        row_count = 4

        for key, value in data.items():
            if isinstance(value, list) and value and all(isinstance(item, Mapping) for item in value):
                sheet.append([key.replace("_", " ").title()])
                headers = list(dict.fromkeys(
                    column for item in value for column in item.keys()
                ))
                header_row = sheet.max_row + 1
                sheet.append(headers)
                for item in value:
                    sheet.append([item.get(column, "") for column in headers])
                ExcelExporter._format_table(sheet, header_row, sheet.max_row, key)
                sheet.append([])
                row_count = sheet.max_row
            elif isinstance(value, Mapping):
                sheet.append([key.replace("_", " ").title()])
                sheet.append(["Metric", "Value"])
                header_row = sheet.max_row
                for metric, metric_value in value.items():
                    if isinstance(metric_value, (list, dict)):
                        continue
                    sheet.append([metric.replace("_", " ").title(), metric_value])
                ExcelExporter._format_table(sheet, header_row, sheet.max_row, key)
                sheet.append([])
                row_count = sheet.max_row
            elif isinstance(value, list):
                sheet.append([key.replace("_", " ").title()])
                sheet.append(["Value"])
                header_row = sheet.max_row
                for item in value:
                    sheet.append([str(item)])
                ExcelExporter._format_table(sheet, header_row, sheet.max_row, key)
                sheet.append([])
                row_count = sheet.max_row
            else:
                sheet.append([key.replace("_", " ").title(), value])
                row_count = sheet.max_row

        ExcelExporter._format_sheet(sheet, header_row=3)
        sheet.freeze_panes = "A4"

    @staticmethod
    def _format_table(sheet, header_row: int, end_row: int, title: str) -> None:
        if end_row <= header_row or sheet.max_column < 1:
            return
        end_col = sheet.max_column
        ref = f"A{header_row}:{get_column_letter(end_col)}{end_row}"
        safe_name = "".join(character for character in title.title() if character.isalnum())[:18] or "Data"
        table_name = f"{safe_name}Table{header_row}"
        try:
            table = Table(displayName=table_name, ref=ref)
            table.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False,
            )
            sheet.add_table(table)
        except ValueError:
            pass

    @staticmethod
    def _format_sheet(sheet, table_name: str | None = None, header_row: int = 1) -> None:
        sheet.freeze_panes = f"A{header_row + 1}"
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                if cell.row == 1:
                    cell.font = Font(bold=True, size=15)
                elif cell.row == header_row:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="1F4E78")
        for column_cells in sheet.columns:
            column_letter = get_column_letter(column_cells[0].column)
            max_length = max(
                (len(str(cell.value)) for cell in column_cells if cell.value is not None),
                default=8,
            )
            sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 42)
