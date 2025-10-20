"""
Model service factory and base interface
"""
from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, Any


class ModelType(Enum):
    """Available model types"""
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"


class BaseModelService(ABC):
    """Base interface for model services"""
    
    @abstractmethod
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return structured result
        
        Args:
            text: Content to analyze
            
        Returns:
            Dict with keys: analysis, is_malicious, confidence, probabilities, model_type
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return human-readable model name"""
        pass


def get_model_service(model_type: ModelType) -> BaseModelService:
    """
    Factory function to get model service instance
    
    Args:
        model_type: Type of model to instantiate
        
    Returns:
        Instance of BaseModelService
    """
    if model_type == ModelType.HUGGINGFACE:
        from .hf_model import HuggingFaceModelService
        return HuggingFaceModelService()
    elif model_type == ModelType.GEMINI:
        from .gemini_model import GeminiModelService
        return GeminiModelService()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
