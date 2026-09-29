"""Automated heuristic content-appropriateness moderator and pre-report safety gate."""
import re
from typing import Any, Dict, List, Optional
from app.models.rating_flag import FlagCategory
from app.utils.logger import logger

MODERATION_RULES: Dict[FlagCategory, Dict[str, Any]] = {
    FlagCategory.UNDER_CONSTRUCTION: {
        "severity": "high",
        "patterns": [
            r"\bunder[-_\s]*construction\b",
            r"\bsite\s+is\s+under\s+construction\b",
            r"\bcoming[-_\s]*soon\b",
            r"\bwebsite[-_\s]*coming[-_\s]*soon\b",
            r"\blorem\s+ipsum\s+dolor\s+sit\s+amet\b",
            r"\bdefault\s+web\s+page\b",
            r"\btest\s+page\s+for\s+apache\b",
            r"\bwelcome\s+to\s+nginx\b",
            r"\bholding\s+page\b",
            r"\bsite\s+in\s+progress\b",
        ],
        "risk_description": "Prospect website appears to be under construction or using placeholder template text.",
    },
    FlagCategory.PARKED_DOMAIN: {
        "severity": "high",
        "patterns": [
            r"\bthis\s+domain\s+is\s+for\s+sale\b",
            r"\bbuy\s+this\s+domain\b",
            r"\bparked[-_\s]*domain\b",
            r"\bdomain[-_\s]*parked\b",
            r"\bdomain\s+is\s+registered\b",
        ],
        "risk_description": "Domain is parked or listed for sale, with no active business website.",
    },
    FlagCategory.ADULT_CONTENT: {
        "severity": "critical",
        "patterns": [
            r"\bporn\b",
            r"\bpornography\b",
            r"\bxxx\b",
            r"\bsex[-_\s]*cam\b",
            r"\badult[-_\s]*dating\b",
            r"\bescort[-_\s]*service\b",
            r"\berotic\b",
            r"\bnsfw\b",
            r"\bonlyfans\b",
            r"\badult[-_\s]*content\b",
        ],
        "risk_description": "Site contains adult or explicit NSFW content unsuitable for business pitch outreach.",
    },
    FlagCategory.GAMBLING: {
        "severity": "high",
        "patterns": [
            r"\bcasino\b",
            r"\bslots?\b",
            r"\bgambling\b",
            r"\bonline[-_\s]*casino\b",
            r"\bslot[-_\s]*machines?\b",
            r"\bsports[-_\s]*betting\b",
            r"\bbet[-_\s]*online\b",
            r"\bpoker[-_\s]*room\b",
            r"\bcrypto[-_\s]*casino\b",
            r"\bdeposit\s+bonus\b",
            r"\bfree\s+spins\b",
            r"\broulette\b",
            r"\bblackjack\b",
            r"\bwager\b",
        ],
        "risk_description": "Site operates as an online gambling, sports betting, or casino platform.",
    },
    FlagCategory.POLITICAL_CONTENT: {
        "severity": "medium",
        "patterns": [
            r"\belection[-_\s]*campaign\b",
            r"\bpolitical\s+action\s+committee\b",
            r"\bvote\s+for\s+[a-z]+\b",
            r"\bpartisan\s+pac\b",
            r"\bcampaign\s+contributions?\b",
            r"\bpolitical\s+party\s+headquarters\b",
        ],
        "risk_description": "Site is affiliated with partisan political campaigning or candidate lobbying.",
    },
    FlagCategory.MALICIOUS: {
        "severity": "critical",
        "patterns": [
            r"\bverify\s+your\s+crypto\s+wallet\b",
            r"\benter\s+your\s+seed\s+phrase\b",
            r"\bdownload\s+cracked\s+software\b",
            r"\bfree\s+robux\s+generator\b",
            r"\baccount\s+suspended\s+verify\s+login\b",
            r"\bcall\s+microsoft\s+support\s+immediately\b",
        ],
        "risk_description": "Phishing or suspicious credential collection signals detected on website.",
    },
}


class ContentAppropriatenessModerator:
    """Evaluates prospect websites against safety heuristics to gate sales outreach reports."""

    def evaluate(
        self,
        domain: str,
        website_url: str,
        company_name: Optional[str] = None,
        notes: Optional[str] = None,
        crawler_data: Optional[Dict[str, Any]] = None,
        raw_text_samples: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Evaluates domain, company name, titles, meta tags, and crawled text for inappropriate content."""
        detected_flags: List[Dict[str, Any]] = []

        # Combine text content from crawler, domain, company_name, and notes
        text_corpus = [domain.lower(), website_url.lower()]

        if company_name:
            text_corpus.append(company_name.lower())
        if notes:
            text_corpus.append(notes.lower())

        if crawler_data:
            ui = crawler_data.get("ui_ux", {})
            if ui.get("title_tag"):
                text_corpus.append(ui["title_tag"].lower())
            if ui.get("meta_description"):
                text_corpus.append(ui["meta_description"].lower())

        if raw_text_samples:
            for s in raw_text_samples:
                if s:
                    text_corpus.append(s.lower()[:3000])

        combined_text = " ".join(text_corpus)

        for category, rule in MODERATION_RULES.items():
            matched_keywords: List[str] = []
            snippet: Optional[str] = None

            for pattern in rule["patterns"]:
                match = re.search(pattern, combined_text, re.I)
                if match:
                    matched_keywords.append(match.group(0))
                    if not snippet:
                        start = max(0, match.start() - 25)
                        end = min(len(combined_text), match.end() + 25)
                        snippet = f"...{combined_text[start:end].strip()}..."

            if matched_keywords:
                match_count = len(matched_keywords)
                confidence = min(0.99, round(0.70 + (match_count * 0.1), 2))
                severity = rule["severity"]

                detected_flags.append({
                    "category": category,
                    "severity": severity,
                    "confidence_score": confidence,
                    "flagged_keywords": list(set(matched_keywords)),
                    "snippet": snippet or matched_keywords[0],
                    "description": rule["risk_description"],
                })

        has_critical_flag = any(f["severity"] in ("critical", "high") for f in detected_flags)
        is_safe = not has_critical_flag

        if not is_safe:
            logger.warning(
                f"Content Appropriateness Gate triggered for domain='{domain}'! "
                f"Flags: {[f['category'].value for f in detected_flags]}"
            )
        else:
            logger.info(f"Content Appropriateness Gate PASSED for domain='{domain}' (Safe for pitch)")

        return {
            "domain": domain,
            "is_safe": is_safe,
            "has_critical_flag": has_critical_flag,
            "flags_count": len(detected_flags),
            "flags": detected_flags,
            "status_label": "Approved for Pitching" if is_safe else "Flagged for Content Review",
        }


content_moderator = ContentAppropriatenessModerator()
