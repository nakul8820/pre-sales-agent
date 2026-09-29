"""Canonical Common Prospect Schema for normalizing intake data from Manual Form, HubSpot CRM, and Excel uploads."""
import re
import urllib.parse
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.prospect import ProspectSource


def extract_clean_domain(url_or_domain: str) -> str:
    """Extracts a clean, normalized domain (lowercase, stripped of protocol, www, and paths)."""
    val = url_or_domain.strip().lower()
    if not val.startswith(("http://", "https://")):
        val = "https://" + val
    parsed = urllib.parse.urlparse(val)
    domain = parsed.netloc or parsed.path
    # Strip port if present
    domain = domain.split(":")[0]
    # Strip leading www.
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.strip()


def normalize_url(url: str) -> str:
    """Ensures URL starts with a valid scheme and is stripped of trailing slashes."""
    val = url.strip()
    if not val.startswith(("http://", "https://")):
        val = f"https://{val}"
    # Remove trailing slash unless it's just the root
    parsed = urllib.parse.urlparse(val)
    path = parsed.path.rstrip("/") if parsed.path != "/" else ""
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))


class CommonProspectInput(BaseModel):
    """Normalized payload that all 3 intake channels (Manual, HubSpot, Excel) conform to."""
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    company_name: str = Field(..., min_length=1, max_length=255, description="Name of the company")
    website_url: str = Field(..., min_length=3, max_length=512, description="Target website URL")
    contact_name: Optional[str] = Field(None, max_length=255, description="Primary contact name")
    contact_email: Optional[EmailStr] = Field(None, description="Primary contact email")
    contact_title: Optional[str] = Field(None, max_length=255, description="Contact job title")
    contact_phone: Optional[str] = Field(None, max_length=64, description="Contact telephone")
    source: ProspectSource = Field(default=ProspectSource.MANUAL, description="Intake channel source")
    hubspot_id: Optional[str] = Field(None, max_length=128, description="HubSpot Contact or Company ID")
    notes: Optional[str] = Field(None, description="Sales notes or context")

    @field_validator("website_url")
    @classmethod
    def validate_and_normalize_url(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Website URL is too short or invalid")
        return normalize_url(v)

    @property
    def domain(self) -> str:
        """Derived clean domain name for indexing and crawling."""
        return extract_clean_domain(self.website_url)


class ManualIntakeRequest(BaseModel):
    """Payload specifically from the web UI manual entry form."""
    company_name: str = Field(..., min_length=1, max_length=255)
    website_url: str = Field(..., min_length=3, max_length=512)
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_title: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

    def to_common_input(self) -> CommonProspectInput:
        return CommonProspectInput(
            company_name=self.company_name,
            website_url=self.website_url,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_title=self.contact_title,
            contact_phone=self.contact_phone,
            source=ProspectSource.MANUAL,
            notes=self.notes,
        )


class HubSpotIntakeItem(BaseModel):
    """Single item parsed from HubSpot contacts or companies API."""
    company_name: str
    website_url: str
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_title: Optional[str] = None
    contact_phone: Optional[str] = None
    hubspot_id: str
    notes: Optional[str] = None

    def to_common_input(self) -> CommonProspectInput:
        return CommonProspectInput(
            company_name=self.company_name,
            website_url=self.website_url,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_title=self.contact_title,
            contact_phone=self.contact_phone,
            source=ProspectSource.HUBSPOT,
            hubspot_id=self.hubspot_id,
            notes=self.notes,
        )


class ExcelIntakeRow(BaseModel):
    """Single row parsed from Excel / CSV spreadsheets."""
    company_name: str
    website_url: str
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_title: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

    def to_common_input(self) -> CommonProspectInput:
        return CommonProspectInput(
            company_name=self.company_name,
            website_url=self.website_url,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_title=self.contact_title,
            contact_phone=self.contact_phone,
            source=ProspectSource.EXCEL_UPLOAD,
            notes=self.notes,
        )
