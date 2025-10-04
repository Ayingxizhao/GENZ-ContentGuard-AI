"""Local model implementation using trained DistilBERT model."""

import logging
from typing import Dict, Any
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalGenZDetector:
    """Local GenZ language detector using DistilBERT."""

    def __init__(self, model_path: str = "final_model") -> None:
        """Initialize the detector with the trained model."""
        self.model_path = model_path
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self) -> None:
        """Load the trained DistilBERT model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.eval()
            self.model_loaded = True
            logger.info(f"✓ Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.warning(f"Failed to load model from {self.model_path}: {e}")
            self.model_loaded = False

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict if text contains malicious content."""
        if not self.model_loaded:
            return {"error": "Model not loaded"}

        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0]
                prediction = torch.argmax(probabilities).item()

            is_malicious = bool(prediction == 1)
            confidence = f"{probabilities[prediction].item() * 100:.2f}%"

            return {
                "is_malicious": is_malicious,
                "confidence": confidence,
                "probabilities": {
                    "safe": f"{probabilities[0].item() * 100:.2f}%",
                    "malicious": f"{probabilities[1].item() * 100:.2f}%",
                },
                "model_type": "DistilBERT",
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"error": str(e)}

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "loaded": self.model_loaded,
            "model_path": self.model_path,
            "model_type": "DistilBERT" if self.model_loaded else "None",
        }


# Initialize the detector
local_detector = LocalGenZDetector()


def analyze_with_local_model(title: str, content: str) -> Dict[str, Any]:
    """Analyze content using the local model."""
    text = f"{title} {content}".strip()

    if not text:
        return {"error": "No content to analyze"}

    result = local_detector.predict(text)

    if "error" in result:
        return result

    # Format the response
    analysis = "Malicious content detected" if result["is_malicious"] else "Content appears safe"

    return {
        "analysis": analysis,
        "is_malicious": result["is_malicious"],
        "confidence": result["confidence"],
        "model_type": result["model_type"],
        "probabilities": result["probabilities"],
    }
