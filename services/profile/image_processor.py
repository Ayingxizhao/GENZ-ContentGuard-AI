"""
Image processor for profile pictures

Handles image resizing, circular cropping, and format conversion.
"""

import os
import io
import logging
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes profile pictures with circular cropping and resizing"""
    
    # Supported image formats
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    
    # Size configurations
    SIZES = {
        'thumbnail': (150, 150),
        'medium': (300, 300),
        'original': (1200, 1200)
    }
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    def __init__(self):
        self.supported_formats = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'WEBP': 'image/webp'
        }
    
    def validate_file(self, file_data: bytes, filename: str) -> Tuple[bool, str]:
        """Validate uploaded file"""
        # Check file size
        if len(file_data) > self.MAX_FILE_SIZE:
            return False, "File size exceeds 5MB limit"
        
        # Check file extension
        if not self._is_allowed_extension(filename):
            return False, "File type not supported. Use JPG, PNG, or WebP"
        
        # Check if it's a valid image
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                img.verify()
            return True, "File is valid"
        except Exception as e:
            logger.error(f"Invalid image file: {e}")
            return False, "Invalid image file"
    
    def _is_allowed_extension(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return extension in self.ALLOWED_EXTENSIONS
    
    def create_circular_crop(self, image: Image.Image, crop_coords: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """Create circular cropped version of the image"""
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGBA')
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # If no crop coordinates provided, use center crop
        if crop_coords is None:
            image = self._center_crop_to_square(image)
        else:
            image = image.crop(crop_coords)
            image = self._ensure_square_aspect_ratio(image)
        
        # Create circular mask
        size = image.size[0]
        mask = Image.new('L', (size, size), 0)
        draw = Image.new('L', (size, size), 0)
        
        # Draw circle on mask
        from PIL import ImageDraw
        d = ImageDraw.Draw(draw)
        d.ellipse((0, 0, size, size), fill=255)
        mask.paste(draw)
        
        # Apply circular mask
        image.putalpha(mask)
        
        return image
    
    def _center_crop_to_square(self, image: Image.Image) -> Image.Image:
        """Crop image to square using center crop"""
        width, height = image.size
        min_dim = min(width, height)
        
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        
        return image.crop((left, top, right, bottom))
    
    def _ensure_square_aspect_ratio(self, image: Image.Image) -> Image.Image:
        """Ensure image has square aspect ratio"""
        width, height = image.size
        if width == height:
            return image
        
        # Use the smaller dimension as the target size
        target_size = min(width, height)
        return self._center_crop_to_square(image)
    
    def resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining quality"""
        # Use high-quality resampling
        return image.resize(size, Image.Resampling.LANCZOS)
    
    def process_profile_picture(self, file_data: bytes, crop_coords: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, Dict[str, bytes]]:
        """Process profile picture into multiple sizes with circular crop"""
        try:
            # Open image
            with Image.open(io.BytesIO(file_data)) as img:
                # Auto-rotate based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Create circular cropped version
                circular_img = self.create_circular_crop(img, crop_coords)
                
                # Process different sizes
                processed_images = {}
                
                for size_name, dimensions in self.SIZES.items():
                    # Resize image
                    resized_img = self.resize_image(circular_img, dimensions)
                    
                    # Convert to WebP format
                    output = io.BytesIO()
                    
                    # Handle transparency
                    if resized_img.mode == 'RGBA':
                        # Create white background for WebP
                        background = Image.new('RGB', resized_img.size, (255, 255, 255))
                        background.paste(resized_img, mask=resized_img.split()[-1])
                        resized_img = background
                    
                    # Save as WebP with optimization
                    resized_img.save(output, format='WEBP', quality=85, optimize=True)
                    processed_images[size_name] = output.getvalue()
                
                return True, processed_images
                
        except Exception as e:
            logger.error(f"Error processing profile picture: {e}")
            return False, {}
    
    def get_image_info(self, file_data: bytes) -> Dict[str, Any]:
        """Get information about the uploaded image"""
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'file_size': len(file_data)
                }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {}
    
    def optimize_for_web(self, image_data: bytes) -> bytes:
        """Optimize image for web delivery"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                
                # Optimize and save as WebP
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=85, optimize=True)
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image_data
    
    def create_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (150, 150)) -> bytes:
        """Create thumbnail from image"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Auto-rotate
                img = ImageOps.exif_transpose(img)
                
                # Create circular crop
                circular_img = self.create_circular_crop(img)
                
                # Resize
                thumbnail = self.resize_image(circular_img, size)
                
                # Convert to WebP
                output = io.BytesIO()
                if thumbnail.mode == 'RGBA':
                    background = Image.new('RGB', thumbnail.size, (255, 255, 255))
                    background.paste(thumbnail, mask=thumbnail.split()[-1])
                    thumbnail = background
                
                thumbnail.save(output, format='WEBP', quality=85, optimize=True)
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return image_data
