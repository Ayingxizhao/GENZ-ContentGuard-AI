"""
Services package for ContentGuard AI
Provides modular model services for content analysis
"""
from .model_service import get_model_service, ModelType

__all__ = ['get_model_service', 'ModelType']
