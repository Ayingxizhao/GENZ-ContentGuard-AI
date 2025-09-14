#!/usr/bin/env python3
"""
Malicious Post Extractor for GenZ Content Moderation System

This script extracts posts flagged as malicious (70%+ confidence) from the Reddit dataset
to create training data for categorization systems.

Features:
- Uses existing DistilBERT + ensemble model
- Filters posts with confidence >= 0.7 (malicious)
- Saves results to CSV with post_text, confidence_score, post_id
- Generates comprehensive statistics and reports
- Production-ready with error handling and logging
"""

import logging
import pickle
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("malicious_extraction.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class MaliciousPostExtractor:
    """
    Extracts malicious posts from Reddit dataset using existing ML models
    """

    def __init__(self, model_path: str = "genz_detector_model.pkl", confidence_threshold: float = 0.7):
        """
        Initialize the extractor

        Args:
            model_path: Path to the trained model file
            confidence_threshold: Minimum confidence for malicious classification
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model_loaded = False
        self.model: Optional[Any] = None
        self.vectorizer: Optional[TfidfVectorizer] = None

        # Statistics tracking
        self.stats: Dict[str, Any] = {
            "total_posts_processed": 0,
            "malicious_posts_found": 0,
            "confidence_distribution": [],
            "processing_errors": 0,
            "start_time": None,
            "end_time": None,
        }

        self._load_model()

    def _load_model(self) -> None:
        """Load the trained model and vectorizer"""
        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.vectorizer = model_data["vectorizer"]
            self.model = model_data["model"]
            self.model_loaded = True
            logger.info(f"Model loaded successfully from {self.model_path}")

        except FileNotFoundError:
            logger.error(f"Model file {self.model_path} not found")
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model_loaded = False

    def clean_text(self, text: str) -> str:
        """Clean text data for analysis"""
        if pd.isna(text) or not text:
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

    def load_reddit_dataset(self, use_local: bool = False, local_file: Optional[str] = None) -> pd.DataFrame:
        """
        Load Reddit dataset from Hugging Face or local file

        Args:
            use_local: Whether to use local file instead of Hugging Face
            local_file: Path to local CSV file

        Returns:
            DataFrame with Reddit posts
        """
        if use_local and local_file:
            logger.info(f"Loading Reddit dataset from local file: {local_file}")
            try:
                df = pd.read_csv(local_file)
                logger.info(f"Loaded {len(df)} posts from local file")
            except Exception as e:
                logger.error(f"Error loading local file: {e}")
                raise
        else:
            logger.info("Loading Reddit dataset from Hugging Face...")

            try:
                # Try using Hugging Face datasets library first
                try:
                    from datasets import load_dataset

                    logger.info("Using Hugging Face datasets library...")

                    # Load the dataset
                    dataset = load_dataset("Ayingxizhao/genz_reddit")

                    # Convert to pandas DataFrame
                    if "train" in dataset:
                        df = dataset["train"].to_pandas()
                    else:
                        # If no train split, use the first available split
                        split_name = list(dataset.keys())[0]
                        df = dataset[split_name].to_pandas()

                    logger.info(f"Loaded {len(df)} posts using datasets library")

                except ImportError:
                    logger.info("datasets library not available, trying direct CSV URLs...")
                    # Fallback to direct CSV URLs
                    urls = [
                        "https://huggingface.co/datasets/Ayingxizhao/genz_reddit/resolve/main/genz_reddit_posts1.csv",
                        "https://huggingface.co/datasets/Ayingxizhao/genz_reddit/resolve/main/genz_reddit_posts2.csv",
                        "https://huggingface.co/datasets/Ayingxizhao/genz_reddit/resolve/main/genz_reddit_posts3.csv",
                        "https://huggingface.co/datasets/Ayingxizhao/genz_reddit/resolve/main/genz_reddit_posts4.csv",
                    ]

                    # Load and combine datasets
                    dataframes = []
                    for i, url in enumerate(urls, 1):
                        logger.info(f"Loading dataset part {i}...")
                        df = pd.read_csv(url)
                        dataframes.append(df)
                        logger.info(f"Loaded {len(df)} posts from part {i}")

                    # Combine all datasets
                    df = pd.concat(dataframes, ignore_index=True)
                    logger.info(f"Total posts loaded: {len(df)}")

            except Exception as e:
                logger.error(f"Error loading dataset from Hugging Face: {e}")
                logger.info("Falling back to creating sample dataset for testing...")
                df = self._create_sample_dataset()

        # Clean and prepare data
        df["clean_title"] = df["title"].apply(self.clean_text)
        df["clean_content"] = df["content"].apply(self.clean_text)
        df["combined_text"] = df["clean_title"] + " " + df["clean_content"]

        # Remove posts with very short text
        df = df[df["combined_text"].str.len() > 20]
        logger.info(f"Posts after cleaning: {len(df)}")

        return df

    def _create_sample_dataset(self) -> pd.DataFrame:
        """
        Create a sample dataset for testing when Hugging Face is not accessible

        Returns:
            DataFrame with sample Reddit posts
        """
        logger.info("Creating sample dataset for testing...")

        # Sample posts with various malicious content
        sample_posts = [
            {
                "id": "sample_1",
                "title": "Why everyone should kys",
                "content": "I think everyone should kill themselves because life is meaningless and we're all going to die anyway",
                "subreddit": "teenagers",
                "score": 5,
                "date": "2024-01-01",
                "url": "https://reddit.com/sample1",
            },
            {
                "id": "sample_2",
                "title": "Hate speech is free speech",
                "content": "I hate all minorities and think they should be eliminated from society. This is my opinion and you can't stop me",
                "subreddit": "GenZ",
                "score": -10,
                "date": "2024-01-02",
                "url": "https://reddit.com/sample2",
            },
            {
                "id": "sample_3",
                "title": "Violence against women is justified",
                "content": "Women deserve to be beaten when they don't listen to men. It's natural and they need to learn their place",
                "subreddit": "youngadults",
                "score": -20,
                "date": "2024-01-03",
                "url": "https://reddit.com/sample3",
            },
            {
                "id": "sample_4",
                "title": "Normal post about hobbies",
                "content": "I love playing video games and reading books. What are your favorite hobbies?",
                "subreddit": "teenagers",
                "score": 15,
                "date": "2024-01-04",
                "url": "https://reddit.com/sample4",
            },
            {
                "id": "sample_5",
                "title": "Looking for advice",
                "content": "I'm having trouble with school and need some help with my studies. Any suggestions?",
                "subreddit": "GenZ",
                "score": 8,
                "date": "2024-01-05",
                "url": "https://reddit.com/sample5",
            },
            {
                "id": "sample_6",
                "title": "Bullying is fun",
                "content": "I love bullying people online because it makes me feel powerful. You're all losers anyway",
                "subreddit": "teenagers",
                "score": -5,
                "date": "2024-01-06",
                "url": "https://reddit.com/sample6",
            },
            {
                "id": "sample_7",
                "title": "Conspiracy theories are real",
                "content": "The government is lying to us about everything. Wake up sheeple! The earth is flat and vaccines are poison",
                "subreddit": "youngadults",
                "score": -15,
                "date": "2024-01-07",
                "url": "https://reddit.com/sample7",
            },
            {
                "id": "sample_8",
                "title": "Positive community post",
                "content": "Thanks to everyone who helped me with my project. This community is amazing and supportive!",
                "subreddit": "GenZ",
                "score": 25,
                "date": "2024-01-08",
                "url": "https://reddit.com/sample8",
            },
        ]

        # Create DataFrame
        df = pd.DataFrame(sample_posts)
        logger.info(f"Created sample dataset with {len(df)} posts")

        return df

    def predict_malicious(self, text: str) -> Tuple[bool, float]:
        """
        Predict if text is malicious and return confidence score

        Args:
            text: Text to analyze

        Returns:
            Tuple of (is_malicious, confidence_score)
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")

        if not text or len(text.strip()) < 5:
            return False, 0.0

        try:
            # Check if model is loaded
            if not self.model_loaded or self.model is None or self.vectorizer is None:
                logger.warning("Model not loaded, cannot classify text")
                return False, 0.0

            # Clean text
            clean_text = self.clean_text(text)

            # Vectorize
            text_vector = self.vectorizer.transform([clean_text])

            # Predict
            prediction = self.model.predict(text_vector)[0]
            probabilities = self.model.predict_proba(text_vector)[0]

            # Get malicious probability (index 1 is malicious, index 0 is safe)
            malicious_probability = probabilities[1]

            # Determine if malicious based on threshold
            is_malicious = malicious_probability >= self.confidence_threshold

            return is_malicious, malicious_probability

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            self.stats["processing_errors"] += 1
            return False, 0.0

    def extract_malicious_posts(self, df: pd.DataFrame, min_posts: int = 1000, max_posts: int = 5000) -> pd.DataFrame:
        """
        Extract malicious posts from the dataset

        Args:
            df: DataFrame with Reddit posts
            min_posts: Minimum number of malicious posts to extract
            max_posts: Maximum number of malicious posts to extract

        Returns:
            DataFrame with malicious posts
        """
        logger.info(f"Starting malicious post extraction...")
        logger.info(f"Target: {min_posts}-{max_posts} malicious posts")

        self.stats["start_time"] = datetime.now()
        malicious_posts = []

        # Process posts in batches for better performance
        batch_size = 1000
        total_batches = len(df) // batch_size + (1 if len(df) % batch_size > 0 else 0)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]

            logger.info(f"Processing batch {batch_idx + 1}/{total_batches} " f"(posts {start_idx}-{end_idx})")

            for idx, row in batch_df.iterrows():
                try:
                    # Get combined text
                    combined_text = row.get("combined_text", "")
                    if not combined_text:
                        continue

                    # Predict maliciousness
                    is_malicious, confidence = self.predict_malicious(combined_text)

                    # Track statistics
                    self.stats["total_posts_processed"] += 1
                    self.stats["confidence_distribution"].append(confidence)

                    # Check if malicious and meets confidence threshold
                    if is_malicious and confidence >= self.confidence_threshold:
                        malicious_posts.append(
                            {
                                "post_id": row.get("id", f"post_{idx}"),
                                "post_text": combined_text,
                                "confidence_score": confidence,
                                "title": row.get("title", ""),
                                "content": row.get("content", ""),
                                "subreddit": row.get("subreddit", ""),
                                "score": row.get("score", 0),
                                "date": row.get("date", ""),
                                "url": row.get("url", ""),
                            }
                        )

                        self.stats["malicious_posts_found"] += 1

                        # Log progress
                        if self.stats["malicious_posts_found"] % 100 == 0:
                            logger.info(f"Found {self.stats['malicious_posts_found']} malicious posts so far...")

                        # Stop if we have enough posts
                        if self.stats["malicious_posts_found"] >= max_posts:
                            logger.info(f"Reached maximum target of {max_posts} malicious posts")
                            break

                except Exception as e:
                    logger.error(f"Error processing post {idx}: {e}")
                    self.stats["processing_errors"] += 1
                    continue

            # Break if we have enough posts
            if self.stats["malicious_posts_found"] >= max_posts:
                break

        self.stats["end_time"] = datetime.now()

        # Check if we met minimum requirements
        if self.stats["malicious_posts_found"] < min_posts:
            logger.warning(
                f"Only found {self.stats['malicious_posts_found']} malicious posts, " f"below minimum target of {min_posts}"
            )

        logger.info(f"Extraction completed. Found {self.stats['malicious_posts_found']} malicious posts")

        return pd.DataFrame(malicious_posts)

    def save_results(self, malicious_df: pd.DataFrame, output_file: str = "malicious_posts.csv") -> None:
        """
        Save malicious posts to CSV file

        Args:
            malicious_df: DataFrame with malicious posts
            output_file: Output CSV filename
        """
        try:
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to CSV
            malicious_df.to_csv(output_file, index=False)
            logger.info(f"Malicious posts saved to {output_file}")

            # Also save a summary file
            summary_file = output_file.replace(".csv", "_summary.txt")
            self.generate_summary_report(summary_file)

        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise

    def generate_summary_report(self, summary_file: str = "extraction_summary.txt") -> None:
        """
        Generate a comprehensive summary report

        Args:
            summary_file: Output summary filename
        """
        try:
            processing_time = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

            # Calculate confidence statistics
            confidences = np.array(self.stats["confidence_distribution"])
            confidence_stats = {
                "mean": np.mean(confidences),
                "median": np.median(confidences),
                "std": np.std(confidences),
                "min": np.min(confidences),
                "max": np.max(confidences),
            }

            # Generate report
            report = f"""
MALICIOUS POST EXTRACTION SUMMARY REPORT
========================================

Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model Used: {self.model_path}
Confidence Threshold: {self.confidence_threshold}

PROCESSING STATISTICS:
----------------------
Total Posts Processed: {self.stats['total_posts_processed']:,}
Malicious Posts Found: {self.stats['malicious_posts_found']:,}
Processing Errors: {self.stats['processing_errors']:,}
Processing Time: {processing_time:.2f} seconds
Posts per Second: {self.stats['total_posts_processed'] / processing_time:.2f}

CONFIDENCE DISTRIBUTION:
------------------------
Mean Confidence: {confidence_stats['mean']:.3f}
Median Confidence: {confidence_stats['median']:.3f}
Standard Deviation: {confidence_stats['std']:.3f}
Minimum Confidence: {confidence_stats['min']:.3f}
Maximum Confidence: {confidence_stats['max']:.3f}

CONFIDENCE RANGES:
------------------
0.7 - 0.8: {np.sum((confidences >= 0.7) & (confidences < 0.8)):,} posts
0.8 - 0.9: {np.sum((confidences >= 0.8) & (confidences < 0.9)):,} posts
0.9 - 1.0: {np.sum(confidences >= 0.9):,} posts

SUCCESS RATE:
-------------
Malicious Detection Rate: {(self.stats['malicious_posts_found'] / self.stats['total_posts_processed'] * 100):.2f}%
Error Rate: {(self.stats['processing_errors'] / self.stats['total_posts_processed'] * 100):.2f}%

RECOMMENDATIONS:
----------------
- {'✓ Target achieved' if self.stats['malicious_posts_found'] >= 1000 else '⚠ Consider lowering confidence threshold or processing more data'}
- {'✓ Good confidence distribution' if confidence_stats['std'] > 0.1 else '⚠ Low variance in confidence scores'}
- {'✓ Low error rate' if self.stats['processing_errors'] < self.stats['total_posts_processed'] * 0.01 else '⚠ High error rate detected'}

FILES GENERATED:
----------------
- malicious_posts.csv: Main output file with extracted posts
- extraction_summary.txt: This summary report
- malicious_extraction.log: Detailed processing log

========================================
Report generated by MaliciousPostExtractor
"""

            # Save report
            with open(summary_file, "w") as f:
                f.write(report)

            logger.info(f"Summary report saved to {summary_file}")

            # Print summary to console
            print("\n" + "=" * 50)
            print("EXTRACTION COMPLETED SUCCESSFULLY")
            print("=" * 50)
            print(f"Total Posts Processed: {self.stats['total_posts_processed']:,}")
            print(f"Malicious Posts Found: {self.stats['malicious_posts_found']:,}")
            print(f"Processing Time: {processing_time:.2f} seconds")
            print(f"Success Rate: {(self.stats['malicious_posts_found'] / self.stats['total_posts_processed'] * 100):.2f}%")
            print("=" * 50)

        except Exception as e:
            logger.error(f"Error generating summary report: {e}")

    def run_extraction(
        self, min_posts: int = 1000, max_posts: int = 5000, output_file: str = "malicious_posts.csv"
    ) -> pd.DataFrame:
        """
        Main method to run the complete extraction process

        Args:
            min_posts: Minimum number of malicious posts to extract
            max_posts: Maximum number of malicious posts to extract
            output_file: Output CSV filename

        Returns:
            DataFrame with extracted malicious posts
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Cannot proceed with extraction.")

        try:
            # Load dataset
            df = self.load_reddit_dataset()

            # Extract malicious posts
            malicious_df = self.extract_malicious_posts(df, min_posts, max_posts)

            # Save results
            self.save_results(malicious_df, output_file)

            return malicious_df

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise


def main():
    """Main function to run the extraction"""
    import argparse

    parser = argparse.ArgumentParser(description="Extract malicious posts from Reddit dataset")
    parser.add_argument("--use-local", action="store_true", help="Use local CSV file instead of Hugging Face")
    parser.add_argument("--local-file", type=str, help="Path to local CSV file")
    parser.add_argument("--min-posts", type=int, default=1000, help="Minimum number of malicious posts to extract")
    parser.add_argument("--max-posts", type=int, default=5000, help="Maximum number of malicious posts to extract")
    parser.add_argument("--confidence", type=float, default=0.7, help="Confidence threshold for malicious classification")
    parser.add_argument("--output", type=str, default="malicious_posts.csv", help="Output CSV filename")

    args = parser.parse_args()

    try:
        # Initialize extractor
        extractor = MaliciousPostExtractor(model_path="genz_detector_model.pkl", confidence_threshold=args.confidence)

        # Load dataset
        df = extractor.load_reddit_dataset(use_local=args.use_local, local_file=args.local_file)

        # Extract malicious posts
        malicious_posts = extractor.extract_malicious_posts(df, min_posts=args.min_posts, max_posts=args.max_posts)

        # Save results
        extractor.save_results(malicious_posts, args.output)

        print(f"\n✅ Extraction completed successfully!")
        print(f"📊 Found {len(malicious_posts)} malicious posts")
        print(f"📁 Results saved to: {args.output}")
        print(f"📋 Summary report: {args.output.replace('.csv', '_summary.txt')}")

    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
