"""
Generic scraper for unsupported platforms
Placeholder for future platform implementations
"""

from .base_scraper import BaseScraper, ScrapedContent, Post, Comment


class GenericScraper(BaseScraper):
    """
    Generic scraper for platforms not yet supported
    Returns helpful error message
    """

    def validate_url(self, url: str) -> bool:
        """
        Generic URL validation (basic check)

        Args:
            url: URL to validate

        Returns:
            True if URL is valid format
        """
        return url.startswith('http://') or url.startswith('https://')

    def scrape(self, url: str, max_comments: int = 20, max_depth: int = 3) -> ScrapedContent:
        """
        Not implemented - returns error

        Args:
            url: The URL to scrape
            max_comments: Maximum comments (unused)
            max_depth: Maximum depth (unused)

        Raises:
            NotImplementedError: Always raises as this is a placeholder
        """
        raise NotImplementedError(
            "This platform is not yet supported. "
            "Currently supported platforms: Reddit. "
            "More platforms coming soon!"
        )
