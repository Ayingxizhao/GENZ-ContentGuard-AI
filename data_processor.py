import json
import pickle
import re
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


class GenZDataProcessor:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        self.model = MultinomialNB()

    def clean_text(self, text: str) -> str:
        """Clean text data"""
        if pd.isna(text):
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

    def load_and_clean_data(self) -> pd.DataFrame:
        """Load and clean the Reddit data"""
        print("Loading Reddit data...")
        url1 = "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts1.csv"
        url2 = "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts2.csv"
        url3 = "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts3.csv"
        url4 = "https://huggingface.co/datasets/Ayingxizhao/genz_reddit_posts/resolve/main/genz_reddit_posts4.csv"
        # Load both CSV files
        df1 = pd.read_csv(url1)
        df2 = pd.read_csv(url2)
        df3 = pd.read_csv(url3)
        df4 = pd.read_csv(url4)

        # Combine datasets
        df = pd.concat([df1, df2, df3, df4], ignore_index=True)
        print(f"Total posts loaded: {len(df)}")

        # Clean title and content
        df["clean_title"] = df["title"].apply(self.clean_text)
        df["clean_content"] = df["content"].apply(self.clean_text)

        # Combine title and content for analysis
        df["combined_text"] = df["clean_title"] + " " + df["clean_content"]

        # Remove posts with very short text
        df = df[df["combined_text"].str.len() > 20]

        print(f"Posts after cleaning: {len(df)}")
        return df

    def create_training_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create training data with improved malicious keyword detection"""

        # Enhanced malicious keywords/phrases (GenZ specific + modern online harassment)
        malicious_keywords = [
            # Suicide and self-harm
            "kill yourself",
            "kys",
            "unalive",
            "unalive yourself",
            "commit suicide",
            "end your life",
            "off yourself",
            "delete yourself",
            "self delete",
            # Hate speech and discrimination
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
            # Violence and threats
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
            # Bullying and harassment
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
            # Body shaming and appearance
            "ugly",
            "fat",
            "skinny",
            "disgusting",
            "gross",
            "hideous",
            "you look like",
            "no one will love you",
            "youre ugly",
            # Mental health shaming
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
            # GenZ specific slang and modern harassment
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
            # Online harassment patterns
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
            # Sexual harassment and exploitation
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
            # Scams and fraud
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
            # Conspiracy and misinformation
            "conspiracy",
            "qanon",
            "flat earth",
            "fake news",
            "hoax",
            "government lies",
            "media lies",
            "sheep",
            "wake up",
            # Trolling and baiting
            "troll",
            "trolling",
            "rage bait",
            "bait",
            "triggered",
            "snowflake",
            "sensitive",
            "cant take a joke",
        ]

        # Enhanced safe keywords/phrases
        safe_keywords = [
            # Positive emotions and support
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
            # Entertainment and hobbies
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
            # Learning and growth
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
            # Relationships and social
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
            # Health and wellness
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
            # Travel and adventure
            "travel",
            "vacation",
            "trip",
            "adventure",
            "explore",
            "exploration",
            "journey",
            "experience",
            "culture",
            "different",
            "new place",
            # Technology and innovation
            "technology",
            "tech",
            "programming",
            "coding",
            "software",
            "app",
            "innovation",
            "creative",
            "invention",
            "future",
            "modern",
            "digital",
            # Nature and environment
            "nature",
            "environment",
            "outdoor",
            "garden",
            "plant",
            "animal",
            "sustainability",
            "eco friendly",
            "green",
            "climate",
            "earth",
        ]

        # Improved classification logic
        def classify_text(text: str) -> str:
            text_lower = text.lower()

            # Check for malicious keywords (stronger weight)
            malicious_score = 0
            for keyword in malicious_keywords:
                if keyword in text_lower:
                    malicious_score += 1
                    # Extra weight for severe keywords
                    if any(
                        severe in keyword
                        for severe in ["kill yourself", "kys", "unalive", "hate", "racist", "threat", "violence"]
                    ):
                        malicious_score += 2

            # If multiple malicious keywords found, definitely malicious
            if malicious_score >= 2:
                return "malicious"
            elif malicious_score == 1:
                # Single malicious keyword - check context
                safe_count = sum(1 for keyword in safe_keywords if keyword in text_lower)
                if safe_count >= 3:  # If lots of safe context, might be false positive
                    return "safe"
                else:
                    return "malicious"

            # Check for safe keywords
            safe_count = sum(1 for keyword in safe_keywords if keyword in text_lower)
            if safe_count >= 2:  # If multiple safe keywords, likely safe
                return "safe"

            # Default to safe for ambiguous cases
            return "safe"

        # Apply classification
        df["label"] = df["combined_text"].apply(classify_text)

        # Balance the dataset
        malicious_posts = df[df["label"] == "malicious"]
        safe_posts = df[df["label"] == "safe"]

        print(f"Before balancing:")
        print(f"  Malicious: {len(malicious_posts)}")
        print(f"  Safe: {len(safe_posts)}")

        # Limit safe posts to balance the dataset
        if len(malicious_posts) < len(safe_posts):
            safe_posts = safe_posts.sample(n=len(malicious_posts) * 2, random_state=42)

        balanced_df = pd.concat([malicious_posts, safe_posts])
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        print(f"\nAfter balancing:")
        print(f"  Malicious: {len(balanced_df[balanced_df['label'] == 'malicious'])}")
        print(f"  Safe: {len(balanced_df[balanced_df['label'] == 'safe'])}")

        return balanced_df

    def train_model(self, df: pd.DataFrame) -> float:
        """Train the ML model"""
        print("Training model...")

        # Prepare data
        X = df["combined_text"]
        y = df["label"]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Vectorize text
        X_train_vectors = self.vectorizer.fit_transform(X_train)
        X_test_vectors = self.vectorizer.transform(X_test)

        # Train model
        self.model.fit(X_train_vectors, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_vectors)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Model accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        return float(accuracy)

    def save_model(self, filename: str = "genz_detector_model.pkl") -> None:
        """Save the trained model"""
        model_data = {"vectorizer": self.vectorizer, "model": self.model}

        with open(filename, "wb") as f:
            pickle.dump(model_data, f)

        print(f"Model saved as {filename}")

    def predict_text(self, text: str) -> Dict[str, Any]:
        """Predict if text is malicious"""
        # Clean text
        clean_text = self.clean_text(text)

        # Vectorize
        text_vector = self.vectorizer.transform([clean_text])

        # Predict
        prediction = self.model.predict(text_vector)[0]
        probability = self.model.predict_proba(text_vector)[0]

        return {
            "prediction": prediction,
            "confidence": max(probability),
            "probabilities": {"safe": probability[0], "malicious": probability[1]},
        }


def main() -> None:
    """Main processing pipeline"""
    processor = GenZDataProcessor()

    # Load and clean data
    df = processor.load_and_clean_data()

    # Create training data
    training_df = processor.create_training_data(df)

    # Train model
    accuracy = processor.train_model(training_df)

    # Save model
    processor.save_model()

    # Test with some examples
    test_texts = [
        "I'm feeling really down today and need some advice",
        "kill yourself you worthless piece of shit",
        "This is a great discussion about mental health",
        "I hate all [racial slur] people, they should die",
        "What's your favorite movie? I love watching films!",
        "kys and touch grass you absolute loser",
        "You're so ugly, delete your account",
    ]

    print("\nTesting model with examples:")
    for text in test_texts:
        result = processor.predict_text(text)
        print(f"\nText: {text[:50]}...")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.3f}")


if __name__ == "__main__":
    main()
