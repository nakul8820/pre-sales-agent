"""Asynchronous depth-limited, rate-limited website spider with robots.txt compliance and multi-audit aggregation."""
import asyncio
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Set
import httpx

from app.core.config import settings
from app.schemas.common_prospect import extract_clean_domain, normalize_url
from app.services.crawler.broken_links import broken_link_detector
from app.services.crawler.lead_gen import lead_gen_auditor
from app.services.crawler.robots import robots_service
from app.services.crawler.ui_audit import ui_technical_auditor
from app.utils.logger import logger

IGNORE_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".css", ".js",
    ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3", ".wav", ".avi", ".mov",
    ".woff", ".woff2", ".ttf", ".eot", ".xml", ".rss", ".atom", ".json"
)


class AsyncSpider:
    """Multi-page crawler enforcing politeness delays, depth limits, and concurrency boundaries."""

    def __init__(
        self,
        max_pages: Optional[int] = None,
        max_depth: Optional[int] = None,
        delay_seconds: Optional[float] = None,
        concurrency: Optional[int] = None,
        request_timeout: Optional[float] = None,
        total_timeout: Optional[float] = None,
    ):
        self.max_pages = max_pages or settings.CRAWLER_MAX_PAGES_PER_SITE
        self.max_depth = max_depth or settings.CRAWLER_MAX_DEPTH
        self.delay_seconds = delay_seconds or settings.CRAWLER_DELAY_BETWEEN_REQUESTS_SECONDS
        self.concurrency = concurrency or settings.CRAWLER_CONCURRENT_REQUESTS_PER_DOMAIN
        self.request_timeout = request_timeout or settings.CRAWLER_REQUEST_TIMEOUT_SECONDS
        self.total_timeout = total_timeout or settings.CRAWLER_TOTAL_SITE_TIMEOUT_SECONDS

    def _is_valid_internal_link(self, url: str, base_domain: str) -> bool:
        """Verifies if the URL is an internal webpage on the target domain."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        link_domain = extract_clean_domain(url)
        if link_domain != base_domain and not link_domain.endswith(f".{base_domain}"):
            return False

        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in IGNORE_EXTENSIONS):
            return False

        return True

    def _extract_page_links(self, html: str, source_url: str, base_domain: str) -> List[str]:
        """Extracts internal links from HTML for BFS queue expansion."""
        discovered: List[str] = []
        raw_hrefs = re.findall(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\']', html, re.I)

        for href in raw_hrefs:
            href = href.strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                continue

            abs_url = urllib.parse.urljoin(source_url, href)
            # Remove fragment
            abs_url = abs_url.split("#")[0]

            if self._is_valid_internal_link(abs_url, base_domain):
                discovered.append(abs_url)

        return discovered

    async def _fetch_page(
        self, client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict[str, Any]]:
        """Fetches a single page with rate-limiting semaphore, delay pacing, and 1 retry with backoff."""
        async with semaphore:
            # Respect robots.txt
            is_allowed = await robots_service.can_fetch(url)
            if not is_allowed:
                logger.info(f"Skipping '{url}' (Disallowed by robots.txt)")
                return None

            # Rate limit pacing delay
            if self.delay_seconds > 0:
                await asyncio.sleep(self.delay_seconds)

            for attempt in range(settings.CRAWLER_MAX_RETRIES + 1):
                try:
                    start_time = time.time()
                    res = await client.get(url, timeout=self.request_timeout, follow_redirects=True)
                    elapsed_ms = round((time.time() - start_time) * 1000)

                    content_type = res.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and not content_type.startswith("text/"):
                        return None

                    return {
                        "url": str(res.url),
                        "status_code": res.status_code,
                        "html": res.text,
                        "response_time_ms": elapsed_ms,
                    }
                except (httpx.TimeoutException, httpx.RequestError) as e:
                    if attempt < settings.CRAWLER_MAX_RETRIES:
                        await asyncio.sleep(1.0)  # Exponential backoff
                        continue
                    logger.debug(f"Failed to fetch page '{url}': {e}")
                    return None

        return None

    async def crawl(self, start_url: str) -> Dict[str, Any]:
        """Performs depth-limited, rate-limited crawl on the target website."""
        norm_start_url = normalize_url(start_url)
        base_domain = extract_clean_domain(norm_start_url)

        logger.info(
            f"Starting spider crawl on '{norm_start_url}' "
            f"(Max pages: {self.max_pages}, Max depth: {self.max_depth}, Domain: {base_domain})"
        )

        visited_urls: Set[str] = set()
        pages_data: List[Dict[str, Any]] = []
        
        # Queue item: (url, depth)
        queue: List[tuple[str, int]] = [(norm_start_url, 0)]
        visited_urls.add(norm_start_url)

        semaphore = asyncio.Semaphore(self.concurrency)
        crawl_start_time = time.time()

        headers = {
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(headers=headers, verify=False) as client:
            while queue and len(pages_data) < self.max_pages:
                # Check global site crawl timeout
                if (time.time() - crawl_start_time) > self.total_timeout:
                    logger.warning(f"Crawl total timeout ({self.total_timeout}s) exceeded for {base_domain}")
                    break

                current_url, current_depth = queue.pop(0)

                page_res = await self._fetch_page(client, current_url, semaphore)
                if not page_res or page_res.get("status_code") != 200:
                    continue

                page_res["depth"] = current_depth
                pages_data.append(page_res)

                # Discover new links if depth limit not reached
                if current_depth < self.max_depth and len(pages_data) + len(queue) < self.max_pages:
                    discovered = self._extract_page_links(page_res.get("html", ""), page_res.get("url", ""), base_domain)
                    for link in discovered:
                        if link not in visited_urls and len(visited_urls) < self.max_pages * 2:
                            visited_urls.add(link)
                            queue.append((link, current_depth + 1))

        crawl_duration_s = round(time.time() - crawl_start_time, 2)
        total_pages = len(pages_data)
        logger.info(f"Spider completed crawl on {base_domain}: {total_pages} pages in {crawl_duration_s}s")

        # Run Audits on collected HTML pages
        lead_gen_results = lead_gen_auditor.audit_pages(pages_data)
        broken_links_results = await broken_link_detector.audit_links(pages_data, base_domain)
        ui_audit_results = ui_technical_auditor.audit_pages(pages_data)

        # Aggregate all critical gaps discovered by the crawler
        crawler_gaps = (
            lead_gen_results.get("gaps", [])
            + broken_links_results.get("gaps", [])
            + ui_audit_results.get("gaps", [])
        )

        return {
            "domain": base_domain,
            "start_url": norm_start_url,
            "pages_crawled_count": total_pages,
            "crawl_duration_seconds": crawl_duration_s,
            "lead_gen": lead_gen_results,
            "broken_links": broken_links_results,
            "ui_ux": ui_audit_results,
            "crawler_gaps": crawler_gaps,
        }


spider_engine = AsyncSpider()
