"""
Profile service for ContentGuard AI

Main service that orchestrates profile picture upload, processing, and storage.
"""

import os
import logging
from typing import Dict, Optional, Tuple, Any
from flask import current_app
from werkzeug.datastructures import FileStorage

from .storage_handler import StorageHandler
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class ProfileService:
    """Main service for profile picture operations"""
    
    def __init__(self):
        self.storage_handler = StorageHandler()
        self.image_processor = ImageProcessor()
    
    def upload_profile_picture(self, user_id: int, file: FileStorage, 
                             crop_coords: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, Dict[str, Any]]:
        """Upload and process profile picture"""
        try:
            logger.info(f"Starting profile picture upload for user {user_id}")
            
            # Validate file
            if not file or not file.filename:
                logger.error("No file provided")
                return False, {"error": "No file provided"}
            
            file_data = file.read()
            file.seek(0)  # Reset file pointer
            
            logger.info(f"File read successfully, size: {len(file_data)} bytes")
            
            is_valid, message = self.image_processor.validate_file(file_data, file.filename)
            logger.info(f"File validation: valid={is_valid}, message={message}")
            
            if not is_valid:
                return False, {"error": message}
            
            # Process image
            logger.info("Starting image processing")
            success, processed_images = self.image_processor.process_profile_picture(
                file_data, crop_coords
            )
            
            logger.info(f"Image processing: success={success}, images={list(processed_images.keys()) if success else 'None'}")
            
            if not success:
                return False, {"error": "Failed to process image"}
            
            # Delete existing profile pictures
            logger.info("Deleting existing profile pictures")
            self.storage_handler.delete_user_profile_pictures(user_id)
            
            # Upload new images
            logger.info("Starting S3 upload")
            upload_success, urls = self.storage_handler.upload_multiple_sizes(
                user_id, processed_images
            )
            
            logger.info(f"S3 upload: success={upload_success}, urls={urls}")
            
            if not upload_success:
                return False, {"error": "Failed to upload images"}
            
            return True, {
                "urls": urls,
                "message": "Profile picture uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Error uploading profile picture for user {user_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, {"error": "Internal server error"}
    
    def get_upload_presigned_url(self, user_id: int, filename: str) -> Tuple[bool, Dict[str, Any]]:
        """Get presigned URL for direct upload"""
        try:
            # Validate filename
            if not self.image_processor._is_allowed_extension(filename):
                return False, {"error": "File type not supported"}
            
            # Generate file key
            file_key = self.storage_handler.generate_file_key(user_id, 'original')
            
            # Generate presigned URL
            presigned_url = self.storage_handler.generate_presigned_upload_url(
                user_id, file_key
            )
            
            if not presigned_url:
                return False, {"error": "Failed to generate upload URL"}
            
            return True, {
                "upload_url": presigned_url,
                "file_key": file_key,
                "max_file_size": self.image_processor.MAX_FILE_SIZE
            }
            
        except Exception as e:
            logger.error(f"Error generating presigned URL for user {user_id}: {e}")
            return False, {"error": "Internal server error"}
    
    def process_uploaded_file(self, user_id: int, file_key: str, 
                            crop_coords: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, Dict[str, Any]]:
        """Process an already uploaded file (from presigned URL)"""
        try:
            # Download the uploaded file from S3
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            try:
                response = s3_client.get_object(
                    Bucket=self.storage_handler.bucket_name,
                    Key=file_key
                )
                file_data = response['Body'].read()
            except ClientError as e:
                logger.error(f"Failed to download uploaded file: {e}")
                return False, {"error": "Failed to process uploaded file"}
            
            # Process image
            success, processed_images = self.image_processor.process_profile_picture(
                file_data, crop_coords
            )
            
            if not success:
                return False, {"error": "Failed to process image"}
            
            # Delete existing profile pictures
            self.storage_handler.delete_user_profile_pictures(user_id)
            
            # Upload processed images
            upload_success, urls = self.storage_handler.upload_multiple_sizes(
                user_id, processed_images
            )
            
            if not upload_success:
                return False, {"error": "Failed to upload processed images"}
            
            # Delete the original uploaded file
            self.storage_handler.delete_file(file_key)
            
            return True, {
                "urls": urls,
                "message": "Profile picture processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing uploaded file for user {user_id}: {e}")
            return False, {"error": "Internal server error"}
    
    def delete_profile_picture(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """Delete user's profile picture"""
        try:
            success = self.storage_handler.delete_user_profile_pictures(user_id)
            
            if success:
                return True, {"message": "Profile picture deleted successfully"}
            else:
                return False, {"error": "Failed to delete profile picture"}
                
        except Exception as e:
            logger.error(f"Error deleting profile picture for user {user_id}: {e}")
            return False, {"error": "Internal server error"}
    
    def get_profile_picture_info(self, user_id: int) -> Dict[str, Any]:
        """Get profile picture information for user"""
        try:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            if not user.profile_picture_url:
                return {
                    "has_profile_picture": False,
                    "message": "No profile picture set"
                }
            
            return {
                "has_profile_picture": True,
                "profile_picture_url": user.profile_picture_url,
                "message": "Profile picture found"
            }
            
        except Exception as e:
            logger.error(f"Error getting profile picture info for user {user_id}: {e}")
            return {"error": "Internal server error"}
    
    def update_user_profile_url(self, user_id: int, urls: Dict[str, str]) -> bool:
        """Update user's profile picture URL in database"""
        try:
            from models import User
            from app import db
            
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Use medium size as the main profile picture URL
            user.profile_picture_url = urls.get('medium', urls.get('original'))
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile URL for user {user_id}: {e}")
            return False
    
    def validate_crop_coordinates(self, crop_coords: Tuple[int, int, int, int], 
                                image_size: Tuple[int, int]) -> bool:
        """Validate crop coordinates are within image bounds"""
        if len(crop_coords) != 4:
            return False
        
        left, top, right, bottom = crop_coords
        width, height = image_size
        
        # Check coordinates are within bounds
        if (left < 0 or top < 0 or right > width or bottom > height):
            return False
        
        # Check coordinates form a valid rectangle
        if (left >= right or top >= bottom):
            return False
        
        return True
    
    def get_image_processing_info(self, file_data: bytes) -> Dict[str, Any]:
        """Get information about image for processing UI"""
        try:
            info = self.image_processor.get_image_info(file_data)
            
            if not info:
                return {"error": "Could not read image information"}
            
            return {
                "size": info["size"],
                "format": info["format"],
                "file_size": info["file_size"],
                "max_file_size": self.image_processor.MAX_FILE_SIZE,
                "allowed_extensions": list(self.image_processor.ALLOWED_EXTENSIONS),
                "output_sizes": self.image_processor.SIZES
            }
            
        except Exception as e:
            logger.error(f"Error getting image processing info: {e}")
            return {"error": "Internal server error"}
