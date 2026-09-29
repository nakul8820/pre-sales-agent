"""Database seed script for populating realistic test data across all models and intake channels."""
import sys
import uuid
from datetime import datetime, timezone

from app.core.database import SyncSessionLocal
from app.models import (
    BatchJob,
    BatchSource,
    BatchStatus,
    Prospect,
    ProspectSource,
    ProspectStatus,
    ScoreResult,
    RatingFlag,
    FlagCategory,
    Report,
    ReportFormat,
    ReportStatus,
)
from app.schemas.common_prospect import extract_clean_domain, normalize_url
from app.utils.logger import logger


def seed_database():
    """Seeds the database with diverse sample data representing real-world sales scenarios."""
    session = SyncSessionLocal()
    try:
        logger.info("Starting database seeding...")

        # 1. Create a sample Batch Job
        batch = BatchJob(
            id=uuid.uuid4(),
            name="HubSpot Q3 Outbound Pitch Campaign",
            source=BatchSource.HUBSPOT,
            status=BatchStatus.COMPLETED,
            total_count=3,
            processed_count=2,
            failed_count=0,
            flagged_count=1,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            metadata_payload={"list_id": "hs_list_98412", "campaign": "q3_web_overhaul"},
        )
        session.add(batch)
        session.flush()

        # 2. Prospect 1: High Performing Tech Company (Score: 88.5)
        p1_url = "https://acmecloud.io"
        p1 = Prospect(
            id=uuid.uuid4(),
            company_name="Acme Cloud Technologies",
            website_url=normalize_url(p1_url),
            domain=extract_clean_domain(p1_url),
            contact_name="Sarah Jenkins",
            contact_email="sarah.jenkins@acmecloud.io",
            contact_title="VP of Marketing",
            contact_phone="+1 (555) 234-5678",
            source=ProspectSource.MANUAL,
            status=ProspectStatus.COMPLETED,
            notes="Inbound discovery inquiry requesting marketing tech stack audit.",
        )
        session.add(p1)
        session.flush()

        sr1 = ScoreResult(
            id=uuid.uuid4(),
            prospect_id=p1.id,
            overall_score=88.5,
            performance_score=92.0,
            seo_score=89.0,
            lead_gen_score=85.0,
            ui_ux_score=90.0,
            broken_links_score=82.0,
            category_weights={
                "performance": 0.25,
                "seo": 0.25,
                "lead_gen": 0.25,
                "ui_ux": 0.15,
                "broken_links": 0.10,
            },
            critical_focus_areas=[
                {
                    "category": "Broken Links",
                    "severity": "medium",
                    "title": "3 External Blog Reference 404s",
                    "description": "Historical blog posts link to defunct partner landing pages.",
                    "impact": "Slight link equity leak and broken user journey.",
                    "pitch_angle": "Offer link maintenance & evergreen content hygiene package.",
                }
            ],
            pagespeed_raw={"fcp_ms": 820, "lcp_ms": 1450, "cls": 0.02, "performance_score": 92},
            semrush_raw={"organic_traffic": 45200, "organic_keywords": 3400, "domain_rank": 58},
            crawler_lead_gen_raw={"has_contact_form": True, "has_phone_number": True, "has_cta": True, "has_chat": True},
            crawler_broken_links_raw={"total_links": 142, "broken_links_count": 3, "broken_urls": ["https://partner.xyz/old-deal"]},
            crawler_ui_ux_raw={"mobile_responsive": True, "missing_alt_tags_count": 2, "has_ssl": True},
        )
        session.add(sr1)
        session.flush()

        rep1 = Report(
            id=uuid.uuid4(),
            prospect_id=p1.id,
            score_result_id=sr1.id,
            report_format=ReportFormat.PDF,
            status=ReportStatus.READY,
            file_path="/app/storage/reports/acme_cloud_audit.pdf",
            file_url="http://localhost:8000/api/v1/reports/downloads/acme_cloud_audit.pdf",
            file_size_bytes=248000,
            generation_time_ms=1850,
            logo_url="https://logo.clearbit.com/acmecloud.io",
        )
        session.add(rep1)

        # 3. Prospect 2: Local Healthcare Clinic with Severe SEO & Broken Links (Score: 42.0)
        p2_url = "http://www.apexortho-clinic.com"
        p2 = Prospect(
            id=uuid.uuid4(),
            company_name="Apex Orthopedic Clinic",
            website_url=normalize_url(p2_url),
            domain=extract_clean_domain(p2_url),
            contact_name="Dr. Marcus Vance",
            contact_email="dr.vance@apexortho-clinic.com",
            contact_title="Managing Partner",
            contact_phone="+1 (555) 987-6543",
            source=ProspectSource.HUBSPOT,
            hubspot_id="hs_contact_77812",
            batch_id=batch.id,
            status=ProspectStatus.COMPLETED,
            notes="HubSpot synced lead. High-value target for local SEO and web rebuild.",
        )
        session.add(p2)
        session.flush()

        sr2 = ScoreResult(
            id=uuid.uuid4(),
            prospect_id=p2.id,
            overall_score=42.0,
            performance_score=35.0,
            seo_score=40.0,
            lead_gen_score=48.0,
            ui_ux_score=50.0,
            broken_links_score=30.0,
            category_weights={
                "performance": 0.25,
                "seo": 0.25,
                "lead_gen": 0.25,
                "ui_ux": 0.15,
                "broken_links": 0.10,
            },
            critical_focus_areas=[
                {
                    "category": "Performance",
                    "severity": "high",
                    "title": "Severe Mobile Loading Latency (LCP > 5.2s)",
                    "description": "Uncompressed 8MB patient testimonial hero banners blocking first paint.",
                    "impact": "Over 65% estimated mobile bounce rate before patient books appointment.",
                    "pitch_angle": "Highlight instant patient conversion gains from modern high-speed headless rebuild.",
                },
                {
                    "category": "SEO",
                    "severity": "high",
                    "title": "Missing Local Schema & Duplicate Meta Descriptions",
                    "description": "Zero medical schema markup and empty H1 tags across 14 service subpages.",
                    "impact": "Losing #1 local map-pack rankings to neighborhood competitors.",
                    "pitch_angle": "Offer local SEO domination and medical schema restructuring.",
                },
                {
                    "category": "Broken Links",
                    "severity": "high",
                    "title": "Patient Portal 'Book Appointment' Button 404s",
                    "description": "Primary booking button on header links to non-existent subdomain.",
                    "impact": "Direct lead destruction — patients cannot self-schedule.",
                    "pitch_angle": "Immediate fix proposal during sales discovery call.",
                },
            ],
            pagespeed_raw={"fcp_ms": 3100, "lcp_ms": 5200, "cls": 0.45, "performance_score": 35},
            semrush_raw={"organic_traffic": 820, "organic_keywords": 45, "domain_rank": 14},
            crawler_lead_gen_raw={"has_contact_form": False, "has_phone_number": True, "has_cta": False, "has_chat": False},
            crawler_broken_links_raw={"total_links": 88, "broken_links_count": 12, "broken_urls": ["http://portal.apexortho-clinic.com/book"]},
            crawler_ui_ux_raw={"mobile_responsive": False, "missing_alt_tags_count": 34, "has_ssl": False},
        )
        session.add(sr2)
        session.flush()

        rep2_pdf = Report(
            id=uuid.uuid4(),
            prospect_id=p2.id,
            score_result_id=sr2.id,
            report_format=ReportFormat.PDF,
            status=ReportStatus.READY,
            file_path="/app/storage/reports/apex_ortho_audit.pdf",
            file_url="http://localhost:8000/api/v1/reports/downloads/apex_ortho_audit.pdf",
            file_size_bytes=312000,
            generation_time_ms=2100,
        )
        rep2_docx = Report(
            id=uuid.uuid4(),
            prospect_id=p2.id,
            score_result_id=sr2.id,
            report_format=ReportFormat.DOCX,
            status=ReportStatus.READY,
            file_path="/app/storage/reports/apex_ortho_audit.docx",
            file_url="http://localhost:8000/api/v1/reports/downloads/apex_ortho_audit.docx",
            file_size_bytes=145000,
            generation_time_ms=850,
        )
        session.add_all([rep2_pdf, rep2_docx])

        # 4. Prospect 3: Construction Supplier from Excel Upload (Score: 56.2)
        p3_url = "nexus-buildsupply.com"
        p3 = Prospect(
            id=uuid.uuid4(),
            company_name="Nexus Construction Supplies",
            website_url=normalize_url(p3_url),
            domain=extract_clean_domain(p3_url),
            contact_name="Dave Miller",
            contact_email="dmiller@nexus-buildsupply.com",
            contact_title="Operations Director",
            contact_phone="+1 (555) 443-1122",
            source=ProspectSource.EXCEL_UPLOAD,
            batch_id=batch.id,
            status=ProspectStatus.COMPLETED,
            notes="Uploaded via Midwest_Suppliers_Q3.xlsx",
        )
        session.add(p3)
        session.flush()

        sr3 = ScoreResult(
            id=uuid.uuid4(),
            prospect_id=p3.id,
            overall_score=56.2,
            performance_score=60.0,
            seo_score=52.0,
            lead_gen_score=45.0,
            ui_ux_score=68.0,
            broken_links_score=70.0,
            category_weights={
                "performance": 0.25,
                "seo": 0.25,
                "lead_gen": 0.25,
                "ui_ux": 0.15,
                "broken_links": 0.10,
            },
            critical_focus_areas=[
                {
                    "category": "Lead Generation",
                    "severity": "high",
                    "title": "No RFQ (Request for Quote) or Wholesale Catalog Signup",
                    "description": "Distributor catalog has no digital quote cart or contact capture forms.",
                    "impact": "Losing commercial contractor leads to online distributors.",
                    "pitch_angle": "Pitch custom B2B wholesale portal & instant quotation funnel.",
                }
            ],
            pagespeed_raw={"fcp_ms": 1800, "lcp_ms": 2900, "cls": 0.12, "performance_score": 60},
            semrush_raw={"organic_traffic": 3200, "organic_keywords": 210, "domain_rank": 26},
            crawler_lead_gen_raw={"has_contact_form": False, "has_phone_number": True, "has_cta": False, "has_chat": False},
            crawler_broken_links_raw={"total_links": 62, "broken_links_count": 2, "broken_urls": []},
            crawler_ui_ux_raw={"mobile_responsive": True, "missing_alt_tags_count": 8, "has_ssl": True},
        )
        session.add(sr3)

        # 5. Prospect 4: Flagged Target (Automated Content Moderation Flag)
        p4_url = "https://vortex-parked-domain.xyz"
        p4 = Prospect(
            id=uuid.uuid4(),
            company_name="Vortex Under Construction Co",
            website_url=normalize_url(p4_url),
            domain=extract_clean_domain(p4_url),
            contact_name=None,
            contact_email=None,
            source=ProspectSource.EXCEL_UPLOAD,
            batch_id=batch.id,
            status=ProspectStatus.MODERATION_FLAGGED,
            notes="Flagged automatically by heuristic content moderator.",
        )
        session.add(p4)
        session.flush()

        rf4 = RatingFlag(
            id=uuid.uuid4(),
            prospect_id=p4.id,
            is_flagged=True,
            flag_category=FlagCategory.UNDER_CONSTRUCTION,
            confidence_score=0.98,
            reason="Domain parking page detected with 'Coming Soon / Site Under Maintenance' placeholder template.",
            details={
                "title_tag": "Default Domain Holding Page",
                "matched_heuristics": ["coming soon", "parked on godaddy", "default index.html"],
                "http_status": 200,
            },
            is_reviewed=False,
            is_override_approved=False,
        )
        session.add(rf4)

        session.commit()
        logger.info("Successfully seeded database with 1 batch, 4 prospects, 3 score results, 1 rating flag, and 3 reports.")
        print("\n✅ Database Seed Successful!")
        print(f"  • Batch Jobs Created: 1 ({batch.name})")
        print(f"  • Prospects Created:  4 ([1] {p1.company_name}, [2] {p2.company_name}, [3] {p3.company_name}, [4] {p4.company_name})")
        print(f"  • Score Results:      3 (Scores: {sr1.overall_score}, {sr2.overall_score}, {sr3.overall_score})")
        print(f"  • Rating Flags:       1 ({rf4.flag_category.value}: {rf4.reason[:40]}...)")
        print(f"  • Reports Generated:  3 (PDF: 2, DOCX: 1)")

    except Exception as e:
        session.rollback()
        logger.exception(f"Database seeding failed: {e}")
        print(f"\n❌ Seeding Failed: {e}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
