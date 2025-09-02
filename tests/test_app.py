import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def client() -> Any:
    """Create a test client for the Flask application"""
    with patch("local_model.local_detector") as mock_detector:
        mock_detector.model_loaded = True
        mock_detector.predict.return_value = {
            "analysis": "SAFE",
            "is_malicious": False,
            "confidence": "85.5%",
            "model_type": "local_ml",
            "probabilities": {"safe": 0.855, "malicious": 0.145},
        }
        mock_detector.get_model_info.return_value = {
            "status": "loaded",
            "model_type": "MultinomialNB",
            "vectorizer_type": "TfidfVectorizer",
            "features": 1000,
        }

        from app import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client


class TestApp:
    """Test cases for the Flask application"""

    def test_index_route(self, client: Any) -> None:
        """Test the index route returns the main page"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_health_route(self, client: Any) -> None:
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_model_info_route(self, client: Any) -> None:
        """Test the model info endpoint"""
        with patch("app.local_detector") as mock_detector:
            mock_detector.get_model_info.return_value = {
                "status": "loaded",
                "model_type": "MultinomialNB",
                "vectorizer_type": "TfidfVectorizer",
                "features": 1000,
            }

            response = client.get("/model-info")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "local_model" in data
            assert data["local_model"]["status"] == "loaded"

    def test_analyze_route_success(self, client: Any) -> None:
        """Test successful text analysis"""
        with patch("app.local_detector") as mock_detector:
            mock_detector.model_loaded = True
            mock_detector.predict.return_value = {
                "analysis": "SAFE",
                "is_malicious": False,
                "confidence": "85.5%",
                "model_type": "local_ml",
                "probabilities": {"safe": 0.855, "malicious": 0.145},
            }

            response = client.post(
                "/analyze", json={"title": "Test title", "content": "Test content"}, content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "analysis" in data
            assert "confidence" in data
            assert "timestamp" in data
            assert data["is_malicious"] is False

    def test_analyze_route_no_content(self, client: Any) -> None:
        """Test analysis with no content provided"""
        response = client.post("/analyze", json={}, content_type="application/json")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_analyze_route_model_not_loaded(self, client: Any) -> None:
        """Test analysis when model is not loaded"""
        with patch("app.local_detector") as mock:
            mock.model_loaded = False

            response = client.post("/analyze", json={"title": "Test", "content": "Test"}, content_type="application/json")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "not loaded" in data["error"]

    def test_analyze_route_malicious_content(self, client: Any) -> None:
        """Test analysis of malicious content"""
        with patch("local_model.local_detector") as mock_detector:
            mock_detector.model_loaded = True
            mock_detector.predict.return_value = {
                "analysis": "MALICIOUS",
                "is_malicious": True,
                "confidence": "92.3%",
                "model_type": "local_ml",
                "probabilities": {"safe": 0.077, "malicious": 0.923},
            }

            from app import app

            app.config["TESTING"] = True
            test_client = app.test_client()

            response = test_client.post(
                "/analyze", json={"title": "Bad title", "content": "Harmful content"}, content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["is_malicious"] is True
            assert data["analysis"] == "MALICIOUS"

    def test_analyze_route_invalid_json(self, client: Any) -> None:
        """Test analysis with invalid JSON"""
        response = client.post("/analyze", data="invalid json", content_type="application/json")

        assert response.status_code == 500
