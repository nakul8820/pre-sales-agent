"""Multi-tiered logo extraction service with Hunter.io, Clearbit, HTML scraping, and Google Favicon fallbacks."""
import re
import urllib.parse
from typing import Optional
import httpx
import redis.asyncio as aioredis

from app.core.config import settings
from app.schemas.common_prospect import extract_clean_domain
from app.utils.logger import logger

CACHE_TTL_SECONDS = 2592000  # 30 Days


class LogoExtractorService:
    """Service for retrieving high-resolution company logos for branded audit pitch decks."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_connection_url

    async def _get_cache(self, domain: str) -> Optional[str]:
        """Retrieves cached logo URL from Redis."""
        try:
            r = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=2.0)
            cached = await r.get(f"logo:{domain}")
            await r.aclose()
            if cached:
                logger.info(f"Logo cache HIT for domain='{domain}'")
                return cached
        except Exception as e:
            logger.warning(f"Redis cache read error for Logo ({domain}): {e}")
        return None

    async def _set_cache(self, domain: str, logo_url: str) -> None:
        """Caches logo URL in Redis with 30-day TTL."""
        try:
            r = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=2.0)
            await r.setex(f"logo:{domain}", CACHE_TTL_SECONDS, logo_url)
            await r.aclose()
            logger.info(f"Logo cached for domain='{domain}'")
        except Exception as e:
            logger.warning(f"Redis cache write error for Logo ({domain}): {e}")

    async def _extract_from_html(self, website_url: str) -> Optional[str]:
        """Scrapes root page HTML for OpenGraph og:image or Apple Touch Icon."""
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                res = await client.get(website_url, headers={"User-Agent": settings.CRAWLER_USER_AGENT})
                if res.status_code == 200:
                    html = res.text

                    # 1. Check og:image
                    og_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.I)
                    if not og_match:
                        og_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html, re.I)
                    if og_match:
                        og_url = og_match.group(1).strip()
                        if og_url.startswith("http"):
                            return og_url
                        return urllib.parse.urljoin(website_url, og_url)

                    # 2. Check apple-touch-icon
                    touch_match = re.search(r'<link\s+rel=["\']apple-touch-icon["\']\s+href=["\']([^"\']+)["\']', html, re.I)
                    if touch_match:
                        icon_url = touch_match.group(1).strip()
                        if icon_url.startswith("http"):
                            return icon_url
                        return urllib.parse.urljoin(website_url, icon_url)
        except Exception as e:
            logger.debug(f"HTML logo extraction skipped for '{website_url}': {e}")
        return None

    async def _check_clearbit(self, domain: str) -> Optional[str]:
        """Checks if Clearbit has a valid logo image for the domain."""
        clearbit_url = f"https://logo.clearbit.com/{domain}"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.head(clearbit_url)
                if res.status_code == 200:
                    return clearbit_url
        except Exception:
            pass
        return None

    async def extract_logo(self, domain_or_url: str, website_url: Optional[str] = None) -> str:
        """Extracts high-resolution logo via 3-tier cascade."""
        domain = extract_clean_domain(domain_or_url)
        target_url = website_url or f"https://{domain}"

        # 1. Check Cache
        cached = await self._get_cache(domain)
        if cached:
            return cached

        # 2. Tier 1: Check Clearbit Logo API
        clearbit_logo = await self._check_clearbit(domain)
        if clearbit_logo:
            await self._set_cache(domain, clearbit_logo)
            return clearbit_logo

        # 3. Tier 2: Scrape HTML for og:image / touch-icon
        html_logo = await self._extract_from_html(target_url)
        if html_logo:
            await self._set_cache(domain, html_logo)
            return html_logo

        # 4. Tier 3: Google Favicon High-Res Service Fallback
        google_favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        await self._set_cache(domain, google_favicon)
        return google_favicon


logo_service = LogoExtractorService()
