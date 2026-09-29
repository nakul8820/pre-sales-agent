"""Pydantic schemas for BatchJob operations and progress monitoring."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.batch_job import BatchSource, BatchStatus


class BatchJobBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source: BatchSource = BatchSource.MANUAL_BULK
    metadata_payload: Optional[dict] = None


class BatchJobCreate(BatchJobBase):
    pass


class BatchJobRead(BatchJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: BatchStatus
    total_count: int
    processed_count: int
    failed_count: int
    flagged_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BatchJobListResponse(BaseModel):
    items: List[BatchJobRead]
    total: int
