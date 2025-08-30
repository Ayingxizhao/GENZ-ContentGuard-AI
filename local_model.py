import pickle
import re
from typing import Dict, Any

class LocalGenZDetector:
    def __init__(self, model_path='genz_detector_model.pkl'):
        """Initialize the local model detector"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.model = model_data['model']
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
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?\,\;\:\-\(\)]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def predict(self, title: str = "", content: str = "") -> Dict[str, Any]:
        """Predict if text is malicious using local model"""
        if not self.model_loaded:
            return {
                'error': 'Model not loaded. Please run data_processor.py first.',
                'prediction': 'unknown',
                'confidence': 0.0
            }
        
        # Combine title and content
        combined_text = f"{title} {content}".strip()
        
        if not combined_text:
            return {
                'error': 'No text provided for analysis',
                'prediction': 'unknown',
                'confidence': 0.0
            }
        
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
            
            # Map prediction to your existing format
            if prediction == 'malicious':
                analysis = 'MALICIOUS'
                is_malicious = True
            else:
                analysis = 'SAFE'
                is_malicious = False
            
            return {
                'analysis': analysis,
                'is_malicious': is_malicious,
                'confidence': f"{confidence:.1%}",
                'prediction': prediction,
                'probabilities': {
                    'safe': float(probabilities[0]),
                    'malicious': float(probabilities[1])
                },
                'model_type': 'local_ml'
            }
            
        except Exception as e:
            return {
                'error': f'Prediction failed: {str(e)}',
                'prediction': 'unknown',
                'confidence': 0.0
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model_loaded:
            return {'status': 'not_loaded'}
        
        return {
            'status': 'loaded',
            'model_type': 'MultinomialNB',
            'vectorizer_type': 'TfidfVectorizer',
            'features': self.vectorizer.get_feature_names_out().shape[0]
        }

# Global instance for easy access
local_detector = LocalGenZDetector()

def analyze_with_local_model(title: str = "", content: str = "") -> Dict[str, Any]:
    """Convenience function to analyze text with local model"""
    return local_detector.predict(title, content)
