"""
Scraper registry and factory
Manages different platform scrapers
"""

from typing import Optional
from scraper_config import ScraperConfig


def get_scraper(url: str):
    """
    Factory function to get appropriate scraper for URL

    Args:
        url: The URL to scrape

    Returns:
        Scraper instance for the platform

    Raises:
        ValueError: If platform is not supported
    """
    platform = ScraperConfig.get_platform_from_url(url)

    if platform == 'reddit':
        from .reddit_scraper import RedditScraper
        return RedditScraper()
    elif platform == 'unknown':
        from .generic_scraper import GenericScraper
        return GenericScraper()
    else:
        # Future platforms
        raise ValueError(f"Platform '{platform}' is recognized but scraper not implemented yet")


__all__ = ['get_scraper']
