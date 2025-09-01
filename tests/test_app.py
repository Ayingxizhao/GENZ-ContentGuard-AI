import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_local_detector():
    """Mock the local detector for testing"""
    with patch('app.local_detector') as mock:
        mock.model_loaded = True
        mock.predict.return_value = {
            'analysis': 'SAFE',
            'is_malicious': False,
            'confidence': '85.5%',
            'model_type': 'local_ml',
            'probabilities': {'safe': 0.855, 'malicious': 0.145}
        }
        yield mock

class TestApp:
    """Test cases for the Flask application"""
    
    def test_index_route(self, client):
        """Test the index route returns the main page"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
    
    def test_health_route(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_model_info_route(self, client, mock_local_detector):
        """Test the model info endpoint"""
        mock_local_detector.get_model_info.return_value = {
            'status': 'loaded',
            'model_type': 'MultinomialNB',
            'vectorizer_type': 'TfidfVectorizer',
            'features': 1000
        }
        
        response = client.get('/model-info')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'local_model' in data
        assert data['local_model']['status'] == 'loaded'
    
    def test_analyze_route_success(self, client, mock_local_detector):
        """Test successful text analysis"""
        response = client.post('/analyze', 
                             json={'title': 'Test title', 'content': 'Test content'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'analysis' in data
        assert 'confidence' in data
        assert 'timestamp' in data
        assert data['is_malicious'] is False
    
    def test_analyze_route_no_content(self, client):
        """Test analysis with no content provided"""
        response = client.post('/analyze', 
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_analyze_route_model_not_loaded(self, client):
        """Test analysis when model is not loaded"""
        with patch('app.local_detector') as mock:
            mock.model_loaded = False
            
            response = client.post('/analyze', 
                                 json={'title': 'Test', 'content': 'Test'},
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not loaded' in data['error']
    
    def test_analyze_route_malicious_content(self, client, mock_local_detector):
        """Test analysis of malicious content"""
        mock_local_detector.predict.return_value = {
            'analysis': 'MALICIOUS',
            'is_malicious': True,
            'confidence': '92.3%',
            'model_type': 'local_ml',
            'probabilities': {'safe': 0.077, 'malicious': 0.923}
        }
        
        response = client.post('/analyze', 
                             json={'title': 'Bad title', 'content': 'Harmful content'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_malicious'] is True
        assert data['analysis'] == 'MALICIOUS'
    
    def test_analyze_route_invalid_json(self, client):
        """Test analysis with invalid JSON"""
        response = client.post('/analyze', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
