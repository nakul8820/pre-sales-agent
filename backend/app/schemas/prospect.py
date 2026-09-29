"""Pydantic schemas for Prospect CRUD operations, intake responses, and serialization."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.prospect import ProspectSource, ProspectStatus
from app.schemas.common_prospect import CommonProspectInput, extract_clean_domain, normalize_url


class ProspectBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    website_url: str = Field(..., min_length=3, max_length=512)
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_title: Optional[str] = None
    contact_phone: Optional[str] = None
    source: ProspectSource = ProspectSource.MANUAL
    hubspot_id: Optional[str] = None
    batch_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class ProspectCreate(ProspectBase):
    @classmethod
    def from_common_input(cls, common: CommonProspectInput, batch_id: Optional[uuid.UUID] = None) -> "ProspectCreate":
        return cls(
            company_name=common.company_name,
            website_url=common.website_url,
            contact_name=common.contact_name,
            contact_email=common.contact_email,
            contact_title=common.contact_title,
            contact_phone=common.contact_phone,
            source=common.source,
            hubspot_id=common.hubspot_id,
            batch_id=batch_id,
            notes=common.notes,
        )


class ProspectUpdate(BaseModel):
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_title: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[ProspectStatus] = None
    notes: Optional[str] = None


class ProspectRead(ProspectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    domain: str
    status: ProspectStatus
    created_at: datetime
    updated_at: datetime


class ProspectSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    domain: str
    website_url: str
    source: ProspectSource
    status: ProspectStatus
    created_at: datetime


class ProspectListResponse(BaseModel):
    items: List[ProspectRead]
    total: int
    page: int
    page_size: int


class ProspectWebFormResponse(BaseModel):
    """Response returned immediately after manual intake submission with letter grades and moderation status."""
    model_config = ConfigDict(from_attributes=True)

    prospect_id: uuid.UUID = Field(..., description="Unique generated identifier for the saved prospect")
    company_name: str
    domain: str
    website_url: str
    source: ProspectSource
    status: ProspectStatus
    message: str = "Prospect successfully registered and evaluated."
    created_at: datetime

    # Full 5 Category Scoring & Letter Grade (Sprint 6)
    logo_url: Optional[str] = None
    overall_score: Optional[float] = None
    letter_grade: Optional[str] = "B"
    grade_label: Optional[str] = "Good"
    grade_color: Optional[str] = "var(--status-success)"
    
    performance_score: Optional[float] = None
    seo_score: Optional[float] = None
    lead_gen_score: Optional[float] = None
    ui_ux_score: Optional[float] = None
    broken_links_score: Optional[float] = None
    category_weights: Optional[Dict[str, float]] = None

    # Content Appropriateness Pre-Report Gate (Sprint 6)
    moderation: Optional[Dict[str, Any]] = None

    pagespeed_data: Optional[Dict[str, Any]] = None
    semrush_data: Optional[Dict[str, Any]] = None
    crawler_data: Optional[Dict[str, Any]] = None
    critical_focus_areas: Optional[List[Dict[str, Any]]] = None
