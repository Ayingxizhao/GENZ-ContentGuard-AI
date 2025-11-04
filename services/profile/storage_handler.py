"""
AWS S3 storage handler for profile pictures

Handles file upload, deletion, and URL generation for profile pictures.
"""

import os
import uuid
import logging
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class StorageHandler:
    """Handles AWS S3 storage operations for profile pictures"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        # CloudFront is optional for testing - use direct S3 URLs if not configured
        
        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET environment variable is required")
    
    def generate_file_key(self, user_id: int, size: str = 'original') -> str:
        """Generate unique file key for S3 storage"""
        file_id = str(uuid.uuid4())
        return f"profile-pictures/{user_id}/{size}/{file_id}.webp"
    
    def generate_presigned_upload_url(self, user_id: int, file_key: str, 
                                    content_type: str = 'image/webp') -> Optional[str]:
        """Generate presigned URL for direct upload to S3"""
        try:
            return self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': content_type,
                    'CacheControl': 'max-age=31536000',  # 1 year cache
                    'Metadata': {
                        'user-id': str(user_id),
                        'upload-type': 'profile-picture'
                    }
                },
                ExpiresIn=3600  # 1 hour expiry
            )
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            return None
    
    def upload_file(self, file_data: bytes, file_key: str, 
                   content_type: str = 'image/webp') -> bool:
        """Upload file directly to S3 (fallback method)"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type,
                CacheControl='max-age=31536000',
                Metadata={
                    'upload-type': 'profile-picture'
                }
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return False
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
    
    def get_file_url(self, file_key: str, size: str = 'original') -> str:
        """Get public URL for file (via CloudFront or direct S3)"""
        cloudfront_domain = os.getenv('AWS_CLOUDFRONT_DOMAIN')
        
        if cloudfront_domain:
            return f"https://{cloudfront_domain}/{file_key}"
        else:
            # Use direct S3 URL for testing
            return f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{file_key}"
    
    def upload_multiple_sizes(self, user_id: int, sizes: dict) -> Tuple[bool, dict]:
        """Upload multiple image sizes and return URLs"""
        urls = {}
        success = True
        
        for size_name, image_data in sizes.items():
            file_key = self.generate_file_key(user_id, size_name)
            
            if self.upload_file(image_data, file_key):
                urls[size_name] = self.get_file_url(file_key, size_name)
            else:
                success = False
                break
        
        return success, urls
    
    def delete_user_profile_pictures(self, user_id: int) -> bool:
        """Delete all profile pictures for a user"""
        try:
            # List all objects in user's profile picture directory
            prefix = f"profile-pictures/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            # Delete all found objects
            if 'Contents' in response:
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                
                if objects_to_delete:
                    self.s3_client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
            
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to delete user profile pictures: {e}")
            return False
    
    def validate_file_exists(self, file_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False
