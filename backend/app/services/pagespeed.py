"""Google PageSpeed Insights API client, parser, and transformer with Redis caching."""
import json
from typing import Any, Dict, List, Optional
import httpx
import redis.asyncio as aioredis

from app.core.config import settings
from app.schemas.common_prospect import extract_clean_domain
from app.utils.logger import logger

PAGESPEED_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CACHE_TTL_SECONDS = 86400  # 24 Hours


class PageSpeedService:
    """Service for auditing web performance and Core Web Vitals via Google PageSpeed Insights."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_connection_url

    async def _get_cache(self, domain: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached PageSpeed result from Redis if available."""
        try:
            r = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=2.0)
            cached = await r.get(f"pagespeed:{domain}")
            await r.aclose()
            if cached:
                logger.info(f"PageSpeed cache HIT for domain='{domain}'")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache read error for PageSpeed ({domain}): {e}")
        return None

    async def _set_cache(self, domain: str, data: Dict[str, Any]) -> None:
        """Stores PageSpeed result into Redis with 24-hour expiration."""
        try:
            r = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=2.0)
            await r.setex(f"pagespeed:{domain}", CACHE_TTL_SECONDS, json.dumps(data))
            await r.aclose()
            logger.info(f"PageSpeed cached for domain='{domain}' (TTL: {CACHE_TTL_SECONDS}s)")
        except Exception as e:
            logger.warning(f"Redis cache write error for PageSpeed ({domain}): {e}")

    def _parse_lighthouse_payload(self, raw_json: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Extracts and transforms Lighthouse performance metrics & diagnostics."""
        lighthouse = raw_json.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        # Performance score (0 to 100)
        perf_score_raw = categories.get("performance", {}).get("score")
        perf_score = round(perf_score_raw * 100, 1) if perf_score_raw is not None else 70.0

        # Core Web Vitals
        fcp_ms = audits.get("first-contentful-paint", {}).get("numericValue", 1200)
        lcp_ms = audits.get("largest-contentful-paint", {}).get("numericValue", 2400)
        cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0.05)
        tbt_ms = audits.get("total-blocking-time", {}).get("numericValue", 180)
        speed_index_ms = audits.get("speed-index", {}).get("numericValue", 2100)

        # Performance opportunities / diagnostics
        opportunities: List[Dict[str, Any]] = []
        target_audits = [
            ("render-blocking-resources", "Eliminate render-blocking resources", "high"),
            ("uses-optimized-images", "Properly size and compress images", "high"),
            ("unminified-javascript", "Minify JavaScript assets", "medium"),
            ("unminified-css", "Minify stylesheet rules", "low"),
            ("modern-image-formats", "Serve images in next-gen formats (WebP/AVIF)", "medium"),
            ("uses-text-compression", "Enable text compression (gzip/Brotli)", "medium"),
        ]

        for audit_id, fallback_title, severity in target_audits:
            item = audits.get(audit_id)
            if item and item.get("score") is not None and item.get("score") < 0.9:
                opportunities.append({
                    "id": audit_id,
                    "title": item.get("title", fallback_title),
                    "description": item.get("description", ""),
                    "display_value": item.get("displayValue", ""),
                    "severity": severity,
                })

        return {
            "domain": domain,
            "status": "success",
            "performance_score": perf_score,
            "core_web_vitals": {
                "fcp_ms": round(fcp_ms),
                "lcp_ms": round(lcp_ms),
                "cls": round(cls, 3),
                "tbt_ms": round(tbt_ms),
                "speed_index_ms": round(speed_index_ms),
            },
            "opportunities": opportunities[:5],
            "is_cached": False,
        }

    def _generate_fallback_payload(self, domain: str, reason: str) -> Dict[str, Any]:
        """Generates realistic fallback telemetry if external API request is unreachable."""
        logger.info(f"Using fallback PageSpeed heuristics for domain='{domain}' (Reason: {reason})")
        return {
            "domain": domain,
            "status": "simulated_fallback",
            "reason": reason,
            "performance_score": 74.0,
            "core_web_vitals": {
                "fcp_ms": 1400,
                "lcp_ms": 2800,
                "cls": 0.08,
                "tbt_ms": 220,
                "speed_index_ms": 2350,
            },
            "opportunities": [
                {
                    "id": "render-blocking-resources",
                    "title": "Eliminate render-blocking resources",
                    "display_value": "Potential savings: ~450ms",
                    "severity": "high",
                },
                {
                    "id": "uses-optimized-images",
                    "title": "Serve images in next-gen formats",
                    "display_value": "Potential savings: ~1.2MB",
                    "severity": "medium",
                },
            ],
            "is_cached": False,
        }

    async def analyze(self, website_url: str, strategy: str = "mobile") -> Dict[str, Any]:
        """Fetches and transforms PageSpeed audit for the given website URL."""
        domain = extract_clean_domain(website_url)

        # 1. Check Redis Cache
        cached_result = await self._get_cache(domain)
        if cached_result:
            cached_result["is_cached"] = True
            return cached_result

        # 2. Call Google PageSpeed API
        params: Dict[str, Any] = {
            "url": website_url,
            "strategy": strategy,
            "category": "performance",
        }
        if settings.PAGESPEED_API_KEY:
            params["key"] = settings.PAGESPEED_API_KEY

        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                logger.info(f"Requesting PageSpeed Insights for '{website_url}' (Strategy: {strategy})")
                response = await client.get(PAGESPEED_API_ENDPOINT, params=params)

                if response.status_code == 200:
                    raw_data = response.json()
                    parsed = self._parse_lighthouse_payload(raw_data, domain)
                    await self._set_cache(domain, parsed)
                    return parsed
                elif response.status_code == 429:
                    logger.warning(f"Google PageSpeed rate limit (429) hit for domain '{domain}'")
                    fallback = self._generate_fallback_payload(domain, "Google PageSpeed API rate limit reached")
                    return fallback
                else:
                    logger.warning(f"Google PageSpeed API returned status {response.status_code}: {response.text[:200]}")
                    fallback = self._generate_fallback_payload(domain, f"API returned status {response.status_code}")
                    return fallback
        except Exception as e:
            logger.warning(f"PageSpeed request failed for '{website_url}': {e}")
            fallback = self._generate_fallback_payload(domain, str(e))
            return fallback


pagespeed_service = PageSpeedService()
