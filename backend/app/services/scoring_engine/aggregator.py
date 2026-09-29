"""Scoring Engine Aggregator computing weighted scores, letter grades, and prioritized critical focus lists."""
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.services.scoring_engine.benchmarks import calculate_letter_grade
from app.services.scoring_engine.category_scorers import (
    broken_links_scorer,
    lead_gen_scorer,
    performance_scorer,
    seo_scorer,
    ui_ux_scorer,
)


class ScoringEngineAggregator:
    """Orchestrates individual category scoring, applies weights, and prioritizes sales pitch recommendations."""

    def __init__(self):
        self.default_weights = {
            "performance": settings.WEIGHT_PERFORMANCE,
            "seo": settings.WEIGHT_SEO,
            "lead_gen": settings.WEIGHT_LEAD_GEN,
            "ui_ux": settings.WEIGHT_UI_UX,
            "broken_links": settings.WEIGHT_BROKEN_LINKS,
        }

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalizes custom or default weights so the sum equals 1.0."""
        total = sum(weights.values())
        if total <= 0:
            return self.default_weights
        return {k: round(v / total, 4) for k, v in weights.items()}

    def _extract_and_rank_critical_focus_areas(
        self,
        pagespeed_data: Dict[str, Any],
        semrush_data: Dict[str, Any],
        crawler_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Collects, deduplicates, and ranks all audit gaps by severity and sales pitch leverage."""
        focus_items: List[Dict[str, Any]] = []

        # 1. PageSpeed Bottlenecks
        for opp in pagespeed_data.get("opportunities", [])[:2]:
            focus_items.append({
                "category": "Performance",
                "severity": opp.get("severity", "medium"),
                "title": opp.get("title", "Performance bottleneck identified"),
                "description": opp.get("display_value", "Asset optimization identified by Google Lighthouse."),
                "impact": "Slow loading speed negatively impacts Google Core Web Vitals rankings and visitor conversions.",
                "pitch_angle": "Propose modern frontend asset bundling, image compression, and edge caching architecture.",
            })

        # 2. SEMrush Search Gap
        traffic = semrush_data.get("organic_traffic", 0)
        keywords = semrush_data.get("organic_keywords", 0)
        if traffic < 1000 or keywords < 100:
            focus_items.append({
                "category": "SEO",
                "severity": "high" if traffic < 200 else "medium",
                "title": "Low Organic Search Footprint & Keyword Gaps",
                "description": f"Domain ranks for only ~{keywords} organic keywords with estimated ~{traffic} monthly visitors.",
                "impact": "Missing out on qualified buyer search intent in your target sector.",
                "pitch_angle": "Pitch targeted technical SEO and high-intent commercial keyword content expansion.",
            })

        # 3. Crawler Gaps (Lead Gen, Broken Links, UI/UX)
        focus_items.extend(crawler_data.get("crawler_gaps", []))

        # Severity sort order: high (0) -> medium (1) -> low (2)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        ranked = sorted(focus_items, key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        # Deduplicate by title
        seen_titles = set()
        deduped = []
        for item in ranked:
            t = item.get("title")
            if t not in seen_titles:
                seen_titles.add(t)
                deduped.append(item)

        return deduped[:6]

    def calculate_scores(
        self,
        pagespeed_data: Dict[str, Any],
        semrush_data: Dict[str, Any],
        crawler_data: Dict[str, Any],
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Calculates all 5 category scores, applies normalized weights, and synthesizes overall score & letter grade."""
        ui_data = crawler_data.get("ui_ux", {})
        lead_data = crawler_data.get("lead_gen", {})
        links_data = crawler_data.get("broken_links", {})

        # Compute Category Scores
        perf_score, perf_telemetry = performance_scorer.score(pagespeed_data)
        seo_score, seo_telemetry = seo_scorer.score(semrush_data, ui_data)
        lead_score, lead_telemetry = lead_gen_scorer.score(lead_data)
        ui_score, ui_telemetry = ui_ux_scorer.score(ui_data)
        links_score, links_telemetry = broken_links_scorer.score(links_data)

        # Apply Weights
        raw_weights = custom_weights or self.default_weights
        weights = self._normalize_weights(raw_weights)

        overall_score = round(
            (perf_score * weights["performance"])
            + (seo_score * weights["seo"])
            + (lead_score * weights["lead_gen"])
            + (ui_score * weights["ui_ux"])
            + (links_score * weights["broken_links"]),
            1,
        )

        letter_grade, grade_label, grade_color = calculate_letter_grade(overall_score)
        critical_focus_areas = self._extract_and_rank_critical_focus_areas(
            pagespeed_data, semrush_data, crawler_data
        )

        return {
            "overall_score": overall_score,
            "letter_grade": letter_grade,
            "grade_label": grade_label,
            "grade_color": grade_color,
            "category_scores": {
                "performance": perf_score,
                "seo": seo_score,
                "lead_gen": lead_score,
                "ui_ux": ui_score,
                "broken_links": links_score,
            },
            "category_weights": weights,
            "telemetry": {
                "performance": perf_telemetry,
                "seo": seo_telemetry,
                "lead_gen": lead_telemetry,
                "ui_ux": ui_telemetry,
                "broken_links": links_telemetry,
            },
            "critical_focus_areas": critical_focus_areas,
        }


scoring_aggregator = ScoringEngineAggregator()
