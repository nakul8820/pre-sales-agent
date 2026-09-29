"""Multi-format report generator: HTML preview, PDF (WeasyPrint), and DOCX (python-docx)."""
import math
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.utils.logger import logger

# ── Paths ─────────────────────────────────────────────────────────────────
TEMPLATES_DIR = Path(__file__).parent / "templates"
REPORTS_DIR = Path("/tmp/reports")  # ephemeral in dev; override via env in prod
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Jinja2 environment ────────────────────────────────────────────────────
_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


# ── Helpers ───────────────────────────────────────────────────────────────
def _score_to_grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 45: return "D"
    return "F"


def _category_icon(name: str) -> str:
    icons = {
        "performance": "⚡",
        "seo": "🔍",
        "lead_gen": "🎣",
        "ui_ux": "🎨",
        "broken_links": "🔗",
    }
    return icons.get(name.lower().replace(" ", "_").replace("/", "_"), "📊")


def _category_label(key: str) -> str:
    labels = {
        "performance": "Performance",
        "seo": "SEO",
        "lead_gen": "Lead Gen",
        "ui_ux": "UI / UX",
        "broken_links": "Link Health",
    }
    return labels.get(key, key.title())


def _build_template_context(audit: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw audit dict into a flat, template-ready context."""
    score = audit.get("overall_score", 0)
    letter_grade = audit.get("letter_grade", _score_to_grade(score))
    grade_label = audit.get("grade_label", "Unknown")

    pagespeed_raw: Dict[str, Any] = audit.get("pagespeed", {})
    semrush_raw: Dict[str, Any] = audit.get("semrush", {})
    crawler_raw: Dict[str, Any] = audit.get("crawler", {})
    moderation: Dict[str, Any] = audit.get("moderation", {})

    lead_gen = crawler_raw.get("lead_gen", {})
    broken_links = crawler_raw.get("broken_links", {})
    ui_ux = crawler_raw.get("ui_ux", {})

    # Wrap dicts in DotDict so Jinja2 attribute access and `is not none` work correctly
    class DotDict(dict):
        """dict subclass supporting attribute-style get access for Jinja2 templates."""
        def __getattr__(self, key: str):
            return self.get(key)

    pagespeed = DotDict(pagespeed_raw)
    semrush = DotDict(semrush_raw)
    lead_gen_ctx = DotDict(lead_gen)
    broken_links_ctx = DotDict(broken_links)
    ui_ux_ctx = DotDict(ui_ux)

    category_scores = {
        "performance": audit.get("performance_score", pagespeed.get("performance_score", 0)),
        "seo": audit.get("seo_score", 0),
        "lead_gen": audit.get("lead_gen_score", lead_gen.get("lead_gen_score", 0)),
        "ui_ux": audit.get("ui_ux_score", ui_ux.get("ui_ux_score", 0)),
        "broken_links": audit.get("broken_links_score", broken_links.get("broken_links_score", 0)),
    }

    categories = [
        {
            "key": key,
            "name": _category_label(key),
            "icon": _category_icon(key),
            "score": round(category_scores[key]),
            "grade": _score_to_grade(category_scores[key]),
        }
        for key in ["performance", "seo", "lead_gen", "ui_ux", "broken_links"]
    ]

    critical_focus_areas = audit.get("critical_focus_areas", [])

    return {
        # Prospect info
        "company_name": audit.get("company_name", "Prospect"),
        "domain": audit.get("domain", ""),
        "website_url": audit.get("website_url", ""),
        "contact_name": audit.get("contact_name", ""),
        "logo_url": audit.get("logo_url", ""),

        # Scores & Grade
        "overall_score": round(score),
        "letter_grade": letter_grade,
        "grade_label": grade_label,
        "categories": categories,
        "critical_focus_areas": critical_focus_areas,
        "critical_focus_count": len(critical_focus_areas),

        # Crawl metadata
        "pages_crawled": crawler_raw.get("pages_crawled_count", 0),
        "crawl_duration": round(crawler_raw.get("crawl_duration_seconds", 0), 1),

        # Report metadata
        "report_date": datetime.now(tz=timezone.utc).strftime("%B %d, %Y"),

        # Service data — wrapped in DotDict for attribute access in Jinja2
        "pagespeed": pagespeed,
        "semrush": semrush,
        "lead_gen": lead_gen_ctx,
        "broken_links": broken_links_ctx,
        "ui_ux": ui_ux_ctx,

        # Moderation
        "moderation_safe": moderation.get("is_safe", True),
        "moderation_label": moderation.get("status_label", "Approved for Pitching"),
        "moderation_flags": moderation.get("flags", []),
    }


class ReportGeneratorService:
    """Renders audit data into HTML, PDF, and DOCX client-facing reports."""

    # ── HTML Preview ─────────────────────────────────────────────────────
    def render_html(self, audit: Dict[str, Any]) -> str:
        """Render the Jinja2 HTML report template and return raw HTML string."""
        t0 = time.monotonic()
        template = _jinja_env.get_template("audit_report.html")
        ctx = _build_template_context(audit)
        html = template.render(**ctx)
        ms = int((time.monotonic() - t0) * 1000)
        logger.info(f"HTML report rendered for '{ctx['company_name']}' in {ms}ms")
        return html

    # ── PDF Generation ────────────────────────────────────────────────────
    def generate_pdf(self, audit: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate a PDF report using WeasyPrint. Returns path to the PDF file."""
        try:
            from weasyprint import HTML  # lazy import — only loaded when PDF is requested
        except ImportError:
            raise RuntimeError("WeasyPrint is not installed. Add 'weasyprint' to requirements.txt.")

        t0 = time.monotonic()
        html_str = self.render_html(audit)

        if not output_path:
            file_name = f"audit_{audit.get('domain', 'report')}_{uuid.uuid4().hex[:8]}.pdf"
            output_path = str(REPORTS_DIR / file_name)

        HTML(string=html_str, base_url=str(TEMPLATES_DIR)).write_pdf(output_path)

        file_size = os.path.getsize(output_path)
        ms = int((time.monotonic() - t0) * 1000)
        logger.info(
            f"PDF report generated for '{audit.get('company_name', '?')}': "
            f"{file_size:,} bytes in {ms}ms → {output_path}"
        )
        return output_path

    # ── DOCX Generation ───────────────────────────────────────────────────
    def generate_docx(self, audit: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate an editable Word document. Returns path to the DOCX file."""
        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            raise RuntimeError("python-docx is not installed. Add 'python-docx' to requirements.txt.")

        t0 = time.monotonic()
        ctx = _build_template_context(audit)
        doc = Document()

        # ── Styles ──────────────────────────────────────────────────────
        style = doc.styles["Normal"]
        font = style.font
        font.name = "Calibri"
        font.size = Pt(10)

        # ── Cover Section ───────────────────────────────────────────────
        title = doc.add_heading(f"Website Audit Report — {ctx['company_name']}", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Domain: {ctx['domain']}")
        doc.add_paragraph(f"Report Date: {ctx['report_date']}")
        doc.add_paragraph(f"Overall Score: {ctx['overall_score']}/100 — Grade {ctx['letter_grade']} ({ctx['grade_label']})")
        doc.add_paragraph(
            f"Content Safety Gate: {'✅ Approved for Pitching' if ctx['moderation_safe'] else '⚠️ Flagged for Review'}"
        )
        doc.add_page_break()

        # ── Executive Score Summary ──────────────────────────────────────
        doc.add_heading("Executive Score Summary", level=1)
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Category"
        hdr[1].text = "Score"
        hdr[2].text = "Grade"
        for cat in ctx["categories"]:
            row = table.add_row().cells
            row[0].text = cat["name"]
            row[1].text = f"{cat['score']}/100"
            row[2].text = cat["grade"]
        doc.add_paragraph()

        # ── Critical Focus Areas ─────────────────────────────────────────
        if ctx["critical_focus_areas"]:
            doc.add_heading("Areas Requiring Critical Focus", level=1)
            for i, focus in enumerate(ctx["critical_focus_areas"], 1):
                doc.add_heading(f"{i}. {focus.get('title', '')}", level=2)
                doc.add_paragraph(f"Severity: {focus.get('severity', '').upper()}")
                doc.add_paragraph(focus.get("description", ""))
                p = doc.add_paragraph()
                p.add_run("Business Impact: ").bold = True
                p.add_run(focus.get("impact", ""))
                pa = doc.add_paragraph()
                pa.add_run("Pitch Angle: ").bold = True
                pa.add_run(focus.get("pitch_angle", ""))
                doc.add_paragraph()

        # ── Performance ──────────────────────────────────────────────────
        doc.add_heading("Performance & Core Web Vitals", level=1)
        ps = ctx["pagespeed"]
        doc.add_paragraph(f"Performance Score: {ps.get('performance_score', 'N/A')}/100")
        if ps.get("fcp_ms"):
            doc.add_paragraph(f"First Contentful Paint (FCP): {round(ps['fcp_ms'] / 1000, 1)}s")
        if ps.get("lcp_ms"):
            doc.add_paragraph(f"Largest Contentful Paint (LCP): {round(ps['lcp_ms'] / 1000, 1)}s")
        if ps.get("cls_score") is not None:
            doc.add_paragraph(f"Cumulative Layout Shift (CLS): {ps['cls_score']}")
        if ps.get("tbt_ms"):
            doc.add_paragraph(f"Total Blocking Time (TBT): {ps['tbt_ms']}ms")
        if ps.get("opportunities"):
            doc.add_heading("Optimization Opportunities", level=2)
            for opp in ps["opportunities"]:
                doc.add_paragraph(f"• {opp.get('title', '')}: {opp.get('display_value', '')}")

        doc.add_page_break()

        # ── SEO ──────────────────────────────────────────────────────────
        doc.add_heading("SEO & Organic Traffic", level=1)
        sm = ctx["semrush"]
        doc.add_paragraph(f"Monthly Organic Traffic: {sm.get('organic_traffic', 0):,}")
        doc.add_paragraph(f"Ranking Keywords: {sm.get('organic_keywords', 0):,}")
        doc.add_paragraph(f"Traffic Value: ${sm.get('organic_cost', 0):,.0f}/month")
        doc.add_paragraph(f"Domain Rank: {sm.get('domain_rank', 0):,}")

        if sm.get("top_keywords"):
            doc.add_heading("Top Keywords", level=2)
            kt = doc.add_table(rows=1, cols=4)
            kt.style = "Table Grid"
            kh = kt.rows[0].cells
            kh[0].text = "Keyword"
            kh[1].text = "Position"
            kh[2].text = "Volume"
            kh[3].text = "CPC"
            for kw in sm["top_keywords"]:
                kr = kt.add_row().cells
                kr[0].text = kw.get("keyword", "")
                kr[1].text = f"#{kw.get('position', '')}"
                kr[2].text = f"{kw.get('search_volume', 0):,}"
                kr[3].text = f"${kw.get('cpc', 0)}"

        doc.add_page_break()

        # ── Lead Generation ──────────────────────────────────────────────
        doc.add_heading("Lead Generation Assessment", level=1)
        lg = ctx["lead_gen"]
        doc.add_paragraph(f"Contact Forms: {'Found' if lg.get('has_contact_form') else 'Missing'}")
        doc.add_paragraph(f"Live Chat Widget: {'Found' if lg.get('has_live_chat') else 'Missing'}")
        doc.add_paragraph(f"Phone Number: {'Found' if lg.get('has_phone_number') else 'Not detected'}")
        doc.add_paragraph(f"Booking Widget: {'Found' if lg.get('has_booking_widget') else 'Missing'}")
        doc.add_paragraph(f"Email Address: {'Found' if lg.get('has_email_address') else 'Not visible'}")
        if lg.get("detected_ctas"):
            doc.add_paragraph(f"CTAs Detected: {', '.join(lg['detected_ctas'])}")
        if lg.get("form_providers"):
            doc.add_paragraph(f"Form Providers: {', '.join(lg['form_providers'])}")

        # ── UI/UX ─────────────────────────────────────────────────────────
        doc.add_heading("UI/UX & Technical Audit", level=1)
        ux = ctx["ui_ux"]
        doc.add_paragraph(f"Mobile Responsive: {'Yes' if ux.get('mobile_responsive') else 'No'}")
        doc.add_paragraph(f"SSL / HTTPS: {'Enabled' if ux.get('has_ssl') else 'MISSING — Critical risk'}")
        doc.add_paragraph(f"Title Tag: {'Present' if ux.get('has_title_tag') else 'Missing'}")
        doc.add_paragraph(f"Meta Description: {'Present' if ux.get('has_meta_description') else 'Missing'}")
        doc.add_paragraph(f"H1 Heading: {'Present' if ux.get('has_h1') else 'Missing'}")
        doc.add_paragraph(
            f"Image Alt Text Coverage: {ux.get('alt_coverage_percent', 0):.0f}% "
            f"({ux.get('missing_alt_tags_count', 0)} missing)"
        )

        # ── Broken Links ─────────────────────────────────────────────────
        doc.add_heading("Broken Links Audit", level=1)
        bl = ctx["broken_links"]
        doc.add_paragraph(f"Total Links Checked: {bl.get('total_links_checked', 0)}")
        doc.add_paragraph(f"Broken Links Found: {bl.get('broken_links_count', 0)}")
        doc.add_paragraph(f"Internal Broken: {bl.get('internal_broken_count', 0)}")
        doc.add_paragraph(f"External Broken: {bl.get('external_broken_count', 0)}")
        if bl.get("broken_links"):
            doc.add_heading("Broken Link URLs", level=2)
            for lnk in bl["broken_links"][:20]:
                doc.add_paragraph(f"• [{lnk.get('status_code', '?')}] {lnk.get('url', '')}")

        # ── Footer ───────────────────────────────────────────────────────
        doc.add_page_break()
        doc.add_paragraph(
            f"Generated by Prospect Digital Analyzer on {ctx['report_date']}. "
            "Confidential — for internal sales use only."
        )

        if not output_path:
            file_name = f"audit_{audit.get('domain', 'report')}_{uuid.uuid4().hex[:8]}.docx"
            output_path = str(REPORTS_DIR / file_name)

        doc.save(output_path)

        file_size = os.path.getsize(output_path)
        ms = int((time.monotonic() - t0) * 1000)
        logger.info(
            f"DOCX report generated for '{audit.get('company_name', '?')}': "
            f"{file_size:,} bytes in {ms}ms → {output_path}"
        )
        return output_path


report_generator = ReportGeneratorService()
