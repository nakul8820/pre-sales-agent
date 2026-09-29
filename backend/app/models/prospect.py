"""Prospect model definitions for tracking client company targets and auditing lifecycle."""
import enum
import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.batch_job import BatchJob
    from app.models.score_result import ScoreResult
    from app.models.rating_flag import RatingFlag
    from app.models.report import Report


class ProspectSource(str, enum.Enum):
    MANUAL = "manual"
    HUBSPOT = "hubspot"
    EXCEL_UPLOAD = "excel_upload"


class ProspectStatus(str, enum.Enum):
    PENDING = "pending"
    CRAWLING = "crawling"
    AUDITING = "auditing"
    SCORING = "scoring"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"
    MODERATION_FLAGGED = "moderation_flagged"


class Prospect(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "prospects"

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str] = mapped_column(String(512), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    source: Mapped[ProspectSource] = mapped_column(
        Enum(
            ProspectSource,
            name="prospect_source_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ProspectSource.MANUAL,
        nullable=False,
    )
    status: Mapped[ProspectStatus] = mapped_column(
        Enum(
            ProspectStatus,
            name="prospect_status_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ProspectStatus.PENDING,
        nullable=False,
        index=True,
    )

    hubspot_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batch_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    batch_job: Mapped[Optional["BatchJob"]] = relationship("BatchJob", back_populates="prospects")
    score_result: Mapped[Optional["ScoreResult"]] = relationship(
        "ScoreResult", back_populates="prospect", uselist=False, cascade="all, delete-orphan"
    )
    rating_flags: Mapped[List["RatingFlag"]] = relationship(
        "RatingFlag", back_populates="prospect", cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="prospect", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_prospect_domain_source", "domain", "source"),
    )
