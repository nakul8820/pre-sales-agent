"""Industry benchmarks, metric thresholds, and letter grade conversion rules for scoring website audits."""
from typing import Dict, Tuple

# Core Web Vitals Google Thresholds (ms, unitless)
CWV_THRESHOLDS = {
    "lcp_good": 2500,  # <= 2.5s is Good
    "lcp_poor": 4000,  # > 4.0s is Poor
    "fcp_good": 1800,  # <= 1.8s is Good
    "fcp_poor": 3000,  # > 3.0s is Poor
    "cls_good": 0.10,  # <= 0.1 is Good
    "cls_poor": 0.25,  # > 0.25 is Poor
    "tbt_good": 200,   # <= 200ms is Good
    "tbt_poor": 600,   # > 600ms is Poor
}

# SEO Traffic and Authority Tiers
SEO_THRESHOLDS = {
    "high_traffic": 10000,
    "moderate_traffic": 1000,
    "low_traffic": 250,
    "high_keywords": 1000,
    "moderate_keywords": 100,
    "low_keywords": 25,
}

# Letter Grade Tiers
GRADE_TIERS: Dict[str, Tuple[float, str, str]] = {
    "A": (85.0, "Excellent", "var(--status-success)"),
    "B": (70.0, "Good", "var(--accent-cyan)"),
    "C": (50.0, "Fair", "var(--status-warning)"),
    "D": (30.0, "Needs Work", "var(--status-warning)"),
    "F": (0.0, "Critical Overhaul", "var(--status-danger)"),
}


def calculate_letter_grade(score: float) -> Tuple[str, str, str]:
    """Converts a numerical score (0-100) to a letter grade, label, and UI color."""
    if score >= 85.0:
        return "A", "Excellent", "var(--status-success)"
    elif score >= 70.0:
        return "B", "Good", "var(--accent-cyan)"
    elif score >= 50.0:
        return "C", "Fair", "var(--status-warning)"
    elif score >= 30.0:
        return "D", "Needs Work", "var(--status-warning)"
    else:
        return "F", "Critical Overhaul", "var(--status-danger)"
