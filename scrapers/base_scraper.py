"""
Base scraper class
Defines interface for all platform-specific scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging


@dataclass
class Comment:
    """Represents a comment with analysis metadata"""
    content: str
    author: str
    depth: int = 0
    comment_id: Optional[str] = None
    parent_id: Optional[str] = None
    score: Optional[int] = None
    created_utc: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Post:
    """Represents a post with metadata"""
    title: str
    content: str
    author: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    created_utc: Optional[float] = None
    num_comments: Optional[int] = None
    subreddit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ScrapedContent:
    """Container for scraped content from a URL"""
    url: str
    platform: str
    post: Post
    comments: List[Comment]
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'platform': self.platform,
            'post': self.post.to_dict(),
            'comments': [c.to_dict() for c in self.comments],
            'metadata': self.metadata or {}
        }


class BaseScraper(ABC):
    """
    Abstract base class for platform scrapers
    All platform-specific scrapers must inherit from this
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape(self, url: str, max_comments: int = 20, max_depth: int = 3) -> ScrapedContent:
        """
        Scrape content from URL

        Args:
            url: The URL to scrape
            max_comments: Maximum number of comments to extract
            max_depth: Maximum depth of nested comments

        Returns:
            ScrapedContent object with post and comments

        Raises:
            ValueError: If URL is invalid or content not found
            Exception: For other scraping errors
        """
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is valid for this scraper

        Args:
            url: The URL to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def _clean_text(self, text: str) -> str:
        """
        Clean text content

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Basic cleanup
        text = text.strip()

        return text

    def _should_include_content(self, content: str, min_length: int = 5, max_length: int = 5000) -> bool:
        """
        Check if content should be included

        Args:
            content: The content to check
            min_length: Minimum content length
            max_length: Maximum content length

        Returns:
            True if content should be included
        """
        if not content:
            return False

        content = self._clean_text(content)
        length = len(content)

        return min_length <= length <= max_length
