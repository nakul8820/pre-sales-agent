import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    overall_score: Optional[float] = None
    performance_score: Optional[float] = None
    seo_score: Optional[float] = None
    lead_gen_score: Optional[float] = None
    ui_ux_score: Optional[float] = None
    broken_links_score: Optional[float] = None


class AuditRead(ScoreBreakdown):
    id: uuid.UUID
    prospect_id: uuid.UUID
    is_flagged: bool
    moderation_reason: Optional[str] = None
    critical_focus_areas: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
