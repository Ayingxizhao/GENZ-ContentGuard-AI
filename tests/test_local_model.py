import pytest
import pickle
from unittest.mock import patch, mock_open, MagicMock
from local_model import LocalGenZDetector, analyze_with_local_model

class TestLocalGenZDetector:
    """Test cases for the LocalGenZDetector class"""
    
    def test_init_model_loaded(self):
        """Test initialization with a loaded model"""
        mock_model_data = {
            'vectorizer': MagicMock(),
            'model': MagicMock()
        }
        
        with patch('builtins.open', mock_open()), \
             patch('pickle.load', return_value=mock_model_data):
            
            detector = LocalGenZDetector()
            assert detector.model_loaded is True
    
    def test_init_model_not_found(self):
        """Test initialization when model file is not found"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            detector = LocalGenZDetector()
            assert detector.model_loaded is False
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        
        # Test URL removal
        text_with_url = "Check out https://example.com for more info"
        cleaned = detector.clean_text(text_with_url)
        assert "https://example.com" not in cleaned
        
        # Test special character removal
        text_with_special = "Hello @#$%^&*() world!"
        cleaned = detector.clean_text(text_with_special)
        assert "@#$%^&*()" not in cleaned
        
        # Test whitespace normalization
        text_with_spaces = "  Multiple    spaces   here  "
        cleaned = detector.clean_text(text_with_spaces)
        assert cleaned == "Multiple spaces here"
    
    def test_analyze_keywords_malicious(self):
        """Test keyword analysis for malicious content"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        
        malicious_text = "You should kill yourself and go kys"
        result = detector.analyze_keywords(malicious_text)
        
        assert result['malicious_score'] > 0
        assert 'suicide_self_harm' in result['malicious_keywords']
        assert 'kill yourself' in result['malicious_keywords']['suicide_self_harm']
    
    def test_analyze_keywords_safe(self):
        """Test keyword analysis for safe content"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        
        safe_text = "I love helping people and providing support"
        result = detector.analyze_keywords(safe_text)
        
        assert result['safe_score'] > 0
        assert 'positive_support' in result['safe_keywords']
        assert 'help' in result['safe_keywords']['positive_support']
    
    def test_predict_model_not_loaded(self):
        """Test prediction when model is not loaded"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        detector.model_loaded = False
        
        result = detector.predict("Test title", "Test content")
        
        assert 'error' in result
        assert result['prediction'] == 'unknown'
    
    def test_predict_no_text(self):
        """Test prediction with no text provided"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        detector.model_loaded = True
        
        result = detector.predict("", "")
        
        assert 'error' in result
        assert 'No text provided' in result['error']
    
    def test_predict_success(self):
        """Test successful prediction"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        detector.model_loaded = True
        detector.vectorizer = MagicMock()
        detector.model = MagicMock()
        
        # Mock the vectorizer and model
        detector.vectorizer.transform.return_value = [[1, 2, 3]]
        detector.model.predict.return_value = ['safe']
        detector.model.predict_proba.return_value = [[0.8, 0.2]]
        
        result = detector.predict("Safe title", "Safe content")
        
        assert result['analysis'] == 'SAFE'
        assert result['is_malicious'] is False
        assert 'confidence' in result
        assert 'detailed_analysis' in result
    
    def test_get_model_info_loaded(self):
        """Test getting model info when model is loaded"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        detector.model_loaded = True
        detector.vectorizer = MagicMock()
        detector.vectorizer.get_feature_names_out.return_value.shape = [1000]
        
        info = detector.get_model_info()
        
        assert info['status'] == 'loaded'
        assert info['model_type'] == 'MultinomialNB'
        assert info['features'] == 1000
    
    def test_get_model_info_not_loaded(self):
        """Test getting model info when model is not loaded"""
        detector = LocalGenZDetector.__new__(LocalGenZDetector)
        detector.model_loaded = False
        
        info = detector.get_model_info()
        
        assert info['status'] == 'not_loaded'

class TestAnalyzeWithLocalModel:
    """Test cases for the analyze_with_local_model function"""
    
    def test_analyze_with_local_model(self):
        """Test the convenience function"""
        with patch('local_model.local_detector') as mock_detector:
            mock_detector.predict.return_value = {
                'analysis': 'SAFE',
                'is_malicious': False,
                'confidence': '90%'
            }
            
            result = analyze_with_local_model("Test title", "Test content")
            
            mock_detector.predict.assert_called_once_with("Test title", "Test content")
            assert result['analysis'] == 'SAFE'
