"""Pydantic schemas for Report creation, serialization, and retrieval."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.report import ReportFormat, ReportStatus


class ReportBase(BaseModel):
    prospect_id: uuid.UUID
    score_result_id: uuid.UUID
    report_format: ReportFormat = ReportFormat.PDF
    logo_url: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ReportStatus
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    generation_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReportDetailRead(ReportRead):
    html_preview_cache: Optional[str] = None


class ReportListResponse(BaseModel):
    items: List[ReportRead]
    total: int
