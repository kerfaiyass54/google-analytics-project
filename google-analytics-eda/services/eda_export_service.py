"""
EDA export service.

Responsibilities:
    - Execute the four Google Play Store EDAs
    - Build visualization-ready DataFrames
    - Generate CSV exports
    - Generate XLSX exports
    - Generate PDF reports
    - Persist export metadata into Elasticsearch

The service does NOT:
    - access PostgreSQL directly
    - execute SQL queries directly
    - calculate EDA statistics directly
    - manage Elasticsearch documents directly

Architecture:

    API
     |
     v
    EdaExportService
     |
     +----> EdaAnalysisService
     |
     +----> EdaVisualizationService
     |
     +----> File generation
     |
     +----> ExportRepository
                  |
                  v
            Elasticsearch
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from services.eda_service import EdaAnalysisService
from elastic.export_repository import ExportRepository
from schema.eda import ExportRecord
from visualizations.eda_visualization_service import (
    EdaVisualizationService,
)


# ============================================================
# TYPES
# ============================================================

ExportFormat = Literal[
    "csv",
    "xlsx",
    "pdf",
]


DataFrameMap = dict[
    str,
    pd.DataFrame,
]


# ============================================================
# SERVICE
# ============================================================

class EdaExportService:
    """
    Application service responsible for generating
    downloadable EDA reports.
    """

    def __init__(
        self,
        analysis_service: EdaAnalysisService | None = None,
        export_repository: ExportRepository | None = None,
        visualization_service: EdaVisualizationService | None = None,
    ) -> None:

        self._analysis_service = (
            analysis_service
            or EdaAnalysisService()
        )

        self._export_repository = (
            export_repository
            or ExportRepository()
        )

        self._visualization_service = (
            visualization_service
            or EdaVisualizationService()
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def export(
        self,
        email: str,
        file_format: ExportFormat,
        output_directory: str | Path = "exports",
    ) -> ExportRecord:
        """
        Execute the complete EDA pipeline and generate
        the requested export.

        Pipeline:

            1. Validate request
            2. Run analysis
            3. Build visualization DataFrames
            4. Generate file
            5. Persist export metadata
            6. Return ExportRecord

        Args:
            email:
                Email address of the user requesting
                the export.

            file_format:
                csv, xlsx or pdf.

            output_directory:
                Directory where the generated file
                will be stored.

        Returns:
            ExportRecord containing:

                - Elasticsearch ID
                - user email
                - export date
                - filename
        """

        # ----------------------------------------------------
        # Normalize input
        # ----------------------------------------------------

        normalized_email = email.strip()

        normalized_format = (
            file_format.strip().lower()
        )

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        self._validate_email(
            normalized_email
        )

        self._validate_format(
            normalized_format
        )

        # ----------------------------------------------------
        # Prepare output directory
        # ----------------------------------------------------

        output_path = Path(
            output_directory
        )

        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ----------------------------------------------------
        # Execute EDA analysis
        # ----------------------------------------------------

        analysis = (
            self._analysis_service.run()
        )

        # ----------------------------------------------------
        # Build visualization data
        #
        # This is intentionally executed ONLY when
        # the user requests an export.
        # ----------------------------------------------------

        dataframes = (
            self._visualization_service.build_all(
                analysis
            )
        )

        summary = (
            self._visualization_service.build_summary(
                analysis
            )
        )

        # ----------------------------------------------------
        # Generate timestamp
        # ----------------------------------------------------

        timestamp = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------------
        # Generate filename
        # ----------------------------------------------------

        filename = (
            self._build_filename(
                timestamp=timestamp,
                file_format=normalized_format,
            )
        )

        file_path = (
            output_path / filename
        )

        # ----------------------------------------------------
        # Generate physical file
        # ----------------------------------------------------

        self._generate_file(
            file_format=normalized_format,
            analysis=analysis,
            summary=summary,
            dataframes=dataframes,
            file_path=file_path,
        )

        # ----------------------------------------------------
        # Safety check
        # ----------------------------------------------------

        if not file_path.exists():

            raise RuntimeError(
                "Export file was not created successfully: "
                f"{file_path}"
            )

        # ----------------------------------------------------
        # Persist metadata in Elasticsearch
        #
        # IMPORTANT:
        # We save the record ONLY after successful file
        # generation.
        # ----------------------------------------------------

        record = ExportRecord(
            email=normalized_email,
            date=timestamp,
            filename=filename,
        )

        saved_record = (
            self._export_repository.save(
                record
            )
        )

        return saved_record

    # ========================================================
    # FILE GENERATION DISPATCHER
    # ========================================================

    @staticmethod
    def _generate_file(
        file_format: str,
        analysis,
        summary: pd.DataFrame,
        dataframes: DataFrameMap,
        file_path: Path,
    ) -> None:
        """
        Dispatch file generation based on the requested
        format.
        """

        if file_format == "csv":

            EdaExportService._generate_csv(
                dataframes=dataframes,
                file_path=file_path,
            )

            return

        if file_format == "xlsx":

            EdaExportService._generate_excel(
                summary=summary,
                dataframes=dataframes,
                file_path=file_path,
            )

            return

        if file_format == "pdf":

            EdaExportService._generate_pdf(
                analysis=analysis,
                summary=summary,
                dataframes=dataframes,
                file_path=file_path,
            )

            return

        raise ValueError(
            f"Unsupported export format: {file_format}"
        )

    # ========================================================
    # CSV
    # ========================================================

    @staticmethod
    def _generate_csv(
        dataframes: DataFrameMap,
        file_path: Path,
    ) -> None:
        """
        Generate a CSV report containing all four EDAs.

        CSV does not support multiple worksheets,
        therefore each EDA is separated by a section marker.
        """

        with file_path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as file:

            for name, dataframe in dataframes.items():

                file.write(
                    f"\n===== {name.upper()} =====\n"
                )

                dataframe.to_csv(
                    file,
                    index=False,
                )

                file.write("\n")

    # ========================================================
    # XLSX
    # ========================================================

    @staticmethod
    def _generate_excel(
        summary: pd.DataFrame,
        dataframes: DataFrameMap,
        file_path: Path,
    ) -> None:
        """
        Generate a multi-sheet Excel report.

        Sheets:

            1. Summary
            2. Ratings by Category
            3. Free vs Paid
            4. Install Distribution
            5. Review Counts
        """

        required_keys = {
            "ratings_by_category",
            "free_vs_paid",
            "install_distribution",
            "review_counts",
        }

        missing_keys = (
            required_keys
            - dataframes.keys()
        )

        if missing_keys:

            raise ValueError(
                "Missing visualization DataFrames: "
                f"{sorted(missing_keys)}"
            )

        with pd.ExcelWriter(
            file_path,
            engine="openpyxl",
        ) as writer:

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

            summary.to_excel(
                writer,
                sheet_name="Summary",
                index=False,
            )

            # ------------------------------------------------
            # EDA 01
            # ------------------------------------------------

            dataframes[
                "ratings_by_category"
            ].to_excel(
                writer,
                sheet_name="Ratings by Category",
                index=False,
            )

            # ------------------------------------------------
            # EDA 02
            # ------------------------------------------------

            dataframes[
                "free_vs_paid"
            ].to_excel(
                writer,
                sheet_name="Free vs Paid",
                index=False,
            )

            # ------------------------------------------------
            # EDA 03
            # ------------------------------------------------

            dataframes[
                "install_distribution"
            ].to_excel(
                writer,
                sheet_name="Install Distribution",
                index=False,
            )

            # ------------------------------------------------
            # EDA 04
            # ------------------------------------------------

            dataframes[
                "review_counts"
            ].to_excel(
                writer,
                sheet_name="Review Counts",
                index=False,
            )

    # ========================================================
    # PDF
    # ========================================================

    @staticmethod
    def _generate_pdf(
        analysis,
        summary: pd.DataFrame,
        dataframes: DataFrameMap,
        file_path: Path,
    ) -> None:
        """
        Generate a PDF analytical report.

        Sections:

            - Report title
            - Analysis date
            - Summary
            - Ratings by Category
            - Free vs Paid
            - Install Distribution
            - Review Counts
        """

        document = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )

        styles = (
            getSampleStyleSheet()
        )

        elements: list = []

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        elements.append(
            Paragraph(
                "Google Play Store EDA Report",
                styles["Title"],
            )
        )

        elements.append(
            Spacer(
                1,
                8,
            )
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        elements.append(
            Paragraph(
                (
                    "Analysis date: "
                    f"{analysis.analysis_date}"
                ),
                styles["BodyText"],
            )
        )

        elements.append(
            Spacer(
                1,
                15,
            )
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        elements.append(
            Paragraph(
                "Summary",
                styles["Heading1"],
            )
        )

        EdaExportService._append_dataframe_table(
            elements=elements,
            dataframe=summary,
            styles=styles,
            max_rows=10,
            max_columns=8,
        )

        # ----------------------------------------------------
        # EDA SECTIONS
        # ----------------------------------------------------

        sections = [
            (
                "Ratings by Category",
                "ratings_by_category",
            ),
            (
                "Free vs Paid",
                "free_vs_paid",
            ),
            (
                "Install Distribution",
                "install_distribution",
            ),
            (
                "Review Counts",
                "review_counts",
            ),
        ]

        for title, key in sections:

            dataframe = dataframes.get(
                key
            )

            if dataframe is None:

                raise ValueError(
                    "Visualization DataFrame "
                    f"'{key}' is missing."
                )

            elements.append(
                PageBreak()
            )

            elements.append(
                Paragraph(
                    title,
                    styles["Heading1"],
                )
            )

            elements.append(
                Spacer(
                    1,
                    8,
                )
            )

            EdaExportService._append_dataframe_table(
                elements=elements,
                dataframe=dataframe,
                styles=styles,
                max_rows=40,
                max_columns=8,
            )

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        document.build(
            elements
        )

    # ========================================================
    # PDF TABLE
    # ========================================================

    @staticmethod
    def _append_dataframe_table(
        elements: list,
        dataframe: pd.DataFrame,
        styles,
        max_rows: int,
        max_columns: int,
    ) -> None:
        """
        Convert a DataFrame into a ReportLab table.
        """

        if dataframe.empty:

            elements.append(
                Paragraph(
                    "No data available.",
                    styles["BodyText"],
                )
            )

            return

        # ----------------------------------------------------
        # Limit rows
        # ----------------------------------------------------

        dataframe = (
            dataframe
            .head(max_rows)
            .copy()
        )

        # ----------------------------------------------------
        # Limit columns
        # ----------------------------------------------------

        columns = list(
            dataframe.columns
        )[:max_columns]

        if not columns:

            elements.append(
                Paragraph(
                    "No data available.",
                    styles["BodyText"],
                )
            )

            return

        dataframe = dataframe[
            columns
        ]

        # ----------------------------------------------------
        # Convert values to strings
        # ----------------------------------------------------

        dataframe = (
            dataframe
            .fillna("")
            .astype(str)
        )

        # ----------------------------------------------------
        # Build table data
        # ----------------------------------------------------

        table_data = [
            columns
        ]

        table_data.extend(
            dataframe.values.tolist()
        )

        # ----------------------------------------------------
        # Create table
        # ----------------------------------------------------

        table = Table(
            table_data,
            repeatRows=1,
        )

        # ----------------------------------------------------
        # Style
        # ----------------------------------------------------

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.black,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        3,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3,
                    ),
                ]
            )
        )

        elements.append(
            table
        )

    # ========================================================
    # FILENAME
    # ========================================================

    @staticmethod
    def _build_filename(
        timestamp: datetime,
        file_format: str,
    ) -> str:
        """
        Build a unique and filesystem-safe filename.

        Example:

            google_play_eda_20260906_161530.xlsx
        """

        timestamp_string = (
            timestamp.strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

        return (
            "google_play_eda_"
            f"{timestamp_string}."
            f"{file_format}"
        )

    # ========================================================
    # VALIDATION — EMAIL
    # ========================================================

    @staticmethod
    def _validate_email(
        email: str,
    ) -> None:
        """
        Perform basic email validation.

        Full validation should also be handled
        by the FastAPI/Pydantic request schema.
        """

        if not email:

            raise ValueError(
                "Email is required."
            )

        if "@" not in email:

            raise ValueError(
                "A valid email address is required."
            )

    # ========================================================
    # VALIDATION — FORMAT
    # ========================================================

    @staticmethod
    def _validate_format(
        file_format: str,
    ) -> None:
        """
        Validate the requested export format.
        """

        supported_formats = {
            "csv",
            "xlsx",
            "pdf",
        }

        if file_format not in supported_formats:

            raise ValueError(
                "Unsupported export format. "
                "Supported formats: "
                "csv, xlsx, pdf."
            )