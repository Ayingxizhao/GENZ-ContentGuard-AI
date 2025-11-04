"""
Profile upload routes for ContentGuard AI

Handles profile picture upload and processing endpoints.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.datastructures import FileStorage
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

from services.profile import ProfileService

logger = logging.getLogger(__name__)

upload_bp = Blueprint('profile_upload', __name__, url_prefix='/api/profile')
profile_service = ProfileService()


@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload and process profile picture"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get crop coordinates if provided
        crop_coords = None
        if 'crop_coords' in request.form:
            try:
                coords_str = request.form['crop_coords']
                crop_coords = tuple(map(int, coords_str.split(',')))
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid crop coordinates format"}), 400
        
        # Upload and process
        print(f"*** STARTING UPLOAD for user {current_user.id}, file: {file.filename}")
        logger.info(f"Starting upload for user {current_user.id}, file: {file.filename}")
        
        success, result = profile_service.upload_profile_picture(
            current_user.id, file, crop_coords
        )
        
        print(f"*** UPLOAD RESULT: success={success}, result={result}")
        logger.info(f"Upload result: success={success}, result={result}")
        
        if success:
            # Update user's profile URL in database
            print(f"*** UPDATING USER PROFILE URL: {result['urls']}")
            profile_service.update_user_profile_url(current_user.id, result['urls'])
            
            # Check what was actually saved
            print(f"*** USER PROFILE URL AFTER UPDATE: {current_user.profile_picture_url}")
            
            return jsonify({
                "success": True,
                "message": result['message'],
                "urls": result['urls']
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error in upload_profile_picture: {e}")
        return jsonify({"error": "Internal server error"}), 500


@upload_bp.route('/test-upload', methods=['POST'])
@login_required
def test_upload():
    """Test upload without S3 - for debugging"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Just validate the file, don't upload
        file_data = file.read()
        file.seek(0)
        
        from services.profile.image_processor import ImageProcessor
        processor = ImageProcessor()
        
        is_valid, message = processor.validate_file(file_data, file.filename)
        
        return jsonify({
            "valid": is_valid,
            "message": message,
            "filename": file.filename,
            "size": len(file_data)
        })
        
    except Exception as e:
        logger.error(f"Error in test_upload: {e}")
        return jsonify({"error": str(e)}), 500


@upload_bp.route('/upload-url', methods=['POST'])
@login_required
def get_upload_url():
    """Get presigned URL for direct upload"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "Filename is required"}), 400
        
        filename = data['filename']
        
        # Generate presigned URL
        success, result = profile_service.get_upload_presigned_url(
            current_user.id, filename
        )
        
        if success:
            return jsonify({
                "success": True,
                "upload_url": result['upload_url'],
                "file_key": result['file_key'],
                "max_file_size": result['max_file_size']
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error in get_upload_url: {e}")
        return jsonify({"error": "Internal server error"}), 500


@upload_bp.route('/process-uploaded', methods=['POST'])
@login_required
def process_uploaded_file():
    """Process an already uploaded file (from presigned URL)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        data = request.get_json()
        if not data or 'file_key' not in data:
            return jsonify({"error": "File key is required"}), 400
        
        file_key = data['file_key']
        
        # Get crop coordinates if provided
        crop_coords = None
        if 'crop_coords' in data:
            try:
                crop_coords = tuple(map(int, data['crop_coords'].split(',')))
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid crop coordinates format"}), 400
        
        # Process the uploaded file
        success, result = profile_service.process_uploaded_file(
            current_user.id, file_key, crop_coords
        )
        
        if success:
            # Update user's profile URL in database
            profile_service.update_user_profile_url(current_user.id, result['urls'])
            return jsonify({
                "success": True,
                "message": result['message'],
                "urls": result['urls']
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error in process_uploaded_file: {e}")
        return jsonify({"error": "Internal server error"}), 500


@upload_bp.route('/validate', methods=['POST'])
@login_required
def validate_image():
    """Validate uploaded image and return processing info"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file data
        file_data = file.read()
        file.seek(0)
        
        # Get image processing info
        info = profile_service.get_image_processing_info(file_data)
        
        if 'error' in info:
            return jsonify({"error": info['error']}), 400
        
        return jsonify({
            "success": True,
            "info": info
        }), 200
            
    except Exception as e:
        logger.error(f"Error in validate_image: {e}")
        return jsonify({"error": "Internal server error"}), 500


@upload_bp.route('/crop-preview', methods=['POST'])
@login_required
def get_crop_preview():
    """Generate preview of cropped image"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({"error": "Invalid CSRF token"}), 401
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get crop coordinates
        if 'crop_coords' not in request.form:
            return jsonify({"error": "Crop coordinates are required"}), 400
        
        try:
            crop_coords = tuple(map(int, request.form['crop_coords'].split(',')))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid crop coordinates format"}), 400
        
        # Read file data
        file_data = file.read()
        
        # Validate file
        from services.profile.image_processor import ImageProcessor
        processor = ImageProcessor()
        
        is_valid, message = processor.validate_file(file_data, file.filename)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Process image with crop
        success, processed_images = processor.process_profile_picture(
            file_data, crop_coords
        )
        
        if not success:
            return jsonify({"error": "Failed to process image"}), 400
        
        # Return base64 encoded preview
        import base64
        preview_data = base64.b64encode(processed_images['medium']).decode('utf-8')
        
        return jsonify({
            "success": True,
            "preview": f"data:image/webp;base64,{preview_data}"
        }), 200
            
    except Exception as e:
        logger.error(f"Error in get_crop_preview: {e}")
        return jsonify({"error": "Internal server error"}), 500
