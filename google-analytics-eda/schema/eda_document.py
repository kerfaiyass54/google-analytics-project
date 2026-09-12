from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EdaDocument(BaseModel):

    eda_id: str | None = None

    email: str

    date: datetime

    ratings_by_category: dict

    free_vs_paid: dict

    install_distribution: dict

    review_counts: dict