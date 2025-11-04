"""
Profile routes package for ContentGuard AI

This package provides API endpoints for profile picture management.
"""

from .upload import upload_bp
from .management import management_bp

__all__ = ['upload_bp', 'management_bp']
