"""Pydantic schemas for RatingFlag automated content moderation."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.rating_flag import FlagCategory


class RatingFlagBase(BaseModel):
    prospect_id: uuid.UUID
    is_flagged: bool = True
    flag_category: FlagCategory = FlagCategory.OTHER
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str = Field(..., max_length=512)
    details: Optional[dict] = None
    is_reviewed: bool = False
    is_override_approved: bool = False


class RatingFlagCreate(RatingFlagBase):
    pass


class RatingFlagUpdate(BaseModel):
    is_reviewed: Optional[bool] = None
    is_override_approved: Optional[bool] = None
    reason: Optional[str] = None


class RatingFlagRead(RatingFlagBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
