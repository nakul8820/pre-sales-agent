"""RatingFlag model for automated content moderation and appropriateness heuristic findings."""
import enum
import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prospect import Prospect


class FlagCategory(str, enum.Enum):
    ADULT_CONTENT = "adult_content"
    POLITICAL_CONTENT = "political_content"
    UNDER_CONSTRUCTION = "under_construction"
    PARKED_DOMAIN = "parked_domain"
    GAMBLING = "gambling"
    MALICIOUS = "malicious"
    OTHER = "other"


class RatingFlag(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rating_flags"

    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_flagged: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    flag_category: Mapped[FlagCategory] = mapped_column(
        Enum(
            FlagCategory,
            name="flag_category_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=FlagCategory.OTHER,
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Human-in-the-loop review overrides
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_override_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="rating_flags")
