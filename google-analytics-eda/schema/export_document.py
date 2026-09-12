from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExportDocument(BaseModel):

    export_id: str | None = None

    eda_id: str

    email: str

    date: datetime

    file_type: str

    filename: str

    content: str