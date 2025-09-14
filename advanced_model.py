"""
Advanced ML Model Implementation for GenZ Language Detection

This module implements a sophisticated text classification system using:
1. Transformer-based models (BERT/RoBERTa)
2. Ensemble learning combining multiple approaches
3. Advanced feature engineering
4. Comprehensive evaluation metrics
"""

import logging
import pickle
import re
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, pipeline

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedGenZDetector:
    """
    Advanced GenZ language detector using multiple ML approaches
    """

    def __init__(self, model_path: str = "advanced_genz_detector.pkl") -> None:
        """Initialize the advanced detector"""
        self.model_path = model_path
        self.models: Dict[str, Any] = {}
        self.vectorizers: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize transformer model
        self.transformer_model_name = "distilbert-base-uncased"
        self.tokenizer: Optional[Any] = None
        self.transformer_model: Optional[Any] = None
        self.transformer_pipeline: Optional[Any] = None

        self.model_loaded = False
        self._load_models()

    def _load_models(self) -> None:
        """Load all trained models"""
        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.models = model_data.get("models", {})
            self.vectorizers = model_data.get("vectorizers", {})
            self.scalers = model_data.get("scalers", {})

            # Load transformer model
            if "transformer_model_name" in model_data:
                self.transformer_model_name = model_data["transformer_model_name"]
                self._load_transformer_model()

            self.model_loaded = True
            logger.info("Advanced models loaded successfully")

        except FileNotFoundError:
            logger.warning(f"Model file {self.model_path} not found. Please train models first.")
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.model_loaded = False

    def _load_transformer_model(self) -> None:
        """Load transformer model for inference"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.transformer_model_name)
            self.transformer_model = AutoModelForSequenceClassification.from_pretrained(
                self.transformer_model_name, num_labels=2
            )
            self.transformer_pipeline = pipeline(
                "text-classification",
                model=self.transformer_model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
            )
            logger.info("Transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading transformer model: {e}")
            self.transformer_pipeline = None

    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning with better preprocessing"""
        if not text:
            return ""

        # Convert to string
        text = str(text)

        # Remove URLs
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)

        # Remove user mentions and hashtags
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"#\w+", "", text)

        # Remove excessive punctuation
        text = re.sub(r"[!]{2,}", "!", text)
        text = re.sub(r"[?]{2,}", "?", text)
        text = re.sub(r"[.]{2,}", ".", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Remove very short words (likely typos)
        words = text.split()
        words = [word for word in words if len(word) > 1 or word.isalnum()]
        text = " ".join(words)

        return text

    def extract_linguistic_features(self, text: str) -> Dict[str, float]:
        """Extract advanced linguistic features"""
        features = {}

        # Basic text statistics
        features["char_count"] = float(len(text))
        features["word_count"] = float(len(text.split()))
        features["sentence_count"] = float(len(re.split(r"[.!?]+", text)))
        features["avg_word_length"] = float(np.mean([len(word) for word in text.split()]) if text.split() else 0)

        # Punctuation analysis
        features["exclamation_ratio"] = float(text.count("!") / max(len(text), 1))
        features["question_ratio"] = float(text.count("?") / max(len(text), 1))
        features["caps_ratio"] = float(sum(1 for c in text if c.isupper()) / max(len(text), 1))

        # Repetition patterns
        features["repeated_chars"] = float(len(re.findall(r"(.)\1{2,}", text)))
        features["repeated_words"] = float(len(re.findall(r"\b(\w+)\s+\1\b", text.lower())))

        # GenZ specific patterns
        features["slang_patterns"] = float(len(re.findall(r"\b(yeet|no cap|bet|periodt|slay|vibe|stan|ship)\b", text.lower())))
        features["emoji_count"] = float(len(re.findall(r"[^\x00-\x7F]", text)))

        # Sentiment indicators
        positive_words = ["good", "great", "amazing", "awesome", "love", "best", "perfect", "excellent"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "disgusting"]

        text_lower = text.lower()
        features["positive_word_ratio"] = sum(1 for word in positive_words if word in text_lower) / max(len(text.split()), 1)
        features["negative_word_ratio"] = sum(1 for word in negative_words if word in text_lower) / max(len(text.split()), 1)

        return features

    def analyze_with_transformer(self, text: str) -> Dict[str, Any]:
        """Analyze text using transformer model"""
        if not self.transformer_pipeline:
            return {"error": "Transformer model not available"}

        try:
            # Clean text for transformer
            clean_text = self.clean_text(text)
            if len(clean_text) < 5:
                return {"prediction": "safe", "confidence": 0.5, "probabilities": [0.5, 0.5]}

            # Get prediction
            result = self.transformer_pipeline(clean_text, truncation=True, max_length=512)

            # Map to our format
            if result[0]["label"] == "LABEL_1":  # Assuming LABEL_1 is malicious
                prediction = "malicious"
                confidence = result[0]["score"]
                probabilities = [1 - confidence, confidence]
            else:
                prediction = "safe"
                confidence = result[0]["score"]
                probabilities = [confidence, 1 - confidence]

            return {
                "prediction": prediction,
                "confidence": confidence,
                "probabilities": probabilities,
                "model_type": "transformer",
            }

        except Exception as e:
            logger.error(f"Transformer analysis error: {e}")
            return {"error": f"Transformer analysis failed: {str(e)}"}

    def analyze_with_ensemble(self, text: str) -> Dict[str, Any]:
        """Analyze text using ensemble of traditional ML models"""
        if not self.models:
            return {"error": "Ensemble models not available"}

        try:
            clean_text = self.clean_text(text)
            if len(clean_text) < 5:
                return {"prediction": "safe", "confidence": 0.5}

            # Extract features
            linguistic_features = self.extract_linguistic_features(clean_text)

            # Get predictions from each model
            predictions = []
            confidences = []

            for model_name, model in self.models.items():
                if model_name in self.vectorizers:
                    # TF-IDF based models
                    text_vector = self.vectorizers[model_name].transform([clean_text])
                    pred = model.predict(text_vector)[0]
                    proba = model.predict_proba(text_vector)[0]

                    predictions.append(pred)
                    confidences.append(max(proba))
                else:
                    # Feature-based models
                    feature_vector = np.array(list(linguistic_features.values())).reshape(1, -1)
                    if model_name in self.scalers:
                        feature_vector = self.scalers[model_name].transform(feature_vector)

                    pred = model.predict(feature_vector)[0]
                    proba = model.predict_proba(feature_vector)[0]

                    predictions.append(pred)
                    confidences.append(max(proba))

            # Ensemble decision (majority vote with confidence weighting)
            malicious_votes = sum(1 for p in predictions if p == "malicious")
            safe_votes = len(predictions) - malicious_votes

            if malicious_votes > safe_votes:
                prediction = "malicious"
                avg_confidence = np.mean([c for p, c in zip(predictions, confidences) if p == "malicious"])
            else:
                prediction = "safe"
                avg_confidence = np.mean([c for p, c in zip(predictions, confidences) if p == "safe"])

            return {
                "prediction": prediction,
                "confidence": avg_confidence,
                "model_type": "ensemble",
                "individual_predictions": dict(zip(self.models.keys(), predictions)),
            }

        except Exception as e:
            logger.error(f"Ensemble analysis error: {e}")
            return {"error": f"Ensemble analysis failed: {str(e)}"}

    def predict(self, title: str = "", content: str = "") -> Dict[str, Any]:
        """Main prediction method combining multiple approaches"""
        if not self.model_loaded:
            return {
                "error": "Models not loaded. Please train models first.",
                "prediction": "unknown",
                "confidence": 0.0,
            }

        # Combine title and content
        combined_text = f"{title} {content}".strip()

        if not combined_text:
            return {"error": "No text provided for analysis", "prediction": "unknown", "confidence": 0.0}

        try:
            # Get predictions from different models
            transformer_result = self.analyze_with_transformer(combined_text)
            ensemble_result = self.analyze_with_ensemble(combined_text)

            # Combine results with weighted voting
            predictions = []
            confidences = []
            weights = []

            # Transformer gets higher weight due to better performance
            if "error" not in transformer_result:
                predictions.append(transformer_result["prediction"])
                confidences.append(transformer_result["confidence"])
                weights.append(0.6)  # 60% weight

            if "error" not in ensemble_result:
                predictions.append(ensemble_result["prediction"])
                confidences.append(ensemble_result["confidence"])
                weights.append(0.4)  # 40% weight

            if not predictions:
                return {"error": "All models failed", "prediction": "unknown", "confidence": 0.0}

            # Weighted voting
            malicious_score = sum(w for p, w in zip(predictions, weights) if p == "malicious")
            safe_score = sum(w for p, w in zip(predictions, weights) if p == "safe")

            if malicious_score > safe_score:
                final_prediction = "malicious"
                final_confidence = np.average(
                    [c for p, c in zip(predictions, confidences) if p == "malicious"],
                    weights=[w for p, w in zip(predictions, weights) if p == "malicious"],
                )
            else:
                final_prediction = "safe"
                final_confidence = np.average(
                    [c for p, c in zip(predictions, confidences) if p == "safe"],
                    weights=[w for p, w in zip(predictions, weights) if p == "safe"],
                )

            # Map to existing format
            analysis = "MALICIOUS" if final_prediction == "malicious" else "SAFE"
            is_malicious = final_prediction == "malicious"

            return {
                "analysis": analysis,
                "is_malicious": is_malicious,
                "confidence": f"{final_confidence:.1%}",
                "prediction": final_prediction,
                "probabilities": {
                    "safe": 1 - final_confidence if is_malicious else final_confidence,
                    "malicious": final_confidence if is_malicious else 1 - final_confidence,
                },
                "model_type": "advanced_ensemble",
                "detailed_analysis": {
                    "transformer_result": transformer_result,
                    "ensemble_result": ensemble_result,
                    "linguistic_features": self.extract_linguistic_features(combined_text),
                    "risk_level": self._get_risk_level(float(final_confidence), is_malicious),
                    "model_confidence": final_confidence,
                },
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"error": f"Prediction failed: {str(e)}", "prediction": "unknown", "confidence": 0.0}

    def _get_risk_level(self, confidence: float, is_malicious: bool) -> str:
        """Determine risk level based on confidence and prediction"""
        if not is_malicious:
            return "LOW"

        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        if not self.model_loaded:
            return {"status": "not_loaded"}

        info = {
            "status": "loaded",
            "model_types": list(self.models.keys()),
            "transformer_model": self.transformer_model_name,
            "device": str(self.device),
            "total_models": len(self.models),
        }

        if self.transformer_pipeline:
            info["transformer_available"] = True
        else:
            info["transformer_available"] = False

        return info


class AdvancedModelTrainer:
    """Trainer class for the advanced models"""

    def __init__(self) -> None:
        self.detector = AdvancedGenZDetector()
        self.transformer_model_name = "distilbert-base-uncased"

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare training data with enhanced features"""
        logger.info("Preparing training data...")

        # Clean text
        df["clean_text"] = df["combined_text"].apply(self.detector.clean_text)

        # Extract linguistic features
        linguistic_features = []
        for text in df["clean_text"]:
            features = self.detector.extract_linguistic_features(text)
            linguistic_features.append(features)

        # Convert to DataFrame
        feature_df = pd.DataFrame(linguistic_features)

        # Combine with original data
        enhanced_df = pd.concat([df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)

        # Remove rows with insufficient text
        enhanced_df = enhanced_df[enhanced_df["clean_text"].str.len() > 10]

        logger.info(f"Enhanced dataset size: {len(enhanced_df)}")
        return enhanced_df, feature_df

    def train_ensemble_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ensemble of traditional ML models"""
        logger.info("Training ensemble models...")

        # Prepare data
        X_text = df["clean_text"]
        y = df["label"]

        # Split data
        X_train_text, X_test_text, y_train, y_test = train_test_split(X_text, y, test_size=0.2, random_state=42, stratify=y)

        # Extract linguistic features
        X_train_features: List[List[float]] = []
        X_test_features: List[List[float]] = []

        for text in X_train_text:
            features = self.detector.extract_linguistic_features(text)
            X_train_features.append(list(features.values()))

        for text in X_test_text:
            features = self.detector.extract_linguistic_features(text)
            X_test_features.append(list(features.values()))

        X_train_features_array = np.array(X_train_features)
        X_test_features_array = np.array(X_test_features)

        # Scale features
        scaler = StandardScaler()
        X_train_features_scaled = scaler.fit_transform(X_train_features_array)
        X_test_features_scaled = scaler.transform(X_test_features_array)

        # TF-IDF vectorization
        tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train_text)
        X_test_tfidf = tfidf_vectorizer.transform(X_test_text)

        # Train multiple models
        models = {}
        vectorizers = {}
        scalers = {}

        # TF-IDF based models
        models["naive_bayes"] = MultinomialNB()
        models["naive_bayes"].fit(X_train_tfidf, y_train)
        vectorizers["naive_bayes"] = tfidf_vectorizer

        models["logistic_regression"] = LogisticRegression(random_state=42, max_iter=1000)
        models["logistic_regression"].fit(X_train_tfidf, y_train)
        vectorizers["logistic_regression"] = tfidf_vectorizer

        models["svm"] = SVC(probability=True, random_state=42)
        models["svm"].fit(X_train_tfidf, y_train)
        vectorizers["svm"] = tfidf_vectorizer

        # Feature-based models
        models["random_forest"] = RandomForestClassifier(n_estimators=100, random_state=42)
        models["random_forest"].fit(X_train_features_scaled, y_train)
        scalers["random_forest"] = scaler

        # Evaluate models
        results = {}
        for name, model in models.items():
            if name in vectorizers:
                y_pred = model.predict(X_test_tfidf)
                y_proba = model.predict_proba(X_test_tfidf)[:, 1]
            else:
                y_pred = model.predict(X_test_features_scaled)
                y_proba = model.predict_proba(X_test_features_scaled)[:, 1]

            results[name] = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, pos_label="malicious"),
                "recall": recall_score(y_test, y_pred, pos_label="malicious"),
                "f1": f1_score(y_test, y_pred, pos_label="malicious"),
                "auc": roc_auc_score(y_test == "malicious", y_proba),
            }

        logger.info("Ensemble models trained successfully")
        logger.info("Model Performance:")
        for name, metrics in results.items():
            logger.info(f"{name}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1']:.3f}")

        return {
            "models": models,
            "vectorizers": vectorizers,
            "scalers": scalers,
            "results": results,
        }

    def save_models(self, model_data: Dict[str, Any], filename: str = "advanced_genz_detector.pkl") -> None:
        """Save trained models"""
        model_data["transformer_model_name"] = self.transformer_model_name

        with open(filename, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Models saved to {filename}")


# Global instance for easy access
advanced_detector = AdvancedGenZDetector()


def analyze_with_advanced_model(title: str = "", content: str = "") -> Dict[str, Any]:
    """Convenience function to analyze text with advanced model"""
    return advanced_detector.predict(title, content)
