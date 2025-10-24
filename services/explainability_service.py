"""
Explainability Service

Provides explainability features for content analysis by identifying
and highlighting specific toxic phrases with their positions and categories.
"""
import logging
from typing import Dict, List, Any, Optional
from .toxic_patterns import get_pattern_matcher


class ExplainabilityService:
    """Service for generating explainability data for content analysis"""
    
    def __init__(self):
        """Initialize explainability service"""
        self.pattern_matcher = get_pattern_matcher()
        self.logger = logging.getLogger(__name__)
    
    def analyze_text(self, text: str, is_malicious: bool = None) -> Dict[str, Any]:
        """
        Analyze text and generate explainability data
        
        Args:
            text: Text to analyze
            is_malicious: Optional flag indicating if content is malicious
            
        Returns:
            Dictionary with explainability data including highlighted phrases
        """
        if not text or not text.strip():
            return {
                "highlighted_phrases": [],
                "categories_detected": {},
                "total_matches": 0
            }
        
        try:
            # Find all toxic pattern matches
            matches = self.pattern_matcher.find_matches(text)
            
            # Get category summary
            category_summary = self.pattern_matcher.get_category_summary(matches)
            
            # Build explainability response
            result = {
                "highlighted_phrases": matches,
                "categories_detected": category_summary,
                "total_matches": len(matches)
            }
            
            # Add severity breakdown
            severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for match in matches:
                severity = match.get("severity", "LOW")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            result["severity_breakdown"] = severity_counts
            
            # Log analysis
            if matches:
                self.logger.info(
                    f"Explainability analysis: {len(matches)} toxic phrases found "
                    f"across {len(category_summary)} categories"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Explainability analysis failed: {str(e)}")
            return {
                "highlighted_phrases": [],
                "categories_detected": {},
                "total_matches": 0,
                "error": str(e)
            }
    
    def merge_with_model_result(
        self, 
        model_result: Dict[str, Any], 
        explainability_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge explainability data with model prediction result
        
        Args:
            model_result: Original model prediction result
            explainability_data: Explainability analysis data
            
        Returns:
            Combined result with explainability fields
        """
        # Create a copy to avoid modifying original
        merged = model_result.copy()
        
        # Add explainability data
        merged["explainability"] = explainability_data
        
        return merged
    
    def format_for_frontend(self, explainability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format explainability data for frontend consumption
        
        Args:
            explainability_data: Raw explainability data
            
        Returns:
            Frontend-friendly formatted data
        """
        # Already in a good format, but we can add display helpers
        formatted = explainability_data.copy()
        
        # Add display-friendly category names
        category_display_names = {
            "suicide_self_harm": "Suicide & Self-Harm",
            "hate_speech": "Hate Speech",
            "harassment": "Harassment",
            "threats": "Threats",
            "body_shaming": "Body Shaming",
            "sexual_content": "Sexual Content",
            "general_toxicity": "General Toxicity"
        }
        
        # Add display names to highlighted phrases
        for phrase in formatted.get("highlighted_phrases", []):
            category = phrase.get("category")
            phrase["category_display"] = category_display_names.get(category, category)
        
        # Add display names to category summary
        if "categories_detected" in formatted:
            formatted["categories_detected_display"] = {
                category_display_names.get(cat, cat): count
                for cat, count in formatted["categories_detected"].items()
            }
        
        return formatted


# Global instance
_explainability_service = None


def get_explainability_service() -> ExplainabilityService:
    """Get or create global explainability service instance"""
    global _explainability_service
    if _explainability_service is None:
        _explainability_service = ExplainabilityService()
    return _explainability_service


def analyze_with_explainability(
    text: str, 
    is_malicious: bool = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze text with explainability
    
    Args:
        text: Text to analyze
        is_malicious: Optional flag indicating if content is malicious
        
    Returns:
        Explainability data
    """
    service = get_explainability_service()
    return service.analyze_text(text, is_malicious)
