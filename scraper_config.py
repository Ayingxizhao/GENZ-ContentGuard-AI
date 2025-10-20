"""
Configuration for web scraping service
Extensible settings for comment depth, limits, and platform support
"""


class ScraperConfig:
    """Extensible configuration for content scraping"""

    # Comment extraction limits (extensible)
    MAX_COMMENTS = 5  # Maximum number of comments to extract per URL
    MAX_COMMENT_DEPTH = 3  # Maximum depth of nested comments to traverse

    # Caching configuration (extensible)
    CACHE_TTL_SECONDS = 3600  # 1 hour cache lifetime
    CACHE_MAX_SIZE = 100  # Maximum number of cached URLs

    # Platform support (extensible - add more platforms here)
    SUPPORTED_PLATFORMS = {
        'reddit': {
            'enabled': True,
            'domains': ['reddit.com', 'www.reddit.com', 'old.reddit.com'],
            'scraper_class': 'RedditScraper'
        },
        # Future platforms can be added here
        # 'twitter': {
        #     'enabled': False,
        #     'domains': ['twitter.com', 'x.com'],
        #     'scraper_class': 'TwitterScraper'
        # },
    }

    # Reddit-specific settings
    REDDIT_CONFIG = {
        'user_agent': 'ContentGuard-AI/1.0 (by /u/contentguard)',
        'client_id': None,  # Optional: for authenticated access
        'client_secret': None,  # Optional: for authenticated access
        'read_only': True,
    }

    # Content filtering
    MIN_CONTENT_LENGTH = 5  # Minimum characters for content to be analyzed
    MAX_CONTENT_LENGTH = 5000  # Maximum characters per content item

    # Rate limiting
    REQUEST_DELAY_SECONDS = 1  # Delay between requests to avoid rate limits
    MAX_RETRIES = 3  # Maximum retry attempts for failed requests

    @classmethod
    def get_platform_from_url(cls, url: str) -> str:
        """
        Detect platform from URL

        Args:
            url: The URL to analyze

        Returns:
            Platform name or 'unknown'
        """
        url_lower = url.lower()

        for platform, config in cls.SUPPORTED_PLATFORMS.items():
            if config['enabled']:
                for domain in config['domains']:
                    if domain in url_lower:
                        return platform

        return 'unknown'

    @classmethod
    def is_supported_platform(cls, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return cls.get_platform_from_url(url) != 'unknown'

    @classmethod
    def get_scraper_class(cls, platform: str) -> str:
        """Get scraper class name for a platform"""
        if platform in cls.SUPPORTED_PLATFORMS:
            return cls.SUPPORTED_PLATFORMS[platform]['scraper_class']
        return 'GenericScraper'
