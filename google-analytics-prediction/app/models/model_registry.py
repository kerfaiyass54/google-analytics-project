from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ModelRegistry(Base):
    __tablename__ = "prediction_model_registry"
    __table_args__ = (
        Index(
            "ix_prediction_registry_task_active",
            "task",
            "is_active",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    task: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    algorithm: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    artifact_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evaluation_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
