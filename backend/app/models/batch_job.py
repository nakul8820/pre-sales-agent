"""BatchJob model definition for tracking bulk imports and batch analysis workflows."""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prospect import Prospect


class BatchSource(str, enum.Enum):
    MANUAL_BULK = "manual_bulk"
    HUBSPOT = "hubspot"
    EXCEL_UPLOAD = "excel_upload"


class BatchStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "batch_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[BatchSource] = mapped_column(
        Enum(
            BatchSource,
            name="batch_source_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=BatchSource.MANUAL_BULK,
    )
    status: Mapped[BatchStatus] = mapped_column(
        Enum(
            BatchStatus,
            name="batch_status_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=BatchStatus.QUEUED,
        index=True,
    )
    
    total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    flagged_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    prospects: Mapped[List["Prospect"]] = relationship(
        "Prospect", back_populates="batch_job", cascade="all, delete-orphan"
    )
