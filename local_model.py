import pickle
import re
from typing import Any, Dict


class LocalGenZDetector:
    def __init__(self, model_path: str = "genz_detector_model.pkl") -> None:
        """Initialize the local model detector"""
        try:
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)

            self.vectorizer = model_data["vectorizer"]
            self.model = model_data["model"]
            self.model_loaded = True
            print("Local model loaded successfully")

        except FileNotFoundError:
            print(f"Model file {model_path} not found. Please run data_processor.py first.")
            self.model_loaded = False
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False

    def clean_text(self, text: str) -> str:
        """Clean text data"""
        if not text:
            return ""

        # Convert to string
        text = str(text)

        # Remove URLs
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^a-zA-Z0-9\s\.\!\?\,\;\:\-\(\)]", "", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _get_risk_level(self, malicious_score: int) -> str:
        """Determine risk level based on malicious score"""
        if malicious_score >= 5:
            return "HIGH"
        elif malicious_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze text for specific malicious and safe keywords"""
        text_lower = text.lower()

        # Define keyword categories
        keyword_categories = {
            "suicide_self_harm": [
                "kill yourself",
                "kys",
                "unalive",
                "unalive yourself",
                "commit suicide",
                "end your life",
                "off yourself",
                "delete yourself",
                "self delete",
            ],
            "hate_speech": [
                "hate",
                "hate speech",
                "racist",
                "racism",
                "sexist",
                "sexism",
                "homophobic",
                "transphobic",
                "bigot",
                "bigotry",
                "discrimination",
                "nazi",
                "fascist",
                "extremist",
                "terrorist",
                "supremacist",
            ],
            "violence_threats": [
                "threat",
                "threaten",
                "violence",
                "violent",
                "beat you",
                "beat you up",
                "punch you",
                "fight you",
                "kill you",
                "hurt you",
                "attack you",
                "shoot you",
                "stab you",
                "burn you",
                "torture you",
            ],
            "bullying_harassment": [
                "bully",
                "bullying",
                "harass",
                "harassment",
                "stalk",
                "stalking",
                "cyberbully",
                "cyberbullying",
                "dox",
                "doxxing",
                "doxx",
                "personal info",
                "private info",
                "real name",
                "address",
                "phone",
            ],
            "body_shaming": [
                "ugly",
                "fat",
                "skinny",
                "disgusting",
                "gross",
                "hideous",
                "you look like",
                "no one will love you",
                "youre ugly",
            ],
            "mental_health_shaming": [
                "crazy",
                "insane",
                "mental",
                "psycho",
                "retarded",
                "stupid",
                "idiot",
                "moron",
                "dumb",
                "brain dead",
                "no brain",
            ],
            "genz_slang_harassment": [
                "touch grass",
                "go outside",
                "get a life",
                "no friends",
                "incel",
                "redpill",
                "blackpill",
                "mgtow",
                "simp",
                "white knight",
                "soy boy",
                "beta",
                "alpha",
                "chad",
                "virgin",
                "loser",
                "cringe",
                "cringey",
                "embarrassing",
                "pathetic",
                "sad",
            ],
            "online_harassment": [
                "delete your account",
                "never post again",
                "stop posting",
                "you shouldnt be here",
                "go away",
                "leave",
                "get lost",
                "nobody likes you",
                "everyone hates you",
                "youre alone",
            ],
            "sexual_harassment": [
                "pedo",
                "pedophile",
                "grooming",
                "exploitation",
                "revenge porn",
                "nudes",
                "explicit",
                "porn",
                "sexual",
                "inappropriate",
            ],
            "scams_fraud": [
                "scam",
                "fraud",
                "phishing",
                "malware",
                "virus",
                "hack",
                "steal",
                "stealing",
                "cheat",
                "cheating",
                "fake",
                "fake news",
            ],
            "conspiracy_misinfo": [
                "conspiracy",
                "qanon",
                "flat earth",
                "fake news",
                "hoax",
                "government lies",
                "media lies",
                "sheep",
                "wake up",
            ],
            "trolling_baiting": [
                "troll",
                "trolling",
                "rage bait",
                "bait",
                "triggered",
                "snowflake",
                "sensitive",
                "cant take a joke",
            ],
        }

        # Safe keyword categories
        safe_keyword_categories = {
            "positive_support": [
                "help",
                "support",
                "advice",
                "question",
                "discussion",
                "opinion",
                "thoughts",
                "feelings",
                "experience",
                "story",
                "share",
                "vent",
                "positive",
                "good",
                "great",
                "amazing",
                "wonderful",
                "awesome",
                "love",
                "care",
                "kind",
                "nice",
                "friendly",
                "helpful",
                "supportive",
            ],
            "entertainment_hobbies": [
                "fun",
                "funny",
                "humor",
                "joke",
                "meme",
                "entertainment",
                "music",
                "movie",
                "game",
                "hobby",
                "interest",
                "passion",
                "art",
                "creative",
                "design",
                "craft",
                "drawing",
                "painting",
            ],
            "learning_growth": [
                "learn",
                "learning",
                "study",
                "education",
                "knowledge",
                "skill",
                "improve",
                "improvement",
                "growth",
                "development",
                "progress",
                "work",
                "job",
                "career",
                "professional",
                "business",
                "entrepreneur",
            ],
            "relationships_social": [
                "family",
                "friend",
                "friendship",
                "relationship",
                "dating",
                "love",
                "community",
                "social",
                "connect",
                "connection",
                "bond",
                "trust",
            ],
            "health_wellness": [
                "health",
                "fitness",
                "exercise",
                "diet",
                "nutrition",
                "wellness",
                "mental health",
                "therapy",
                "counseling",
                "self care",
                "wellbeing",
                "meditation",
                "mindfulness",
                "stress relief",
                "relaxation",
            ],
        }

        # Analyze malicious keywords
        detected_malicious = {}
        total_malicious_score = 0

        for category, keywords in keyword_categories.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
                    # Add weight based on severity
                    if any(
                        severe in keyword
                        for severe in ["kill yourself", "kys", "unalive", "hate", "racist", "threat", "violence"]
                    ):
                        total_malicious_score += 3
                    else:
                        total_malicious_score += 1

            if found_keywords:
                detected_malicious[category] = found_keywords

        # Analyze safe keywords
        detected_safe = {}
        total_safe_score = 0

        for category, keywords in safe_keyword_categories.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
                    total_safe_score += 1

            if found_keywords:
                detected_safe[category] = found_keywords

        return {
            "malicious_keywords": detected_malicious,
            "safe_keywords": detected_safe,
            "malicious_score": total_malicious_score,
            "safe_score": total_safe_score,
            "total_keywords_found": len(detected_malicious) + len(detected_safe),
        }

    def generate_explanation(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a detailed explanation of the analysis"""
        malicious_keywords = analysis_result.get("malicious_keywords", {})
        safe_keywords = analysis_result.get("safe_keywords", {})
        malicious_score = analysis_result.get("malicious_score", 0)
        safe_score = analysis_result.get("safe_score", 0)

        explanation_parts = []

        if malicious_keywords:
            explanation_parts.append("🚨 **Detected Risk Categories:**")
            for category, keywords in malicious_keywords.items():
                category_name = category.replace("_", " ").title()
                explanation_parts.append(f"• **{category_name}**: Found keywords like '{', '.join(keywords[:3])}'")
                if len(keywords) > 3:
                    explanation_parts.append(f"  (and {len(keywords) - 3} more)")

        if safe_keywords:
            explanation_parts.append("\n✅ **Detected Positive Elements:**")
            for category, keywords in safe_keywords.items():
                category_name = category.replace("_", " ").title()
                explanation_parts.append(f"• **{category_name}**: Found keywords like '{', '.join(keywords[:3])}'")
                if len(keywords) > 3:
                    explanation_parts.append(f"  (and {len(keywords) - 3} more)")

        # Add risk assessment
        if malicious_score > 0:
            if malicious_score >= 5:
                risk_level = "HIGH"
                risk_description = "Multiple severe risk indicators detected"
            elif malicious_score >= 3:
                risk_level = "MEDIUM"
                risk_description = "Several concerning elements found"
            else:
                risk_level = "LOW"
                risk_description = "Some potentially problematic content"

            explanation_parts.append(f"\n⚠️ **Risk Assessment:** {risk_level} - {risk_description}")

        if safe_score > 0:
            explanation_parts.append(f"\n✅ **Positive Indicators:** {safe_score} positive elements detected")

        # Final recommendation
        if malicious_score > safe_score:
            explanation_parts.append(
                "\n🔴 **Recommendation:** This content contains potentially harmful language and should be reviewed carefully."
            )
        elif malicious_score == 0 and safe_score > 0:
            explanation_parts.append("\n🟢 **Recommendation:** This content appears to be positive and supportive.")
        else:
            explanation_parts.append(
                "\n🟡 **Recommendation:** This content has mixed indicators and should be reviewed with context."
            )

        return "\n".join(explanation_parts)

    def predict(self, title: str = "", content: str = "") -> Dict[str, Any]:
        """Predict if text is malicious using local model with detailed analysis"""
        if not self.model_loaded:
            return {
                "error": "Model not loaded. Please run data_processor.py first.",
                "prediction": "unknown",
                "confidence": 0.0,
            }

        # Combine title and content
        combined_text = f"{title} {content}".strip()

        if not combined_text:
            return {"error": "No text provided for analysis", "prediction": "unknown", "confidence": 0.0}

        try:
            # Clean text
            clean_text = self.clean_text(combined_text)

            # Vectorize
            text_vector = self.vectorizer.transform([clean_text])

            # Predict
            prediction = self.model.predict(text_vector)[0]
            probabilities = self.model.predict_proba(text_vector)[0]

            # Get confidence
            confidence = max(probabilities)

            # Analyze keywords for detailed breakdown
            keyword_analysis = self.analyze_keywords(combined_text)

            # Generate explanation
            explanation = self.generate_explanation(keyword_analysis)

            # Map prediction to your existing format
            if prediction == "malicious":
                analysis = "MALICIOUS"
                is_malicious = True
            else:
                analysis = "SAFE"
                is_malicious = False

            return {
                "analysis": analysis,
                "is_malicious": is_malicious,
                "confidence": f"{confidence:.1%}",
                "prediction": prediction,
                "probabilities": {"safe": float(probabilities[0]), "malicious": float(probabilities[1])},
                "model_type": "local_ml",
                "detailed_analysis": {
                    "keyword_analysis": keyword_analysis,
                    "explanation": explanation,
                    "risk_level": self._get_risk_level(keyword_analysis["malicious_score"]),
                    "elements_scanned": keyword_analysis["total_keywords_found"],
                },
            }

        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}", "prediction": "unknown", "confidence": 0.0}

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model_loaded:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "model_type": "MultinomialNB",
            "vectorizer_type": "TfidfVectorizer",
            "features": self.vectorizer.get_feature_names_out().shape[0],
        }


# Global instance for easy access
local_detector = LocalGenZDetector()


def analyze_with_local_model(title: str = "", content: str = "") -> Dict[str, Any]:
    """Convenience function to analyze text with local model"""
    return local_detector.predict(title, content)
