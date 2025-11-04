"""
Admin Package for ContentGuard AI

Development-only admin functionality for testing and debugging.
This package is only loaded when ENABLE_ADMIN_ROUTES=true and FLASK_ENV=development.
"""

import os
from flask import current_app

def is_admin_enabled():
    """Check if admin functionality is enabled"""
    return (
        os.getenv('ENABLE_ADMIN_ROUTES', '').lower() == 'true' and 
        os.getenv('FLASK_ENV', '').lower() == 'development'
    )

def require_admin_enabled():
    """Decorator to require admin functionality to be enabled"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not is_admin_enabled():
                raise RuntimeError("Admin functionality is disabled")
            return f(*args, **kwargs)
        return wrapper
    return decorator
