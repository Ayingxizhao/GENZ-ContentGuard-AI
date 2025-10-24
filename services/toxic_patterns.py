"""
Toxic Patterns Service

Organizes toxic keywords into categorized patterns with severity levels
for explainability features. Based on data/seed_keywords.py
"""
import re
from typing import Dict, List, Tuple
from enum import Enum


class Severity(Enum):
    """Severity levels for toxic content"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ToxicCategory(Enum):
    """Toxic content categories"""
    SUICIDE_SELF_HARM = "suicide_self_harm"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    THREATS = "threats"
    BODY_SHAMING = "body_shaming"
    SEXUAL_CONTENT = "sexual_content"
    GENERAL_TOXICITY = "general_toxicity"


# Map categories to severity and explanations
CATEGORY_CONFIG = {
    ToxicCategory.SUICIDE_SELF_HARM: {
        "severity": Severity.HIGH,
        "explanation": "Contains suicide encouragement or self-harm language",
        "keywords": [
            "kys", "kill yourself", "end yourself", "unalive", "unalive yourself",
            "rope", "roping", "rope fuel", "suicide fuel", "sui fuel",
            "hang yourself", "jump off bridge", "yeet yourself"
        ]
    },
    ToxicCategory.HATE_SPEECH: {
        "severity": Severity.HIGH,
        "explanation": "Contains hate speech or discriminatory language",
        "keywords": [
            # Slurs and identity attacks (using representative samples)
            "retard", "retarded", "retards", "tard", "r-word",
            "cracker", "crackers", "coon", "coons",
            "spic", "spics", "wetback", "beaner",
            "chink", "chinks", "gook", "nip", "jap",
            "towelhead", "raghead", "camel jockey",
            "kike", "heeb", "yid",
            "libtard", "feminazi", "femoid", "foid",
            "13/50", "14/88", "1488", "88"
        ]
    },
    ToxicCategory.THREATS: {
        "severity": Severity.HIGH,
        "explanation": "Contains threats or violent language",
        "keywords": [
            "die", "death threats", "threat", "threaten", "threatening",
            "dox", "doxx", "doxxing", "doxed",
            "swat", "swatting", "swatted"
        ]
    },
    ToxicCategory.HARASSMENT: {
        "severity": Severity.MEDIUM,
        "explanation": "Contains harassment or bullying language",
        "keywords": [
            "ugly", "ugly ass", "ugly bitch", "butterface",
            "stupid", "dumb", "dumbass", "dumb bitch", "idiot", "moron",
            "loser", "losing", "pathetic", "worthless", "waste of space",
            "human trash", "embarrassment", "cringe lord",
            "virgin", "incel", "loner", "no friends", "friendless",
            "weirdo", "freak", "creep", "creepy",
            "nobody", "no one cares", "irrelevant", "washed up",
            "ratio", "ratioed", "get ratioed", "ratio + L + bozo",
            "cope", "coping", "cope harder", "seethe", "seething",
            "mald", "malding", "cry more", "triggered", "butthurt", "salty"
        ]
    },
    ToxicCategory.BODY_SHAMING: {
        "severity": Severity.MEDIUM,
        "explanation": "Contains body shaming or appearance-based attacks",
        "keywords": [
            "fat", "fatass", "fat bitch", "obese", "pig", "whale",
            "landwhale", "hamplanet",
            "skinny", "anorexic", "skeleton", "bony",
            "short", "midget", "dwarf",
            "bald", "baldie", "chrome dome",
            "acne", "pizza face", "crater face",
            "ugly", "butterface"
        ]
    },
    ToxicCategory.SEXUAL_CONTENT: {
        "severity": Severity.MEDIUM,
        "explanation": "Contains inappropriate sexual content or harassment",
        "keywords": [
            "fuck", "fucking", "fucked", "fucker",
            "shit", "shitting", "shitty",
            "bitch", "bitches", "bitching",
            "ass", "asshole",
            "dick", "dickhead",
            "pussy",
            "cock",
            "slut", "sluts", "slutty", "whore", "whores",
            "thot", "thots"
        ]
    },
    ToxicCategory.GENERAL_TOXICITY: {
        "severity": Severity.LOW,
        "explanation": "Contains toxic or aggressive language",
        "keywords": [
            "hate", "hating", "hatred",
            "disgusting", "gross", "nasty", "vile",
            "toxic", "toxicity",
            "clown", "clowning", "circus",
            "cringe", "cringey", "cringe fest",
            "yikes", "oof",
            "cancel", "cancelled", "cancelling"
        ]
    }
}


class ToxicPatternMatcher:
    """Matches toxic patterns in text"""
    
    def __init__(self):
        """Initialize pattern matcher with compiled regex patterns"""
        self.patterns: Dict[ToxicCategory, List[Tuple[re.Pattern, str]]] = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each category"""
        for category, config in CATEGORY_CONFIG.items():
            patterns = []
            for keyword in config["keywords"]:
                # Create word boundary pattern for whole word matching
                escaped = re.escape(keyword)
                # For phrases with spaces, match them as-is
                pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
                patterns.append((pattern, keyword))
            self.patterns[category] = patterns
    
    def find_matches(self, text: str) -> List[Dict]:
        """
        Find all toxic pattern matches in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of match dictionaries with position, category, severity
        """
        matches = []
        
        for category, patterns in self.patterns.items():
            config = CATEGORY_CONFIG[category]
            
            for pattern, keyword in patterns:
                for match in pattern.finditer(text):
                    matches.append({
                        "text": match.group(),
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                        "category": category.value,
                        "severity": config["severity"].value,
                        "explanation": config["explanation"]
                    })
        
        # Sort by position
        matches.sort(key=lambda x: x["start_pos"])
        
        # Remove overlapping matches (keep first occurrence)
        filtered_matches = []
        last_end = -1
        for match in matches:
            if match["start_pos"] >= last_end:
                filtered_matches.append(match)
                last_end = match["end_pos"]
        
        return filtered_matches
    
    def get_category_summary(self, matches: List[Dict]) -> Dict[str, int]:
        """
        Get summary of detected categories
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Dictionary with category counts
        """
        summary = {}
        for match in matches:
            category = match["category"]
            summary[category] = summary.get(category, 0) + 1
        return summary


# Global instance
_pattern_matcher = None


def get_pattern_matcher() -> ToxicPatternMatcher:
    """Get or create global pattern matcher instance"""
    global _pattern_matcher
    if _pattern_matcher is None:
        _pattern_matcher = ToxicPatternMatcher()
    return _pattern_matcher
