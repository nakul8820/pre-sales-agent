"""Report generation endpoints — HTML preview, PDF download, DOCX download."""
import asyncio
import json
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.prospect import Prospect
from app.models.report import Report, ReportStatus
from app.models.score_result import ScoreResult
from app.services.report_generator import report_generator
from app.utils.logger import logger

router = APIRouter()


async def _load_audit_context(prospect_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
    """Load prospect + score_result from DB and build audit context dict for report rendering."""
    # Fetch prospect
    prospect_res = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = prospect_res.scalar_one_or_none()
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect {prospect_id} not found.",
        )

    # Fetch score result
    score_res = await db.execute(select(ScoreResult).where(ScoreResult.prospect_id == prospect_id))
    score = score_res.scalar_one_or_none()
    if not score:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Prospect {prospect_id} has not been analyzed yet. Run analysis first.",
        )

    # Fetch report record for logo_url
    rep_res = await db.execute(select(Report).where(Report.prospect_id == prospect_id))
    report_rec = rep_res.scalar_one_or_none()
    logo_url = report_rec.logo_url if report_rec else None

    # ── Reconstruct scoring grade ──────────────────────────────────────────
    s = score.overall_score or 0

    def _grade(v: float) -> str:
        if v >= 90: return "A"
        if v >= 75: return "B"
        if v >= 60: return "C"
        if v >= 45: return "D"
        return "F"

    grade_labels = {"A": "Excellent", "B": "Good", "C": "Moderate", "D": "Needs Work", "F": "Critical"}
    grade_colors = {"A": "#10b981", "B": "#3b82f6", "C": "#f59e0b", "D": "#ef4444", "F": "#dc2626"}
    lg = _grade(s)

    return {
        "prospect_id": str(prospect.id),
        "company_name": prospect.company_name,
        "domain": prospect.domain,
        "website_url": prospect.website_url,
        "contact_name": prospect.contact_name,
        "logo_url": logo_url,
        "overall_score": round(s),
        "letter_grade": lg,
        "grade_label": grade_labels[lg],
        "grade_color": grade_colors[lg],
        "performance_score": score.performance_score or 0,
        "seo_score": score.seo_score or 0,
        "lead_gen_score": score.lead_gen_score or 0,
        "ui_ux_score": score.ui_ux_score or 0,
        "broken_links_score": score.broken_links_score or 0,
        "category_weights": score.category_weights or {},
        "critical_focus_areas": score.critical_focus_areas or [],
        "pagespeed": score.pagespeed_raw or {},
        "semrush": score.semrush_raw or {},
        "crawler": {
            "pages_crawled_count": 0,
            "crawl_duration_seconds": 0,
            "lead_gen": score.crawler_lead_gen_raw or {},
            "broken_links": score.crawler_broken_links_raw or {},
            "ui_ux": score.crawler_ui_ux_raw or {},
        },
        "moderation": {"is_safe": True, "status_label": "Approved for Pitching", "flags": []},
    }


# ── HTML Preview ─────────────────────────────────────────────────────────────
@router.get(
    "/{prospect_id}/preview",
    response_class=HTMLResponse,
    summary="Live HTML Report Preview",
    description="Renders the audit report as an interactive HTML page for in-browser viewing.",
)
async def preview_report(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> HTMLResponse:
    """Render and return the audit report as an inline HTML page."""
    audit = await _load_audit_context(prospect_id, db)

    try:
        html = await asyncio.get_event_loop().run_in_executor(
            None, report_generator.render_html, audit
        )
        logger.info(f"HTML report preview served for prospect {prospect_id}")
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        logger.error(f"Error rendering HTML report for {prospect_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Report rendering failed: {str(e)}")


# ── PDF Download ─────────────────────────────────────────────────────────────
@router.get(
    "/{prospect_id}/pdf",
    summary="Download PDF Audit Report",
    description="Generates and streams a WeasyPrint PDF report for the analyzed prospect.",
)
async def download_pdf(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> FileResponse:
    """Generate and download PDF report."""
    audit = await _load_audit_context(prospect_id, db)

    try:
        pdf_path = await asyncio.get_event_loop().run_in_executor(
            None, report_generator.generate_pdf, audit, None
        )
        safe_name = audit["domain"].replace(".", "_")
        filename = f"audit_report_{safe_name}.pdf"
        logger.info(f"PDF report downloaded for prospect {prospect_id}")
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"Error generating PDF for {prospect_id}: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ── DOCX Download ─────────────────────────────────────────────────────────────
@router.get(
    "/{prospect_id}/docx",
    summary="Download Word Document Audit Report",
    description="Generates an editable Microsoft Word document for sales reps to customize.",
)
async def download_docx(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> FileResponse:
    """Generate and download DOCX report."""
    audit = await _load_audit_context(prospect_id, db)

    try:
        docx_path = await asyncio.get_event_loop().run_in_executor(
            None, report_generator.generate_docx, audit, None
        )
        safe_name = audit["domain"].replace(".", "_")
        filename = f"audit_report_{safe_name}.docx"
        logger.info(f"DOCX report downloaded for prospect {prospect_id}")
        return FileResponse(
            path=docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"Error generating DOCX for {prospect_id}: {e}")
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")


# ── Report Metadata ───────────────────────────────────────────────────────────
@router.get(
    "/{prospect_id}",
    summary="Get report metadata",
    description="Returns report record metadata (status, format, logo URL) for a prospect.",
)
async def get_report_metadata(
    prospect_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    """Returns the Report record metadata for a given prospect."""
    rep_res = await db.execute(select(Report).where(Report.prospect_id == prospect_id))
    report_rec = rep_res.scalar_one_or_none()

    if not report_rec:
        raise HTTPException(status_code=404, detail=f"No report found for prospect {prospect_id}.")

    score_res = await db.execute(select(ScoreResult).where(ScoreResult.prospect_id == prospect_id))
    score = score_res.scalar_one_or_none()

    return {
        "report_id": str(report_rec.id),
        "prospect_id": str(prospect_id),
        "status": report_rec.status.value,
        "format": report_rec.report_format.value,
        "logo_url": report_rec.logo_url,
        "overall_score": score.overall_score if score else None,
        "created_at": report_rec.created_at.isoformat() if report_rec.created_at else None,
        "links": {
            "preview": f"/api/v1/reports/{prospect_id}/preview",
            "pdf": f"/api/v1/reports/{prospect_id}/pdf",
            "docx": f"/api/v1/reports/{prospect_id}/docx",
        },
    }
