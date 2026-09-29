"""Asynchronous robots.txt parser and policy evaluator with domain-level caching."""
import urllib.parse
import urllib.robotparser
from typing import Dict, Optional
import httpx

from app.core.config import settings
from app.utils.logger import logger


class RobotsParser:
    """Fetches and evaluates robots.txt directives per domain."""

    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    async def fetch_and_parse(self, domain: str) -> urllib.robotparser.RobotFileParser:
        """Fetches robots.txt from domain and parses rules."""
        if domain in self._parsers:
            return self._parsers[domain]

        parser = urllib.robotparser.RobotFileParser()
        robots_url = f"https://{domain}/robots.txt"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                res = await client.get(robots_url, headers={"User-Agent": settings.CRAWLER_USER_AGENT})
                if res.status_code == 200:
                    parser.parse(res.text.splitlines())
                    logger.info(f"Loaded and parsed robots.txt for domain='{domain}'")
                elif res.status_code in (401, 403):
                    # If robots.txt is forbidden, default to disallow all per standard RFC
                    parser.parse(["User-agent: *", "Disallow: /"])
                    logger.warning(f"robots.txt for domain='{domain}' returned {res.status_code}, blocking crawler")
                else:
                    # 404 or others: allowed by default
                    parser.parse(["User-agent: *", "Allow: /"])
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt for domain='{domain}': {e}. Allowing by default.")
            parser.parse(["User-agent: *", "Allow: /"])

        self._parsers[domain] = parser
        return parser

    async def can_fetch(self, url: str, user_agent: Optional[str] = None) -> bool:
        """Determines if the specified URL is allowed to be crawled according to robots.txt."""
        ua = user_agent or settings.CRAWLER_USER_AGENT
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        parser = await self.fetch_and_parse(domain)
        try:
            return parser.can_fetch(ua, url)
        except Exception:
            return True


robots_service = RobotsParser()
