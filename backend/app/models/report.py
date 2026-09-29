"""Report model definitions for generated client-facing audit collateral (PDF, DOCX, HTML)."""
import enum
import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prospect import Prospect
    from app.models.score_result import ScoreResult


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reports"

    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("score_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    report_format: Mapped[ReportFormat] = mapped_column(
        Enum(
            ReportFormat,
            name="report_format_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ReportFormat.PDF,
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus,
            name="report_status_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ReportStatus.GENERATING,
        index=True,
    )

    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # In-browser HTML cache for instant rendering
    html_preview_cache: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="reports")
    score_result: Mapped["ScoreResult"] = relationship("ScoreResult", back_populates="reports")
