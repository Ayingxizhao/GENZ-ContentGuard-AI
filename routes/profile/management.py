"""
Profile management routes for ContentGuard AI

Handles profile picture management, deletion, and status endpoints.
"""

import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

from services.profile import ProfileService

logger = logging.getLogger(__name__)

management_bp = Blueprint('profile_management', __name__, url_prefix='/api/profile')
profile_service = ProfileService()


@management_bp.route('/status', methods=['GET'])
@login_required
def get_profile_status():
    """Get current profile picture status"""
    try:
        info = profile_service.get_profile_picture_info(current_user.id)
        
        if 'error' in info:
            return jsonify({"error": info['error']}), 404
        
        return jsonify({
            "success": True,
            "status": info
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_profile_status: {e}")
        return jsonify({"error": "Internal server error"}), 500


@management_bp.route('/delete', methods=['DELETE'])
@login_required
def delete_profile_picture():
    """Delete user's profile picture"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        success, result = profile_service.delete_profile_picture(current_user.id)
        
        if success:
            # Update user's profile URL in database
            from models import User
            from app import db
            
            user = User.query.get(current_user.id)
            if user:
                user.profile_picture_url = None
                db.session.commit()
            
            return jsonify({
                "success": True,
                "message": result['message']
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error in delete_profile_picture: {e}")
        return jsonify({"error": "Internal server error"}), 500


@management_bp.route('/urls', methods=['GET'])
@login_required
def get_profile_urls():
    """Get all profile picture URLs for the current user"""
    try:
        from models import User
        
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if not user.profile_picture_url:
            return jsonify({
                "success": True,
                "has_profile_picture": False,
                "urls": {}
            }), 200
        
        # Extract different sizes from the main URL
        # This assumes a consistent URL pattern
        base_url = user.profile_picture_url
        urls = {
            "medium": base_url,
            "thumbnail": base_url.replace('/medium/', '/thumbnail/'),
            "original": base_url.replace('/medium/', '/original/')
        }
        
        return jsonify({
            "success": True,
            "has_profile_picture": True,
            "urls": urls
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_profile_urls: {e}")
        return jsonify({"error": "Internal server error"}), 500


@management_bp.route('/update-primary', methods=['POST'])
@login_required
def update_primary_size():
    """Update which size is used as the primary profile picture"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        data = request.get_json()
        if not data or 'size' not in data:
            return jsonify({"error": "Size is required"}), 400
        
        size = data['size']
        if size not in ['thumbnail', 'medium', 'original']:
            return jsonify({"error": "Invalid size. Must be thumbnail, medium, or original"}), 400
        
        # Get current URLs
        info = profile_service.get_profile_picture_info(current_user.id)
        if not info.get('has_profile_picture'):
            return jsonify({"error": "No profile picture found"}), 404
        
        # Update user's profile URL
        from models import User
        from app import db
        
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Extract the specific size URL
        base_url = user.profile_picture_url
        if size == 'medium':
            new_url = base_url
        elif size == 'thumbnail':
            new_url = base_url.replace('/medium/', '/thumbnail/')
        else:  # original
            new_url = base_url.replace('/medium/', '/original/')
        
        user.profile_picture_url = new_url
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Primary profile picture updated to {size} size",
            "new_url": new_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error in update_primary_size: {e}")
        return jsonify({"error": "Internal server error"}), 500


@management_bp.route('/settings', methods=['GET'])
@login_required
def get_profile_settings():
    """Get profile picture upload settings and limits"""
    try:
        from services.profile.image_processor import ImageProcessor
        
        processor = ImageProcessor()
        
        settings = {
            "max_file_size": processor.MAX_FILE_SIZE,
            "max_file_size_mb": processor.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": list(processor.ALLOWED_EXTENSIONS),
            "output_sizes": processor.SIZES,
            "supported_formats": processor.supported_formats
        }
        
        return jsonify({
            "success": True,
            "settings": settings
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_profile_settings: {e}")
        return jsonify({"error": "Internal server error"}), 500
