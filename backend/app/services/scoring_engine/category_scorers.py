"""Specialized category scorers evaluating performance, SEO, lead generation, UI/UX, and broken link telemetry."""
from typing import Any, Dict, List, Tuple
from app.services.scoring_engine.benchmarks import CWV_THRESHOLDS, SEO_THRESHOLDS


class PerformanceScorer:
    """Evaluates Google PageSpeed and Core Web Vitals."""

    def score(self, pagespeed_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        perf_score = pagespeed_data.get("performance_score", 70.0)
        cwv = pagespeed_data.get("core_web_vitals", {})

        fcp = cwv.get("fcp_ms", 1500)
        lcp = cwv.get("lcp_ms", 2800)
        cls = cwv.get("cls", 0.08)
        tbt = cwv.get("tbt_ms", 200)

        # CWV pass status
        cwv_pass = (
            lcp <= CWV_THRESHOLDS["lcp_good"]
            and cls <= CWV_THRESHOLDS["cls_good"]
            and fcp <= CWV_THRESHOLDS["fcp_good"]
            and tbt <= CWV_THRESHOLDS["tbt_good"]
        )

        telemetry = {
            "score": round(perf_score, 1),
            "core_web_vitals_passed": cwv_pass,
            "metrics": {
                "fcp_ms": fcp,
                "lcp_ms": lcp,
                "cls": cls,
                "tbt_ms": tbt,
                "speed_index_ms": cwv.get("speed_index_ms", 2200),
            },
            "opportunities_count": len(pagespeed_data.get("opportunities", [])),
        }
        return round(perf_score, 1), telemetry


class SEOScorer:
    """Evaluates SEMrush search intelligence and on-page technical SEO hygiene."""

    def score(self, semrush_data: Dict[str, Any], ui_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        traffic = semrush_data.get("organic_traffic", 0)
        keywords = semrush_data.get("organic_keywords", 0)
        domain_rank = semrush_data.get("domain_rank", 0)
        traffic_cost = semrush_data.get("organic_cost", 0.0)

        # Search footprint subscore (0 - 60)
        search_subscore = 30.0
        if keywords >= SEO_THRESHOLDS["high_keywords"]:
            search_subscore += 20.0
        elif keywords >= SEO_THRESHOLDS["moderate_keywords"]:
            search_subscore += 12.0
        elif keywords >= SEO_THRESHOLDS["low_keywords"]:
            search_subscore += 6.0

        if traffic >= SEO_THRESHOLDS["high_traffic"]:
            search_subscore += 10.0
        elif traffic >= SEO_THRESHOLDS["moderate_traffic"]:
            search_subscore += 6.0
        elif traffic >= SEO_THRESHOLDS["low_traffic"]:
            search_subscore += 3.0

        # Technical on-page SEO subscore (0 - 40)
        tech_subscore = 0.0
        if ui_data.get("has_title_tag") and (30 <= ui_data.get("title_length", 0) <= 70):
            tech_subscore += 15.0
        elif ui_data.get("has_title_tag"):
            tech_subscore += 8.0

        if ui_data.get("has_meta_description"):
            tech_subscore += 10.0
        if ui_data.get("has_canonical"):
            tech_subscore += 5.0
        if ui_data.get("has_og_tags"):
            tech_subscore += 5.0
        if ui_data.get("has_h1"):
            tech_subscore += 5.0

        total_seo = min(100.0, max(25.0, round(search_subscore + tech_subscore, 1)))

        telemetry = {
            "score": total_seo,
            "organic_traffic": traffic,
            "organic_keywords": keywords,
            "domain_rank": domain_rank,
            "organic_cost": traffic_cost,
            "has_title_tag": ui_data.get("has_title_tag", False),
            "has_meta_description": ui_data.get("has_meta_description", False),
        }
        return total_seo, telemetry


class LeadGenScorer:
    """Evaluates lead conversion funnels, forms, phone numbers, and chat widgets."""

    def score(self, lead_gen_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        raw_score = lead_gen_data.get("lead_gen_score", 65.0)
        final_score = min(100.0, max(15.0, round(raw_score, 1)))

        telemetry = {
            "score": final_score,
            "has_contact_form": lead_gen_data.get("has_contact_form", False),
            "has_phone_number": lead_gen_data.get("has_phone_number", False),
            "has_email_address": lead_gen_data.get("has_email_address", False),
            "has_live_chat": lead_gen_data.get("has_live_chat", False),
            "has_booking_widget": lead_gen_data.get("has_booking_widget", False),
            "detected_ctas_count": len(lead_gen_data.get("detected_ctas", [])),
            "form_providers": lead_gen_data.get("form_providers", []),
            "chat_providers": lead_gen_data.get("chat_providers", []),
        }
        return final_score, telemetry


class UIUXScorer:
    """Evaluates mobile responsiveness, image alt coverage, SSL, and accessibility."""

    def score(self, ui_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        raw_score = ui_data.get("ui_ux_score", 70.0)
        final_score = min(100.0, max(20.0, round(raw_score, 1)))

        telemetry = {
            "score": final_score,
            "mobile_responsive": ui_data.get("mobile_responsive", False),
            "alt_coverage_percent": ui_data.get("alt_coverage_percent", 100.0),
            "missing_alt_count": ui_data.get("missing_alt_tags_count", 0),
            "has_ssl": ui_data.get("has_ssl", True),
            "mixed_content_count": ui_data.get("mixed_content_count", 0),
            "h1_count": ui_data.get("h1_count", 1),
            "has_html_lang": ui_data.get("has_html_lang", True),
        }
        return final_score, telemetry


class BrokenLinksScorer:
    """Evaluates broken links and dead redirect ratios."""

    def score(self, broken_links_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        raw_score = broken_links_data.get("broken_links_score", 90.0)
        final_score = min(100.0, max(20.0, round(raw_score, 1)))

        telemetry = {
            "score": final_score,
            "total_links_checked": broken_links_data.get("total_links_checked", 0),
            "broken_links_count": broken_links_data.get("broken_links_count", 0),
            "internal_broken_count": broken_links_data.get("internal_broken_count", 0),
            "external_broken_count": broken_links_data.get("external_broken_count", 0),
        }
        return final_score, telemetry


performance_scorer = PerformanceScorer()
seo_scorer = SEOScorer()
lead_gen_scorer = LeadGenScorer()
ui_ux_scorer = UIUXScorer()
broken_links_scorer = BrokenLinksScorer()
