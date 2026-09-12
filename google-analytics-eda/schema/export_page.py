from __future__ import annotations

from pydantic import BaseModel

from schema.export_response import ExportResponse


class ExportPage(BaseModel):

    content: list[ExportResponse]

    page: int

    size: int

    total_elements: int

    total_pages: int