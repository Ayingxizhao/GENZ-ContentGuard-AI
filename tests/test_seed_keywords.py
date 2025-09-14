"""
Tests for the seed keywords module.
"""

import pytest

from data.seed_keywords import (
    get_all_keywords,
    get_category_metadata,
    get_keyword_count_by_category,
    get_keywords_by_category,
    seed_categories,
)


class TestSeedKeywords:
    """Test cases for seed keywords functionality."""

    def test_seed_categories_structure(self) -> None:
        """Test that seed_categories has the expected structure."""
        assert isinstance(seed_categories, dict)
        assert len(seed_categories) == 4

        expected_categories = ["Hate/Discrimination", "Harassment/Bullying", "Sexual Content", "General Toxicity"]

        for category in expected_categories:
            assert category in seed_categories
            assert isinstance(seed_categories[category], list)
            assert len(seed_categories[category]) > 0

    def test_keyword_counts(self) -> None:
        """Test that each category has sufficient keywords."""
        counts = get_keyword_count_by_category()

        # Each category should have at least 50 keywords
        for category, count in counts.items():
            assert count >= 50, f"{category} has only {count} keywords, expected at least 50"

        # Total should be reasonable
        total = sum(counts.values())
        assert total > 900, f"Total keywords {total} is too low"

    def test_get_keywords_by_category(self) -> None:
        """Test retrieving keywords by category."""
        # Test valid category
        hate_keywords = get_keywords_by_category("Hate/Discrimination")
        assert isinstance(hate_keywords, list)
        assert len(hate_keywords) > 0

        # Test invalid category
        with pytest.raises(KeyError):
            get_keywords_by_category("Invalid Category")

    def test_get_all_keywords(self) -> None:
        """Test retrieving all keywords."""
        all_keywords = get_all_keywords()
        assert isinstance(all_keywords, dict)
        assert len(all_keywords) == 4
        assert all_keywords == seed_categories

    def test_get_category_metadata(self) -> None:
        """Test retrieving category metadata."""
        # Test valid category
        metadata = get_category_metadata("Hate/Discrimination")
        assert isinstance(metadata, dict)
        assert "description" in metadata
        assert "patterns" in metadata
        assert isinstance(metadata["description"], str)
        assert isinstance(metadata["patterns"], list)

        # Test invalid category
        with pytest.raises(KeyError):
            get_category_metadata("Invalid Category")

    def test_keyword_format(self) -> None:
        """Test that keywords are properly formatted."""
        for category, keywords in seed_categories.items():
            for keyword in keywords:
                assert isinstance(keyword, str)
                assert len(keyword) > 0
                # Keywords should not have leading/trailing whitespace
                assert keyword == keyword.strip()

    def test_no_duplicate_keywords_within_category(self) -> None:
        """Test that there are no duplicate keywords within each category."""
        for category, keywords in seed_categories.items():
            unique_keywords = set(keywords)
            assert len(unique_keywords) == len(keywords), f"Duplicates found in {category}"

    def test_keyword_content_samples(self) -> None:
        """Test that categories contain expected sample keywords."""
        # Test Hate/Discrimination category
        hate_keywords = seed_categories["Hate/Discrimination"]
        expected_samples = ["karen", "boomer", "incel", "simp"]
        for sample in expected_samples:
            assert sample in hate_keywords, f"Expected keyword '{sample}' not found in Hate/Discrimination"

        # Test Harassment/Bullying category
        harassment_keywords = seed_categories["Harassment/Bullying"]
        expected_samples = ["kys", "ratio", "cope", "seethe"]
        for sample in expected_samples:
            assert sample in harassment_keywords, f"Expected keyword '{sample}' not found in Harassment/Bullying"

        # Test Sexual Content category
        sexual_keywords = seed_categories["Sexual Content"]
        expected_samples = ["rizz", "pulling", "sliding", "dm"]
        for sample in expected_samples:
            assert sample in sexual_keywords, f"Expected keyword '{sample}' not found in Sexual Content"

        # Test General Toxicity category
        toxicity_keywords = seed_categories["General Toxicity"]
        expected_samples = ["cringe", "mald", "yikes", "oof"]
        for sample in expected_samples:
            assert sample in toxicity_keywords, f"Expected keyword '{sample}' not found in General Toxicity"
