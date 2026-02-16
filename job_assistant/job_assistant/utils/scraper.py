"""Job posting URL scraper using BeautifulSoup."""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from job_assistant.config import settings
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def scrape_job_posting(url: str) -> str:
    """Scrape job posting text from a URL.

    Extracts meaningful text content, stripping navigation, scripts, etc.

    Returns:
        Cleaned text content of the job posting.

    Raises:
        ValueError: If scraping fails or returns no content.
    """
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    try:
        response = requests.get(
            url, headers=headers, timeout=settings.request_timeout
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}") from e

    soup = BeautifulSoup(response.text, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        tag.decompose()

    # Try common job posting containers first
    content = None
    selectors = [
        "article",
        "[class*='job-description']",
        "[class*='job_description']",
        "[class*='jobDescription']",
        "[class*='posting']",
        "[class*='vacancy']",
        "main",
        "[role='main']",
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element and len(element.get_text(strip=True)) > 200:
            content = element.get_text(separator="\n", strip=True)
            break

    # Fall back to body text
    if not content:
        body = soup.find("body")
        if body:
            content = body.get_text(separator="\n", strip=True)

    if not content or len(content) < 100:
        raise ValueError("Could not extract meaningful content from the URL.")

    # Clean up excessive whitespace
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    # Truncate if excessively long (likely scraped too much)
    if len(cleaned) > 15000:
        cleaned = cleaned[:15000] + "\n\n[Content truncated]"

    logger.info(f"Scraped {len(cleaned)} characters from {url}")
    return cleaned
