"""Broken Link Detection engine for auditing internal/external link health, 404s, and dead redirects."""
import asyncio
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple
import httpx

from app.core.config import settings
from app.schemas.common_prospect import extract_clean_domain
from app.utils.logger import logger


class BrokenLinkDetector:
    """Extracts and verifies links discovered across crawled pages."""

    def __init__(self, max_links_to_check: int = 50, timeout: float = 6.0):
        self.max_links_to_check = max_links_to_check
        self.timeout = timeout

    def extract_links(self, pages_data: List[Dict[str, Any]], base_domain: str) -> List[Tuple[str, str, bool]]:
        """Extracts unique hyperlinks (url, source_page, is_internal)."""
        seen_urls: Set[str] = set()
        links_to_check: List[Tuple[str, str, bool]] = []

        for page in pages_data:
            html = page.get("html", "")
            source_url = page.get("url", "")

            # Regex extract href attributes
            raw_hrefs = re.findall(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\']', html, re.I)

            for href in raw_hrefs:
                href = href.strip()
                # Ignore non-http links (tel, mailto, javascript, anchors)
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                    continue

                abs_url = urllib.parse.urljoin(source_url, href)
                # Strip fragment
                abs_url = abs_url.split("#")[0]

                if abs_url in seen_urls:
                    continue
                seen_urls.add(abs_url)

                link_domain = extract_clean_domain(abs_url)
                is_internal = (link_domain == base_domain) or link_domain.endswith(f".{base_domain}")

                links_to_check.append((abs_url, source_url, is_internal))

                if len(links_to_check) >= self.max_links_to_check:
                    break

            if len(links_to_check) >= self.max_links_to_check:
                break

        return links_to_check

    async def _check_single_link(
        self, client: httpx.AsyncClient, url: str, source_page: str, is_internal: bool, semaphore: asyncio.Semaphore
    ) -> Optional[Dict[str, Any]]:
        """Verifies status of a single link with concurrency throttling."""
        async with semaphore:
            try:
                # Try HEAD first for performance
                res = await client.head(url, timeout=self.timeout, follow_redirects=True)
                # Fallback to GET if method not allowed (405) or bad request (400)
                if res.status_code in (400, 405):
                    res = await client.get(url, timeout=self.timeout, follow_redirects=True)

                if res.status_code >= 400:
                    return {
                        "url": url,
                        "status_code": res.status_code,
                        "source_page": source_page,
                        "is_internal": is_internal,
                        "error_type": "HTTP Error" if res.status_code != 404 else "404 Not Found",
                    }
            except httpx.TimeoutException:
                return {
                    "url": url,
                    "status_code": None,
                    "source_page": source_page,
                    "is_internal": is_internal,
                    "error_type": "Request Timeout",
                }
            except Exception as e:
                return {
                    "url": url,
                    "status_code": None,
                    "source_page": source_page,
                    "is_internal": is_internal,
                    "error_type": f"Connection Error: {type(e).__name__}",
                }
            return None

    async def audit_links(self, pages_data: List[Dict[str, Any]], base_domain: str) -> Dict[str, Any]:
        """Concurrently audits links extracted across crawled pages."""
        links = self.extract_links(pages_data, base_domain)
        semaphore = asyncio.Semaphore(10)
        broken_items: List[Dict[str, Any]] = []

        headers = {
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        async with httpx.AsyncClient(headers=headers, verify=False) as client:
            tasks = [
                self._check_single_link(client, url, source, is_int, semaphore)
                for url, source, is_int in links
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, dict) and res is not None:
                    broken_items.append(res)

        total_checked = len(links)
        broken_count = len(broken_items)

        # Compute Broken Links Score (0 - 100)
        # Deduct 6 pts per internal broken link, 3 pts per external
        internal_broken = sum(1 for b in broken_items if b.get("is_internal"))
        external_broken = broken_count - internal_broken

        deduction = (internal_broken * 6.0) + (external_broken * 3.0)
        broken_links_score = max(20.0, min(100.0, round(100.0 - deduction, 1)))

        gaps: List[Dict[str, Any]] = []
        if broken_count > 0:
            gaps.append({
                "category": "Broken Links",
                "severity": "high" if internal_broken > 0 else "medium",
                "title": f"{broken_count} Defunct / 404 Links Detected",
                "description": f"Discovered {internal_broken} internal broken links and {external_broken} dead external references across scanned pages.",
                "impact": "Dead links destroy visitor trust, leak SEO PageRank, and break conversion funnels.",
                "pitch_angle": "Highlight specific dead links during sales pitch as immediate quick wins.",
            })

        return {
            "broken_links_score": broken_links_score,
            "total_links_checked": total_checked,
            "broken_links_count": broken_count,
            "internal_broken_count": internal_broken,
            "external_broken_count": external_broken,
            "broken_links": broken_items[:10],
            "gaps": gaps,
        }


broken_link_detector = BrokenLinkDetector()
