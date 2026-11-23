from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RatingPrediction(Base):
    __tablename__ = "predict_rating"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    app_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    input_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    predicted_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    model_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
