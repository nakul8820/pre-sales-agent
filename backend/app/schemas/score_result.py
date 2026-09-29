"""Pydantic schemas for ScoreResult operations, breakdowns, and audit dumps."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ScoreCategoryWeights(BaseModel):
    performance: float = 0.25
    seo: float = 0.25
    lead_gen: float = 0.25
    ui_ux: float = 0.15
    broken_links: float = 0.10


class CriticalFocusArea(BaseModel):
    category: str
    severity: str  # high, medium, low
    title: str
    description: str
    impact: str
    pitch_angle: Optional[str] = None


class ScoreResultBase(BaseModel):
    prospect_id: uuid.UUID
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    performance_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    seo_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    lead_gen_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    ui_ux_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    broken_links_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    category_weights: Optional[dict] = None
    critical_focus_areas: Optional[List[dict]] = None


class ScoreResultCreate(ScoreResultBase):
    pagespeed_raw: Optional[dict] = None
    semrush_raw: Optional[dict] = None
    crawler_lead_gen_raw: Optional[dict] = None
    crawler_broken_links_raw: Optional[dict] = None
    crawler_ui_ux_raw: Optional[dict] = None


class ScoreResultRead(ScoreResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ScoreResultDetailRead(ScoreResultRead):
    pagespeed_raw: Optional[dict] = None
    semrush_raw: Optional[dict] = None
    crawler_lead_gen_raw: Optional[dict] = None
    crawler_broken_links_raw: Optional[dict] = None
    crawler_ui_ux_raw: Optional[dict] = None
