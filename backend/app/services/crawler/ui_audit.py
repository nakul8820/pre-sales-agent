"""UI/UX and Technical Website Auditor for mobile viewport, image alt tags, meta tags, SSL, and accessibility."""
import re
from typing import Any, Dict, List, Tuple
from app.utils.logger import logger


class UITechnicalAuditor:
    """Audits technical front-end health, mobile responsiveness, and accessibility fundamentals."""

    def audit_pages(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits technical UI and on-page HTML quality across crawled pages."""
        if not pages_data:
            return {
                "ui_ux_score": 50.0,
                "mobile_responsive": False,
                "total_images": 0,
                "missing_alt_tags_count": 0,
                "alt_coverage_percent": 0.0,
                "has_ssl": False,
                "mixed_content_count": 0,
                "has_title_tag": False,
                "has_meta_description": False,
                "has_h1": False,
                "gaps": [],
            }

        # Analyze homepage / aggregate pages
        home_page = pages_data[0]
        home_html = home_page.get("html", "")
        home_url = home_page.get("url", "")
        is_https = home_url.lower().startswith("https://")

        # 1. Mobile Viewport Check
        has_viewport = bool(re.search(r'<meta\s+[^>]*?name=["\']viewport["\']', home_html, re.I))

        # 2. Image Alt Text Scan
        total_images = 0
        missing_alt_count = 0
        unlabelled_images: List[str] = []

        for page in pages_data:
            html = page.get("html", "")
            img_matches = re.findall(r'<img\s+([^>]+)>', html, re.I)
            total_images += len(img_matches)

            for img_attrs in img_matches:
                alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_attrs, re.I)
                src_match = re.search(r'src=["\']([^"\']*)["\']', img_attrs, re.I)
                src_val = src_match.group(1) if src_match else "unknown"

                if not alt_match or not alt_match.group(1).strip():
                    missing_alt_count += 1
                    if len(unlabelled_images) < 5 and src_val != "unknown":
                        unlabelled_images.append(src_val[:80])

        alt_coverage = 100.0
        if total_images > 0:
            alt_coverage = round(((total_images - missing_alt_count) / total_images) * 100, 1)

        # 3. Meta Tag Evaluation
        title_match = re.search(r'<title>(.*?)</title>', home_html, re.I | re.DOTALL)
        title_tag = title_match.group(1).strip() if title_match else ""
        has_title_tag = bool(title_tag)
        title_len = len(title_tag)

        meta_desc_match = re.search(r'<meta\s+[^>]*?name=["\']description["\']\s+content=["\']([^"\']*)["\']', home_html, re.I)
        if not meta_desc_match:
            meta_desc_match = re.search(r'<meta\s+[^>]*?content=["\']([^"\']*)["\']\s+name=["\']description["\']', home_html, re.I)
        meta_desc = meta_desc_match.group(1).strip() if meta_desc_match else ""
        has_meta_description = bool(meta_desc)

        has_canonical = bool(re.search(r'<link\s+[^>]*?rel=["\']canonical["\']', home_html, re.I))
        has_og_tags = bool(re.search(r'<meta\s+[^>]*?property=["\']og:', home_html, re.I))

        # 4. Heading Structure
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', home_html, re.I | re.DOTALL)
        h1_count = len(h1_matches)
        has_h1 = h1_count > 0

        # 5. Accessibility & HTML Lang
        has_lang = bool(re.search(r'<html\s+[^>]*?lang=["\']', home_html, re.I))

        # 6. Mixed Content Detection (HTTP resources on HTTPS page)
        mixed_content_count = 0
        if is_https:
            mixed_content_matches = re.findall(r'(?:src|href)=["\']http://([^"\']+)["\']', home_html, re.I)
            # Filter out standard schema / xml namespaces
            for m in mixed_content_matches:
                if not m.startswith(("www.w3.org", "schema.org")):
                    mixed_content_count += 1

        # Calculate UI/UX & Technical Score (0 - 100)
        score = 0.0
        if has_viewport:
            score += 25.0
        if is_https and mixed_content_count == 0:
            score += 20.0
        elif is_https:
            score += 12.0
            
        score += (alt_coverage / 100.0) * 20.0
        
        if has_title_tag and (30 <= title_len <= 70):
            score += 10.0
        elif has_title_tag:
            score += 6.0
            
        if has_meta_description:
            score += 10.0
        if has_h1 and h1_count == 1:
            score += 10.0
        elif has_h1:
            score += 6.0
        if has_lang:
            score += 5.0

        ui_ux_score = min(100.0, max(20.0, round(score, 1)))

        # Identify Gaps for Sales Pitch
        gaps: List[Dict[str, Any]] = []

        if not has_viewport:
            gaps.append({
                "category": "UI/UX & Mobile",
                "severity": "high",
                "title": "Missing Mobile Viewport Configuration",
                "description": "Website is missing `<meta name='viewport'>`, causing layout distortion on mobile smartphones.",
                "impact": "Severely damages mobile conversions and triggers Google mobile ranking penalties.",
                "pitch_angle": "Offer complete responsive layout modernization.",
            })

        if missing_alt_count > 5 or alt_coverage < 60.0:
            gaps.append({
                "category": "Technical & SEO",
                "severity": "medium",
                "title": f"Poor Image Alt Text Coverage ({alt_coverage}% Coverage)",
                "description": f"{missing_alt_count} images across scanned pages lack descriptive alt attributes.",
                "impact": "Damages image search indexing and violates ADA/WCAG accessibility guidelines.",
                "pitch_angle": "Offer accessibility compliance and image SEO remediation package.",
            })

        if not has_meta_description:
            gaps.append({
                "category": "Technical & SEO",
                "severity": "medium",
                "title": "Missing Homepage Meta Description",
                "description": "Google is forced to auto-generate search result snippets, reducing click-through rate (CTR).",
                "impact": "Lower organic click-through rate from Google Search Engine Result Pages (SERPs).",
                "pitch_angle": "Provide copywriting for high-converting Google search meta snippets.",
            })

        if not is_https:
            gaps.append({
                "category": "Technical & UI",
                "severity": "high",
                "title": "Insecure HTTP Protocol (Missing SSL)",
                "description": "Website loads over unencrypted HTTP, showing 'Not Secure' browser warnings.",
                "impact": "Drastic drop in customer trust and security compliance.",
                "pitch_angle": "Immediate SSL certificate installation & HTTPS 301 redirection.",
            })

        if mixed_content_count > 0:
            gaps.append({
                "category": "Technical & UI",
                "severity": "medium",
                "title": f"Mixed Content Vulnerabilities ({mixed_content_count} Insecure Assets)",
                "description": "Secure HTTPS pages load insecure HTTP scripts or images.",
                "impact": "Browser security warnings and blocked asset rendering.",
                "pitch_angle": "Resolve all asset protocol paths to secure HTTPS.",
            })

        return {
            "ui_ux_score": ui_ux_score,
            "mobile_responsive": has_viewport,
            "total_images": total_images,
            "missing_alt_tags_count": missing_alt_count,
            "alt_coverage_percent": alt_coverage,
            "unlabelled_images": unlabelled_images,
            "has_ssl": is_https,
            "mixed_content_count": mixed_content_count,
            "has_title_tag": has_title_tag,
            "title_tag": title_tag,
            "title_length": title_len,
            "has_meta_description": has_meta_description,
            "meta_description": meta_desc[:120],
            "has_canonical": has_canonical,
            "has_og_tags": has_og_tags,
            "has_h1": has_h1,
            "h1_count": h1_count,
            "has_html_lang": has_lang,
            "gaps": gaps,
        }


ui_technical_auditor = UITechnicalAuditor()
