"""Audit model definitions for tracking multi-channel analysis results."""
import uuid
from sqlalchemy import Float, ForeignKey, JSON, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Audit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audits"

    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Aggregated Scores (0 - 100)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    performance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    seo_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_gen_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ui_ux_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    broken_links_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Moderation
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moderation_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Detailed Audit Payloads
    pagespeed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    semrush_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    crawler_lead_gen_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    crawler_broken_links_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    crawler_ui_ux_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    critical_focus_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
