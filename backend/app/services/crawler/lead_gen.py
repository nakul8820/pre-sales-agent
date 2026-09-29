"""Lead Generation Gap Analysis auditor for contact forms, CTAs, phone numbers, and chat widgets."""
import re
from typing import Any, Dict, List, Set
from app.utils.logger import logger

PHONE_REGEX = re.compile(r'(?:\+?(\d{1,3}))?[-.\s]?(?:\(?(\d{3})\)?[-.\s]?)(\d{3})[-.\s]?(\d{4})')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

CTA_KEYWORDS = [
    "book a demo", "schedule demo", "request demo", "book demo",
    "request a quote", "get a quote", "request pricing", "get pricing",
    "free consultation", "schedule consultation", "talk to sales", "contact sales",
    "get started", "start free trial", "free trial", "try for free", "sign up free",
    "book a call", "schedule a call", "book appointment", "reserve now"
]

CHAT_WIDGET_SIGNALS = [
    ("Intercom", ["widget.intercom.io", "intercomsettings", "intercom-frame"]),
    ("Drift", ["js.driftt.com", "drift.load", "driftt"]),
    ("HubSpot Chat", ["js.hs-scripts.com", "conversations-embed", "hubspot-messages"]),
    ("Zendesk", ["static.zdassets.com", "zopim", "zendesk-embed"]),
    ("Crisp", ["client.crisp.chat", "$crisp"]),
    ("LiveChat", ["cdn.livechatinc.com", "__livechat"]),
    ("Tidio", ["code.tidio.co", "tidio-chat"]),
    ("Calendly", ["calendly.com/assets", "calendly-inline-widget"]),
    ("ChiliPiper", ["js.chilipiper.com", "chilipiper"]),
]

FORM_SIGNALS = [
    ("HubSpot Forms", ["js.hsforms.net", "hbspt.forms.create"]),
    ("Marketo", ["marketo.com", "mktform"]),
    ("Typeform", ["typeform.com", "embed.typeform.com"]),
    ("Pardot", ["pardot.com"]),
    ("JotForm", ["jotform.com"]),
    ("ActiveCampaign", ["activecampaign.com"]),
]


class LeadGenAuditor:
    """Audits HTML pages for conversion funnels and lead generation gaps."""

    def audit_pages(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates lead-gen analysis across all visited pages of a domain."""
        has_contact_form = False
        has_phone_number = False
        has_email_address = False
        has_live_chat = False
        has_booking_widget = False
        has_newsletter = False
        
        detected_phones: Set[str] = set()
        detected_emails: Set[str] = set()
        detected_ctas: Set[str] = set()
        detected_chat_providers: Set[str] = set()
        detected_form_providers: Set[str] = set()
        form_count = 0

        for page in pages_data:
            html = page.get("html", "")
            url = page.get("url", "")
            html_lower = html.lower()

            # 1. Detect Phone Numbers
            # a) tel: links
            tel_matches = re.findall(r'href=["\']tel:([^"\']+)["\']', html, re.I)
            for m in tel_matches:
                clean_tel = re.sub(r'[^\d+]', '', m)
                if len(clean_tel) >= 7:
                    detected_phones.add(m.strip())
                    has_phone_number = True

            # b) regex text phones
            text_phones = PHONE_REGEX.findall(html)
            if text_phones:
                has_phone_number = True
                for p in text_phones[:3]:
                    detected_phones.add("-".join(filter(None, p)))

            # 2. Detect Email addresses & mailto:
            mailto_matches = re.findall(r'href=["\']mailto:([^"?\'\s]+)', html, re.I)
            for em in mailto_matches:
                if "@" in em:
                    detected_emails.add(em.strip().lower())
                    has_email_address = True

            # 3. Detect Forms (native HTML + embedded CRM forms)
            if "<form" in html_lower:
                has_contact_form = True
                form_count += html_lower.count("<form")

            for provider, patterns in FORM_SIGNALS:
                if any(p in html_lower for p in patterns):
                    has_contact_form = True
                    detected_form_providers.add(provider)

            # 4. Detect Live Chat & Scheduling Widgets
            for provider, patterns in CHAT_WIDGET_SIGNALS:
                if any(p in html_lower for p in patterns):
                    if provider in ("Calendly", "ChiliPiper"):
                        has_booking_widget = True
                    else:
                        has_live_chat = True
                        detected_chat_providers.add(provider)

            # 5. Detect Conversion CTAs in buttons & links
            for kw in CTA_KEYWORDS:
                if kw in html_lower:
                    detected_ctas.add(kw.title())

            # 6. Detect Newsletter / Lead Magnets
            if any(n in html_lower for n in ["newsletter", "subscribe to", "get our guide", "download whitepaper", "join our list"]):
                if "<input" in html_lower:
                    has_newsletter = True

        # Calculate Lead Generation Score (0 - 100)
        score = 0.0
        if has_contact_form:
            score += 30.0
        if has_phone_number or has_email_address:
            score += 20.0
        if len(detected_ctas) > 0:
            score += 20.0
        if has_live_chat or has_booking_widget:
            score += 20.0
        if has_newsletter:
            score += 10.0

        lead_gen_score = min(100.0, max(15.0, round(score, 1)))

        # Identify Gaps for Sales Rep Pitch Angles
        gaps: List[Dict[str, Any]] = []
        if not has_contact_form:
            gaps.append({
                "category": "Lead Generation",
                "severity": "high",
                "title": "Missing Lead Capture / Contact Forms",
                "description": "No digital lead capture forms discovered on the website.",
                "impact": "Prospect is losing potential inbound discovery requests and RFQs.",
                "pitch_angle": "Pitch high-converting inbound form funnels & CRM integration.",
            })

        if not has_live_chat and not has_booking_widget:
            gaps.append({
                "category": "Lead Generation",
                "severity": "medium",
                "title": "No Instant Live Chat or Self-Scheduling Funnel",
                "description": "Website lacks immediate engagement tools (e.g. Intercom, HubSpot Chat, Calendly).",
                "impact": "High-intent buyers who prefer immediate answers leave without converting.",
                "pitch_angle": "Offer instant chat qualification bots & automated calendar booking widgets.",
            })

        if not has_phone_number:
            gaps.append({
                "category": "Lead Generation",
                "severity": "medium",
                "title": "No Direct Click-to-Call Phone Number",
                "description": "Website does not provide clickable 'tel:' contact links in the header/footer.",
                "impact": "Friction for mobile visitors wanting immediate phone assistance.",
                "pitch_angle": "Add prominent click-to-call mobile header actions.",
            })

        if len(detected_ctas) == 0:
            gaps.append({
                "category": "Lead Generation",
                "severity": "high",
                "title": "Weak or Missing Conversion CTAs",
                "description": "No primary action-oriented call-to-action buttons (e.g., 'Book a Demo', 'Request Quote').",
                "impact": "Passive website copy fails to guide visitors into sales pipeline.",
                "pitch_angle": "Implement structured hero CTAs with high-visibility button styling.",
            })

        return {
            "lead_gen_score": lead_gen_score,
            "has_contact_form": has_contact_form,
            "has_phone_number": has_phone_number,
            "has_email_address": has_email_address,
            "has_live_chat": has_live_chat,
            "has_booking_widget": has_booking_widget,
            "has_newsletter": has_newsletter,
            "form_count": form_count,
            "detected_phones": list(detected_phones)[:5],
            "detected_emails": list(detected_emails)[:5],
            "detected_ctas": list(detected_ctas)[:6],
            "chat_providers": list(detected_chat_providers),
            "form_providers": list(detected_form_providers),
            "gaps": gaps,
        }


lead_gen_auditor = LeadGenAuditor()
