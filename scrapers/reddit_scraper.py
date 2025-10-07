"""
Reddit scraper using PRAW (Python Reddit API Wrapper)
Extracts posts and comments from Reddit URLs
"""

import re
from typing import List
import praw
from praw.exceptions import PRAWException
from scraper_config import ScraperConfig
from .base_scraper import BaseScraper, ScrapedContent, Post, Comment


class RedditScraper(BaseScraper):
    """Scraper for Reddit using PRAW API"""

    def __init__(self):
        super().__init__()
        # Initialize PRAW with read-only mode
        # Use environment variables or dummy credentials for read-only access
        import os
        client_id = os.getenv('REDDIT_CLIENT_ID') or ScraperConfig.REDDIT_CONFIG.get('client_id') or 'dummy_client_id'
        client_secret = os.getenv('REDDIT_CLIENT_SECRET') or ScraperConfig.REDDIT_CONFIG.get('client_secret') or 'dummy_secret'

        self.reddit = praw.Reddit(
            user_agent=ScraperConfig.REDDIT_CONFIG['user_agent'],
            client_id=client_id,
            client_secret=client_secret,
            check_for_async=False
        )
        self.reddit.read_only = True

    def validate_url(self, url: str) -> bool:
        """
        Validate Reddit URL format

        Args:
            url: URL to validate

        Returns:
            True if valid Reddit post URL
        """
        # Match Reddit post URLs
        pattern = r'https?://(www\.|old\.)?reddit\.com/r/\w+/comments/\w+/?.*'
        return bool(re.match(pattern, url))

    def _extract_submission_id(self, url: str) -> str:
        """
        Extract submission ID from Reddit URL

        Args:
            url: Reddit URL

        Returns:
            Submission ID

        Raises:
            ValueError: If URL format is invalid
        """
        # Pattern: /r/subreddit/comments/{id}/...
        match = re.search(r'/comments/(\w+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract submission ID from URL: {url}")

    def _flatten_comment_tree(
        self,
        comment_forest,
        max_comments: int,
        max_depth: int,
        current_depth: int = 0
    ) -> List[Comment]:
        """
        Flatten Reddit comment tree to list with depth tracking

        Args:
            comment_forest: PRAW CommentForest or list of comments
            max_comments: Maximum number of comments to extract
            max_depth: Maximum depth to traverse
            current_depth: Current depth level

        Returns:
            List of Comment objects
        """
        comments = []

        # Check if we've reached limits
        if len(comments) >= max_comments or current_depth > max_depth:
            return comments

        try:
            # Replace "MoreComments" objects to load nested comments
            # Limit the replacement to avoid excessive API calls
            if hasattr(comment_forest, 'replace_more'):
                comment_forest.replace_more(limit=0)  # Don't expand "load more" links

            # Iterate through comments at this level
            for item in comment_forest:
                # Skip if we've hit the comment limit
                if len(comments) >= max_comments:
                    break

                # Skip deleted/removed comments
                if not hasattr(item, 'body') or item.body in ['[deleted]', '[removed]']:
                    continue

                # Extract comment data
                content = self._clean_text(item.body)

                # Check if content is valid
                if not self._should_include_content(
                    content,
                    min_length=ScraperConfig.MIN_CONTENT_LENGTH,
                    max_length=ScraperConfig.MAX_CONTENT_LENGTH
                ):
                    continue

                # Create Comment object
                comment_obj = Comment(
                    content=content,
                    author=str(item.author) if item.author else '[deleted]',
                    depth=current_depth,
                    comment_id=item.id,
                    parent_id=item.parent_id,
                    score=item.score,
                    created_utc=item.created_utc
                )
                comments.append(comment_obj)

                # Recursively process replies if within depth limit
                if current_depth < max_depth and hasattr(item, 'replies') and item.replies:
                    remaining_slots = max_comments - len(comments)
                    if remaining_slots > 0:
                        nested_comments = self._flatten_comment_tree(
                            item.replies,
                            max_comments=remaining_slots,
                            max_depth=max_depth,
                            current_depth=current_depth + 1
                        )
                        comments.extend(nested_comments)

        except Exception as e:
            self.logger.warning(f"Error flattening comment tree: {str(e)}")

        return comments

    def scrape(
        self,
        url: str,
        max_comments: int = ScraperConfig.MAX_COMMENTS,
        max_depth: int = ScraperConfig.MAX_COMMENT_DEPTH
    ) -> ScrapedContent:
        """
        Scrape Reddit post and comments

        Args:
            url: Reddit post URL
            max_comments: Maximum number of comments to extract
            max_depth: Maximum comment depth to traverse

        Returns:
            ScrapedContent with post and comments

        Raises:
            ValueError: If URL is invalid or post not found
            Exception: For other scraping errors
        """
        # Validate URL
        if not self.validate_url(url):
            raise ValueError(f"Invalid Reddit URL format: {url}")

        try:
            # Extract submission ID and get submission
            submission_id = self._extract_submission_id(url)
            submission = self.reddit.submission(id=submission_id)

            # Force fetch submission data
            _ = submission.title  # This triggers the fetch

            # Extract post data
            post_title = self._clean_text(submission.title)
            post_content = self._clean_text(submission.selftext) if submission.selftext else ""

            # Handle link posts (no selftext)
            if not post_content and submission.is_self is False:
                post_content = f"[Link post: {submission.url}]"

            post = Post(
                title=post_title,
                content=post_content,
                author=str(submission.author) if submission.author else '[deleted]',
                post_id=submission.id,
                url=submission.url,
                score=submission.score,
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                subreddit=str(submission.subreddit)
            )

            # Extract comments
            self.logger.info(f"Extracting up to {max_comments} comments with max depth {max_depth}")
            comments = self._flatten_comment_tree(
                submission.comments,
                max_comments=max_comments,
                max_depth=max_depth,
                current_depth=0
            )

            self.logger.info(f"Extracted {len(comments)} comments from {submission.num_comments} total")

            # Create ScrapedContent
            scraped_content = ScrapedContent(
                url=url,
                platform='reddit',
                post=post,
                comments=comments,
                metadata={
                    'total_comments': submission.num_comments,
                    'extracted_comments': len(comments),
                    'comments_truncated': len(comments) >= max_comments,
                    'subreddit': str(submission.subreddit),
                    'post_score': submission.score
                }
            )

            return scraped_content

        except PRAWException as e:
            self.logger.error(f"PRAW error scraping {url}: {str(e)}")
            raise ValueError(f"Failed to fetch Reddit post: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise Exception(f"Scraping error: {str(e)}")
