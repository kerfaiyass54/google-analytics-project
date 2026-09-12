from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExportResponse(BaseModel):

    export_id: str

    eda_id: str

    email: str

    date: datetime

    file_type: str

    filename: str