"""
Custom Topic Modeling with DistilBERT Integration

This module provides topic modeling capabilities using DistilBERT embeddings
without the BERTopic dependency issues. It implements similar functionality
using scikit-learn clustering algorithms.
"""

import logging
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan
from umap import UMAP

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomTopicAnalyzer:
    """
    Custom topic analyzer using DistilBERT embeddings and clustering
    """

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        n_topics: int = 4,
        min_topic_size: int = 10,
        model_save_path: str = "custom_topic_model.pkl",
        embeddings_save_path: str = "embeddings_cache.pkl"
    ) -> None:
        """
        Initialize custom topic analyzer
        
        Args:
            model_name: DistilBERT model name for embeddings
            n_topics: Target number of topics
            min_topic_size: Minimum size for a topic cluster
            model_save_path: Path to save trained model
            embeddings_save_path: Path to cache embeddings
        """
        self.model_name = model_name
        self.n_topics = n_topics
        self.min_topic_size = min_topic_size
        self.model_save_path = model_save_path
        self.embeddings_save_path = embeddings_save_path
        
        # Initialize components
        self.sentence_model: Optional[SentenceTransformer] = None
        self.clusterer: Optional[Any] = None
        self.umap_model: Optional[UMAP] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        
        # Model state
        self.is_trained = False
        self.topic_keywords: Dict[int, List[Tuple[str, float]]] = {}
        self.topic_info: Optional[pd.DataFrame] = None
        
        # Load models
        self._load_models()
        
    def _load_models(self) -> None:
        """Load DistilBERT model"""
        try:
            logger.info(f"Loading DistilBERT model: {self.model_name}")
            self.sentence_model = SentenceTransformer(self.model_name)
            logger.info("DistilBERT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def _load_embeddings_cache(self) -> Dict[str, np.ndarray]:
        """Load cached embeddings if available"""
        try:
            if Path(self.embeddings_save_path).exists():
                with open(self.embeddings_save_path, "rb") as f:
                    cache = pickle.load(f)
                logger.info(f"Loaded embeddings cache with {len(cache)} entries")
                return cache
        except Exception as e:
            logger.warning(f"Could not load embeddings cache: {e}")
        return {}
    
    def _save_embeddings_cache(self, cache: Dict[str, np.ndarray]) -> None:
        """Save embeddings cache"""
        try:
            with open(self.embeddings_save_path, "wb") as f:
                pickle.dump(cache, f)
            logger.info(f"Saved embeddings cache with {len(cache)} entries")
        except Exception as e:
            logger.warning(f"Could not save embeddings cache: {e}")
    
    def load_malicious_posts(self, csv_path: str) -> pd.DataFrame:
        """
        Load malicious posts from CSV file
        
        Args:
            csv_path: Path to the malicious posts CSV file
            
        Returns:
            DataFrame with malicious posts data
        """
        try:
            logger.info(f"Loading malicious posts from {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Validate required columns
            required_columns = ['post_text', 'title', 'content']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Combine title and content for analysis
            df['combined_text'] = df['title'].fillna('') + ' ' + df['content'].fillna('')
            df['combined_text'] = df['combined_text'].str.strip()
            
            # Filter out empty texts
            df = df[df['combined_text'].str.len() > 10]
            
            logger.info(f"Loaded {len(df)} malicious posts")
            return df
            
        except Exception as e:
            logger.error(f"Error loading malicious posts: {e}")
            raise
    
    def generate_embeddings(
        self, 
        texts: List[str], 
        use_cache: bool = True,
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate DistilBERT embeddings for texts
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            batch_size: Batch size for embedding generation
            
        Returns:
            Array of embeddings
        """
        try:
            if not self.sentence_model:
                raise ValueError("Sentence model not loaded")
            
            # Load cache if requested
            if use_cache:
                self.embeddings_cache = self._load_embeddings_cache()
            
            embeddings = []
            texts_to_embed = []
            text_indices = []
            
            # Check cache for each text
            for i, text in enumerate(texts):
                text_hash = str(hash(text))
                if use_cache and text_hash in self.embeddings_cache:
                    embeddings.append(self.embeddings_cache[text_hash])
                else:
                    texts_to_embed.append(text)
                    text_indices.append(i)
                    embeddings.append(None)  # Placeholder
            
            # Generate embeddings for uncached texts
            if texts_to_embed:
                logger.info(f"Generating embeddings for {len(texts_to_embed)} texts")
                new_embeddings = self.sentence_model.encode(
                    texts_to_embed,
                    batch_size=batch_size,
                    show_progress_bar=True,
                    convert_to_numpy=True
                )
                
                # Update embeddings and cache
                for i, embedding in enumerate(new_embeddings):
                    text_idx = text_indices[i]
                    text_hash = str(hash(texts_to_embed[i]))
                    embeddings[text_idx] = embedding
                    
                    if use_cache:
                        self.embeddings_cache[text_hash] = embedding
            
            # Save updated cache
            if use_cache and texts_to_embed:
                self._save_embeddings_cache(self.embeddings_cache)
            
            embeddings_array = np.array(embeddings)
            logger.info(f"Generated embeddings shape: {embeddings_array.shape}")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def create_clustering_model(self, embeddings: np.ndarray) -> Any:
        """
        Create clustering model based on embeddings
        
        Args:
            embeddings: Pre-computed embeddings
            
        Returns:
            Configured clustering model
        """
        try:
            logger.info("Creating clustering model")
            
            # Reduce dimensionality with UMAP
            self.umap_model = UMAP(
                n_neighbors=15,
                n_components=min(5, embeddings.shape[1] - 1),
                min_dist=0.0,
                metric='cosine',
                random_state=42
            )
            
            reduced_embeddings = self.umap_model.fit_transform(embeddings)
            
            # Use HDBSCAN for clustering
            self.clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_topic_size,
                min_samples=5,
                metric='euclidean',
                cluster_selection_method='eom'
            )
            
            logger.info("Clustering model created successfully")
            return self.clusterer
            
        except Exception as e:
            logger.error(f"Error creating clustering model: {e}")
            raise
    
    def extract_topic_keywords(
        self, 
        texts: List[str], 
        topics: np.ndarray,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[str, float]]]:
        """
        Extract keywords for each topic using TF-IDF
        
        Args:
            texts: List of texts
            topics: Topic assignments
            top_k: Number of top keywords per topic
            
        Returns:
            Dictionary mapping topic_id to list of (keyword, score) tuples
        """
        try:
            logger.info("Extracting topic keywords")
            
            topic_keywords = {}
            unique_topics = np.unique(topics)
            
            # Remove outlier topic (-1) if present
            unique_topics = unique_topics[unique_topics != -1]
            
            for topic_id in unique_topics:
                # Get texts for this topic
                topic_texts = [texts[i] for i in range(len(texts)) if topics[i] == topic_id]
                
                if len(topic_texts) < 2:
                    continue
                
                # Create TF-IDF vectorizer for this topic
                vectorizer = TfidfVectorizer(
                    max_features=100,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                try:
                    tfidf_matrix = vectorizer.fit_transform(topic_texts)
                    feature_names = vectorizer.get_feature_names_out()
                    
                    # Get mean TF-IDF scores
                    mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
                    
                    # Sort by score
                    keyword_scores = list(zip(feature_names, mean_scores))
                    keyword_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    topic_keywords[topic_id] = keyword_scores[:top_k]
                    
                except Exception as e:
                    logger.warning(f"Could not extract keywords for topic {topic_id}: {e}")
                    topic_keywords[topic_id] = []
            
            logger.info(f"Extracted keywords for {len(topic_keywords)} topics")
            return topic_keywords
            
        except Exception as e:
            logger.error(f"Error extracting topic keywords: {e}")
            return {}
    
    def train_topic_model(
        self, 
        texts: List[str], 
        embeddings: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Train topic model on malicious posts
        
        Args:
            texts: List of texts to analyze
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            Training results and model information
        """
        try:
            logger.info("Starting topic model training")
            
            # Generate embeddings if not provided
            if embeddings is None:
                embeddings = self.generate_embeddings(texts)
            
            # Create clustering model
            self.create_clustering_model(embeddings)
            
            # Reduce dimensionality
            reduced_embeddings = self.umap_model.fit_transform(embeddings)
            
            # Fit clustering
            logger.info("Fitting clustering model...")
            topics = self.clusterer.fit_predict(reduced_embeddings)
            
            # Extract topic keywords
            self.topic_keywords = self.extract_topic_keywords(texts, topics)
            
            # Create topic info DataFrame
            unique_topics = np.unique(topics)
            unique_topics = unique_topics[unique_topics != -1]  # Remove outliers
            
            topic_info_data = []
            for topic_id in unique_topics:
                topic_texts = [texts[i] for i in range(len(texts)) if topics[i] == topic_id]
                keywords = self.topic_keywords.get(topic_id, [])
                
                topic_info_data.append({
                    'Topic': topic_id,
                    'Count': len(topic_texts),
                    'Name': f"Topic_{topic_id}",
                    'Top_Keywords': ', '.join([kw[0] for kw in keywords[:5]])
                })
            
            self.topic_info = pd.DataFrame(topic_info_data)
            
            # Calculate statistics
            n_topics_found = len(unique_topics)
            avg_topic_size = len(texts) / max(n_topics_found, 1)
            
            results = {
                "topics": topics,
                "topic_info": self.topic_info,
                "topic_keywords": self.topic_keywords,
                "n_topics_found": n_topics_found,
                "avg_topic_size": avg_topic_size,
                "embeddings_shape": embeddings.shape,
                "reduced_embeddings_shape": reduced_embeddings.shape
            }
            
            self.is_trained = True
            
            logger.info(f"Training completed. Found {n_topics_found} topics")
            logger.info(f"Average topic size: {avg_topic_size:.1f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error training topic model: {e}")
            raise
    
    def predict_topics(self, texts: List[str]) -> Dict[str, Any]:
        """
        Predict topics for new texts
        
        Args:
            texts: List of texts to predict topics for
            
        Returns:
            Prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            logger.info(f"Predicting topics for {len(texts)} texts")
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Reduce dimensionality
            reduced_embeddings = self.umap_model.transform(embeddings)
            
            # Predict topics
            topics = self.clusterer.fit_predict(reduced_embeddings)
            
            results = {
                "topics": topics,
                "embeddings_shape": embeddings.shape,
                "reduced_embeddings_shape": reduced_embeddings.shape
            }
            
            logger.info("Topic prediction completed")
            return results
            
        except Exception as e:
            logger.error(f"Error predicting topics: {e}")
            raise
    
    def get_topic_keywords(self, topic_id: int, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Get keywords for a specific topic
        
        Args:
            topic_id: Topic ID
            top_k: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        return self.topic_keywords.get(topic_id, [])[:top_k]
    
    def save_model(self, filepath: Optional[str] = None) -> None:
        """Save trained model"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        save_path = filepath or self.model_save_path
        try:
            model_data = {
                'clusterer': self.clusterer,
                'umap_model': self.umap_model,
                'topic_keywords': self.topic_keywords,
                'topic_info': self.topic_info,
                'model_name': self.model_name,
                'n_topics': self.n_topics,
                'min_topic_size': self.min_topic_size,
                'is_trained': self.is_trained
            }
            
            with open(save_path, "wb") as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load_model(self, filepath: Optional[str] = None) -> None:
        """Load pre-trained model"""
        load_path = filepath or self.model_save_path
        try:
            with open(load_path, "rb") as f:
                model_data = pickle.load(f)
            
            self.clusterer = model_data['clusterer']
            self.umap_model = model_data['umap_model']
            self.topic_keywords = model_data['topic_keywords']
            self.topic_info = model_data['topic_info']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {load_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model state"""
        info = {
            "sentence_model": self.model_name,
            "n_topics_target": self.n_topics,
            "min_topic_size": self.min_topic_size,
            "sentence_model_loaded": self.sentence_model is not None,
            "clusterer_loaded": self.clusterer is not None,
            "umap_model_loaded": self.umap_model is not None,
            "is_trained": self.is_trained,
            "embeddings_cache_size": len(self.embeddings_cache)
        }
        
        if self.is_trained and self.topic_info is not None:
            info.update({
                "n_topics_found": len(self.topic_info),
                "model_save_path": self.model_save_path
            })
        
        return info


def analyze_malicious_posts_topics(
    csv_path: str,
    n_topics: int = 4,
    min_topic_size: int = 10,
    save_model: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to analyze malicious posts and extract topics
    
    Args:
        csv_path: Path to malicious posts CSV
        n_topics: Target number of topics
        min_topic_size: Minimum topic size
        save_model: Whether to save the trained model
        
    Returns:
        Analysis results
    """
    try:
        # Initialize analyzer
        analyzer = CustomTopicAnalyzer(
            n_topics=n_topics,
            min_topic_size=min_topic_size
        )
        
        # Load data
        df = analyzer.load_malicious_posts(csv_path)
        
        # Train model
        results = analyzer.train_topic_model(df['combined_text'].tolist())
        
        # Save model if requested
        if save_model:
            analyzer.save_model()
        
        # Add additional analysis
        results['data_info'] = {
            'total_posts': len(df),
            'columns': list(df.columns),
            'sample_texts': df['combined_text'].head(3).tolist()
        }
        
        # Get topic summaries
        topic_summaries = {}
        for topic_id in range(results['n_topics_found']):
            keywords = analyzer.get_topic_keywords(topic_id)
            topic_summaries[f'topic_{topic_id}'] = {
                'keywords': keywords,
                'top_keywords': [kw[0] for kw in keywords[:5]]
            }
        
        results['topic_summaries'] = topic_summaries
        
        logger.info("Malicious posts topic analysis completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error in topic analysis: {e}")
        raise


def test_custom_topic_setup(sample_size: int = 50) -> Dict[str, Any]:
    """
    Test custom topic setup with sample data
    
    Args:
        sample_size: Number of sample posts to use for testing
        
    Returns:
        Test results
    """
    try:
        logger.info(f"Testing custom topic setup with {sample_size} sample posts")
        
        # Initialize analyzer
        analyzer = CustomTopicAnalyzer(n_topics=3, min_topic_size=5)
        
        # Load sample data
        df = analyzer.load_malicious_posts("malicious_posts.csv")
        sample_df = df.head(sample_size)
        
        # Test embedding generation
        logger.info("Testing embedding generation...")
        embeddings = analyzer.generate_embeddings(sample_df['combined_text'].tolist())
        
        # Test topic modeling
        logger.info("Testing topic modeling...")
        results = analyzer.train_topic_model(sample_df['combined_text'].tolist(), embeddings)
        
        # Test predictions
        logger.info("Testing topic predictions...")
        test_texts = sample_df['combined_text'].head(5).tolist()
        predictions = analyzer.predict_topics(test_texts)
        
        test_results = {
            "status": "success",
            "sample_size": sample_size,
            "embeddings_shape": embeddings.shape,
            "n_topics_found": results['n_topics_found'],
            "avg_topic_size": results['avg_topic_size'],
            "predictions_sample": predictions['topics'][:5],
            "model_info": analyzer.get_model_info()
        }
        
        logger.info("Custom topic setup test completed successfully")
        return test_results
        
    except Exception as e:
        logger.error(f"Custom topic setup test failed: {e}")
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    # Run test when script is executed directly
    test_results = test_custom_topic_setup(sample_size=100)
    print("Test Results:")
    for key, value in test_results.items():
        print(f"  {key}: {value}")

