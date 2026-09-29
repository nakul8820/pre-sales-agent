"""ScoreResult model for persisting weighted audit scores and raw telemetry dumps."""
import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prospect import Prospect
    from app.models.report import Report


class ScoreResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "score_results"

    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Aggregated & Category Scores (Scale: 0.0 – 100.0)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    performance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lead_gen_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ui_ux_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    broken_links_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Weights snapshot used for calculation
    category_weights: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # "Areas Requiring Critical Focus" array
    critical_focus_areas: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Raw Audit Payloads from External & Internal services
    pagespeed_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    semrush_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    crawler_lead_gen_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    crawler_broken_links_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    crawler_ui_ux_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="score_result")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="score_result")
