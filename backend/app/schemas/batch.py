from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List

from app.models.batch_job import BatchSource, BatchStatus


class BatchJobCreate(BaseModel):
    name: str
    source: BatchSource


class BatchJobRead(BaseModel):
    id: UUID
    name: str
    source: BatchSource
    status: BatchStatus
    total_count: int
    processed_count: int
    failed_count: int
    flagged_count: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchJobListResponse(BaseModel):
    items: List[BatchJobRead]
    total: int
    page: int
    page_size: int
