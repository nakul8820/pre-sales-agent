from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    database: str = Field(..., description="Database connection status ('connected' or error)")
    redis: str = Field(..., description="Redis connection status ('connected' or error)")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall system health: 'healthy' or 'degraded'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    environment: str
    version: str
    services: ServiceStatus
