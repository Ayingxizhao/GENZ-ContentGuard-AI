"""
Advanced Data Processor for GenZ Language Detection

This module provides enhanced data processing capabilities including:
1. Better data cleaning and preprocessing
2. Advanced feature engineering
3. Comprehensive model evaluation
4. Training pipeline for advanced models
"""

import logging
import pickle
import re
from typing import Any, Dict, List, Tuple

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
import numpy as np

from advanced_model import AdvancedModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedGenZDataProcessor:
    """Enhanced data processor with advanced ML capabilities"""
    
    def __init__(self) -> None:
        self.trainer = AdvancedModelTrainer()
        
    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning"""
        if pd.isna(text):
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

    def load_and_clean_data(self) -> pd.DataFrame:
        """Load and clean the Reddit data with enhanced preprocessing"""
        logger.info("Loading Reddit data...")
        
        # URLs for the datasets
        urls = [
            "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts1.csv",
            "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts2.csv",
            "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts3.csv",
            "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts4.csv",
        ]
        
        # Load datasets
        dfs = []
        for i, url in enumerate(urls):
            try:
                df = pd.read_csv(url)
                dfs.append(df)
                logger.info(f"Loaded dataset {i+1}: {len(df)} posts")
            except Exception as e:
                logger.error(f"Failed to load dataset {i+1}: {e}")
                continue
        
        if not dfs:
            raise ValueError("No datasets could be loaded")
        
        # Combine datasets
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total posts loaded: {len(df)}")

        # Clean title and content
        df["clean_title"] = df["title"].apply(self.clean_text)
        df["clean_content"] = df["content"].apply(self.clean_text)

        # Combine title and content for analysis
        df["combined_text"] = df["clean_title"] + " " + df["clean_content"]

        # Remove posts with very short text
        df = df[df["combined_text"].str.len() > 20]
        
        # Remove duplicate posts
        df = df.drop_duplicates(subset=["combined_text"])
        
        logger.info(f"Posts after cleaning: {len(df)}")
        return df

    def create_enhanced_training_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create training data with enhanced malicious keyword detection"""
        logger.info("Creating enhanced training data...")

        # Enhanced malicious keywords/phrases with severity weights
        malicious_patterns = {
            # High severity (weight: 3)
            "suicide_self_harm": [
                "kill yourself", "kys", "unalive", "unalive yourself", "commit suicide",
                "end your life", "off yourself", "delete yourself", "self delete",
                "rope", "hanging", "jump off", "end it all", "not worth living"
            ],
            "hate_speech": [
                "hate", "hate speech", "racist", "racism", "sexist", "sexism",
                "homophobic", "transphobic", "bigot", "bigotry", "discrimination",
                "nazi", "fascist", "extremist", "terrorist", "supremacist",
                "white power", "black lives don't matter", "all lives matter"
            ],
            "violence_threats": [
                "threat", "threaten", "violence", "violent", "beat you", "beat you up",
                "punch you", "fight you", "kill you", "hurt you", "attack you",
                "shoot you", "stab you", "burn you", "torture you", "murder you",
                "destroy you", "crush you", "eliminate you"
            ],
            
            # Medium severity (weight: 2)
            "bullying_harassment": [
                "bully", "bullying", "harass", "harassment", "stalk", "stalking",
                "cyberbully", "cyberbullying", "dox", "doxxing", "doxx",
                "personal info", "private info", "real name", "address", "phone",
                "expose you", "ruin your life", "make you suffer"
            ],
            "body_shaming": [
                "ugly", "fat", "skinny", "disgusting", "gross", "hideous",
                "you look like", "no one will love you", "youre ugly", "pig",
                "whale", "stick", "anorexic", "obese", "deformed"
            ],
            "mental_health_shaming": [
                "crazy", "insane", "mental", "psycho", "retarded", "stupid",
                "idiot", "moron", "dumb", "brain dead", "no brain", "mental case",
                "psychopath", "sociopath", "deranged", "unhinged"
            ],
            
            # Lower severity (weight: 1)
            "genz_slang_harassment": [
                "touch grass", "go outside", "get a life", "no friends", "incel",
                "redpill", "blackpill", "mgtow", "simp", "white knight", "soy boy",
                "beta", "alpha", "chad", "virgin", "loser", "cringe", "cringey",
                "embarrassing", "pathetic", "sad", "noob", "boomer"
            ],
            "online_harassment": [
                "delete your account", "never post again", "stop posting",
                "you shouldnt be here", "go away", "leave", "get lost",
                "nobody likes you", "everyone hates you", "youre alone",
                "uninstall", "quit the internet", "log off"
            ],
            "sexual_harassment": [
                "pedo", "pedophile", "grooming", "exploitation", "revenge porn",
                "nudes", "explicit", "porn", "sexual", "inappropriate",
                "rape", "sexual assault", "molest", "pervert"
            ],
            "scams_fraud": [
                "scam", "fraud", "phishing", "malware", "virus", "hack",
                "steal", "stealing", "cheat", "cheating", "fake", "fake news",
                "con artist", "swindler", "ripoff"
            ],
            "conspiracy_misinfo": [
                "conspiracy", "qanon", "flat earth", "fake news", "hoax",
                "government lies", "media lies", "sheep", "wake up",
                "deep state", "illuminati", "new world order"
            ],
            "trolling_baiting": [
                "troll", "trolling", "rage bait", "bait", "triggered",
                "snowflake", "sensitive", "cant take a joke", "butthurt",
                "salty", "mad", "crybaby"
            ],
        }

        # Enhanced safe keywords/phrases
        safe_patterns = {
            "positive_support": [
                "help", "support", "advice", "question", "discussion", "opinion",
                "thoughts", "feelings", "experience", "story", "share", "vent",
                "positive", "good", "great", "amazing", "wonderful", "awesome",
                "love", "care", "kind", "nice", "friendly", "helpful", "supportive",
                "encourage", "motivate", "inspire", "uplift", "comfort"
            ],
            "entertainment_hobbies": [
                "fun", "funny", "humor", "joke", "meme", "entertainment",
                "music", "movie", "game", "hobby", "interest", "passion",
                "art", "creative", "design", "craft", "drawing", "painting",
                "photography", "writing", "reading", "cooking", "gardening"
            ],
            "learning_growth": [
                "learn", "learning", "study", "education", "knowledge", "skill",
                "improve", "improvement", "growth", "development", "progress",
                "work", "job", "career", "professional", "business", "entrepreneur",
                "success", "achieve", "accomplish", "master", "expert"
            ],
            "relationships_social": [
                "family", "friend", "friendship", "relationship", "dating", "love",
                "community", "social", "connect", "connection", "bond", "trust",
                "marriage", "partner", "spouse", "parent", "child", "sibling"
            ],
            "health_wellness": [
                "health", "fitness", "exercise", "diet", "nutrition", "wellness",
                "mental health", "therapy", "counseling", "self care", "wellbeing",
                "meditation", "mindfulness", "stress relief", "relaxation",
                "yoga", "meditation", "therapy", "counseling", "recovery"
            ],
            "technology_innovation": [
                "technology", "tech", "programming", "coding", "software", "app",
                "innovation", "creative", "invention", "future", "modern", "digital",
                "ai", "artificial intelligence", "machine learning", "data science"
            ],
            "nature_environment": [
                "nature", "environment", "outdoor", "garden", "plant", "animal",
                "sustainability", "eco friendly", "green", "climate", "earth",
                "conservation", "wildlife", "forest", "ocean", "mountain"
            ],
        }

        def classify_text_enhanced(text: str) -> Tuple[str, Dict[str, Any]]:
            """Enhanced classification with detailed analysis"""
            text_lower = text.lower()
            
            # Calculate malicious score with severity weights
            malicious_score = 0
            detected_categories = {}
            
            for category, keywords in malicious_patterns.items():
                found_keywords = []
                category_score = 0
                
                for keyword in keywords:
                    if keyword in text_lower:
                        found_keywords.append(keyword)
                        # Assign severity weights
                        if category in ["suicide_self_harm", "hate_speech", "violence_threats"]:
                            category_score += 3
                        elif category in ["bullying_harassment", "body_shaming", "mental_health_shaming"]:
                            category_score += 2
                        else:
                            category_score += 1
                
                if found_keywords:
                    detected_categories[category] = {
                        "keywords": found_keywords,
                        "score": category_score
                    }
                    malicious_score += category_score
            
            # Calculate safe score
            safe_score = 0
            safe_categories = {}
            
            for category, keywords in safe_patterns.items():
                found_keywords = []
                category_score = 0
                
                for keyword in keywords:
                    if keyword in text_lower:
                        found_keywords.append(keyword)
                        category_score += 1
                
                if found_keywords:
                    safe_categories[category] = {
                        "keywords": found_keywords,
                        "score": category_score
                    }
                    safe_score += category_score
            
            # Enhanced decision logic
            if malicious_score >= 5:  # High malicious score
                label = "malicious"
            elif malicious_score >= 2:  # Medium malicious score
                # Check if safe context outweighs malicious
                if safe_score >= malicious_score * 2:
                    label = "safe"
                else:
                    label = "malicious"
            elif malicious_score == 1:  # Low malicious score
                # Require strong safe context
                if safe_score >= 3:
                    label = "safe"
                else:
                    label = "malicious"
            else:  # No malicious content
                if safe_score >= 1:
                    label = "safe"
                else:
                    label = "safe"  # Default to safe for neutral content
            
            analysis = {
                "malicious_score": malicious_score,
                "safe_score": safe_score,
                "malicious_categories": detected_categories,
                "safe_categories": safe_categories,
                "total_keywords": len(detected_categories) + len(safe_categories)
            }
            
            return label, analysis

        # Apply enhanced classification
        logger.info("Applying enhanced classification...")
        classifications = []
        analyses = []
        
        for text in df["combined_text"]:
            label, analysis = classify_text_enhanced(text)
            classifications.append(label)
            analyses.append(analysis)
        
        df["label"] = classifications
        df["analysis"] = analyses

        # Balance the dataset
        malicious_posts = df[df["label"] == "malicious"]
        safe_posts = df[df["label"] == "safe"]

        logger.info("Before balancing:")
        logger.info(f"  Malicious: {len(malicious_posts)}")
        logger.info(f"  Safe: {len(safe_posts)}")

        # Balance dataset (2:1 ratio safe to malicious for better training)
        if len(malicious_posts) < len(safe_posts):
            safe_posts = safe_posts.sample(n=min(len(malicious_posts) * 2, len(safe_posts)), random_state=42)

        balanced_df = pd.concat([malicious_posts, safe_posts])
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        logger.info("After balancing:")
        logger.info(f"  Malicious: {len(balanced_df[balanced_df['label'] == 'malicious'])}")
        logger.info(f"  Safe: {len(balanced_df[balanced_df['label'] == 'safe'])}")

        return balanced_df

    def evaluate_model_performance(self, y_true: List[str], y_pred: List[str], y_proba: List[float] = None) -> Dict[str, Any]:
        """Comprehensive model evaluation"""
        logger.info("Evaluating model performance...")
        
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, pos_label="malicious")
        recall = recall_score(y_true, y_pred, pos_label="malicious")
        f1 = f1_score(y_true, y_pred, pos_label="malicious")
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=["safe", "malicious"])
        
        # ROC AUC if probabilities available
        auc = None
        if y_proba is not None:
            y_binary = [1 if label == "malicious" else 0 for label in y_true]
            auc = roc_auc_score(y_binary, y_proba)
        
        # Classification report
        report = classification_report(y_true, y_pred, output_dict=True)
        
        results = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
        }
        
        if auc is not None:
            results["roc_auc"] = auc
        
        logger.info(f"Model Performance:")
        logger.info(f"  Accuracy: {accuracy:.3f}")
        logger.info(f"  Precision: {precision:.3f}")
        logger.info(f"  Recall: {recall:.3f}")
        logger.info(f"  F1-Score: {f1:.3f}")
        if auc:
            logger.info(f"  ROC-AUC: {auc:.3f}")
        
        return results

    def train_advanced_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train advanced models with comprehensive evaluation"""
        logger.info("Training advanced models...")
        
        # Prepare data
        enhanced_df, feature_df = self.trainer.prepare_data(df)
        
        # Train ensemble models
        ensemble_results = self.trainer.train_ensemble_models(enhanced_df)
        
        # Evaluate performance
        X_text = enhanced_df["clean_text"]
        y = enhanced_df["label"]
        
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            X_text, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Get predictions for evaluation
        best_model_name = max(ensemble_results["results"].keys(), 
                            key=lambda x: ensemble_results["results"][x]["f1"])
        best_model = ensemble_results["models"][best_model_name]
        
        if best_model_name in ensemble_results["vectorizers"]:
            X_test_vector = ensemble_results["vectorizers"][best_model_name].transform(X_test_text)
            y_pred = best_model.predict(X_test_vector)
            y_proba = best_model.predict_proba(X_test_vector)[:, 1]
        else:
            # Feature-based model
            X_test_features = []
            for text in X_test_text:
                features = self.trainer.detector.extract_linguistic_features(text)
                X_test_features.append(list(features.values()))
            
            X_test_features = np.array(X_test_features)
            if best_model_name in ensemble_results["scalers"]:
                X_test_features = ensemble_results["scalers"][best_model_name].transform(X_test_features)
            
            y_pred = best_model.predict(X_test_features)
            y_proba = best_model.predict_proba(X_test_features)[:, 1]
        
        # Evaluate
        evaluation_results = self.evaluate_model_performance(y_test.tolist(), y_pred.tolist(), y_proba.tolist())
        
        # Save models
        model_data = {
            "models": ensemble_results["models"],
            "vectorizers": ensemble_results["vectorizers"],
            "scalers": ensemble_results["scalers"],
            "evaluation_results": evaluation_results,
            "best_model": best_model_name,
        }
        
        self.trainer.save_models(model_data)
        
        return {
            "model_data": model_data,
            "ensemble_results": ensemble_results["results"],
            "evaluation_results": evaluation_results,
            "best_model": best_model_name,
        }

    def test_model_with_examples(self) -> None:
        """Test the trained model with various examples"""
        logger.info("Testing model with examples...")
        
        test_cases = [
            # Safe examples
            ("I'm feeling really down today and need some advice", "safe"),
            ("This is a great discussion about mental health", "safe"),
            ("What's your favorite movie? I love watching films!", "safe"),
            ("I'm learning to code and it's so much fun!", "safe"),
            ("Can someone help me with my homework?", "safe"),
            
            # Malicious examples
            ("kill yourself you worthless piece of shit", "malicious"),
            ("I hate all [racial slur] people, they should die", "malicious"),
            ("kys and touch grass you absolute loser", "malicious"),
            ("You're so ugly, delete your account", "malicious"),
            ("Go kys and never come back", "malicious"),
            
            # Edge cases
            ("I want to kill this bug in my code", "safe"),
            ("This movie is so bad it makes me want to die", "safe"),
            ("I hate this assignment but I'll finish it", "safe"),
        ]
        
        # Load the advanced detector
        from advanced_model import advanced_detector
        
        if not advanced_detector.model_loaded:
            logger.error("Advanced model not loaded. Please train models first.")
            return
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        
        logger.info("Testing examples:")
        for text, expected in test_cases:
            result = advanced_detector.predict("", text)
            
            if "error" not in result:
                predicted = result["prediction"]
                confidence = result["confidence"]
                is_correct = predicted == expected
                
                if is_correct:
                    correct_predictions += 1
                
                status = "✓" if is_correct else "✗"
                logger.info(f"{status} Text: '{text[:50]}...'")
                logger.info(f"  Expected: {expected}, Predicted: {predicted}, Confidence: {confidence}")
            else:
                logger.error(f"Error predicting: {result['error']}")
        
        accuracy = correct_predictions / total_predictions
        logger.info(f"Test Accuracy: {accuracy:.3f} ({correct_predictions}/{total_predictions})")


def main() -> None:
    """Main training pipeline"""
    processor = AdvancedGenZDataProcessor()
    
    try:
        # Load and clean data
        df = processor.load_and_clean_data()
        
        # Create enhanced training data
        training_df = processor.create_enhanced_training_data(df)
        
        # Train advanced models
        results = processor.train_advanced_models(training_df)
        
        logger.info("Training completed successfully!")
        logger.info(f"Best model: {results['best_model']}")
        logger.info(f"Best F1-score: {results['ensemble_results'][results['best_model']]['f1']:.3f}")
        
        # Test with examples
        processor.test_model_with_examples()
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
