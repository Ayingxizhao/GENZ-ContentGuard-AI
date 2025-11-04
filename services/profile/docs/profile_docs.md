# Profile Picture Upload System

## Overview

The Profile Picture Upload System allows users to upload, crop, and manage custom profile pictures in the ContentGuard AI application. It provides a modern, responsive interface with circular cropping, multiple size generation, and cloud storage via AWS S3.

## Features

- **Drag-and-drop upload** with progress indicators
- **Circular image cropping** with real-time preview
- **Multiple size generation** (thumbnail, medium, original)
- **AWS S3 storage** with CloudFront CDN support
- **Image validation** and optimization
- **Mobile-responsive design**
- **Accessibility compliance**
- **CSRF protection** and security measures

## Architecture

### Backend Components

#### Services (`services/profile/`)

- **`profile_service.py`** - Main service orchestrator that handles upload workflows
- **`storage_handler.py`** - AWS S3 operations and file management
- **`image_processor.py`** - Image processing, resizing, and circular cropping

#### Routes (`routes/profile/`)

- **`upload.py`** - Upload endpoints:
  - `POST /api/profile/upload` - Upload and process profile picture
  - `POST /api/profile/upload-url` - Get presigned URL for direct upload
  - `POST /api/profile/process-uploaded` - Process uploaded file from S3
  - `POST /api/profile/validate` - Validate uploaded image
  - `POST /api/profile/crop-preview` - Generate crop preview

- **`management.py`** - Management endpoints:
  - `GET /api/profile/status` - Get current profile picture status
  - `DELETE /api/profile/delete` - Remove profile picture
  - `GET /api/profile/urls` - Get all profile picture URLs
  - `POST /api/profile/update-primary` - Update primary size
  - `GET /api/profile/settings` - Get upload settings and limits

#### Database Model

Updated `User` model in `models.py`:
- Added `profile_picture_url` field for custom profile pictures
- Existing `avatar_url` field retained for OAuth avatars

### Frontend Components

#### JavaScript (`static/profile/js/`)

- **`upload.js`** - Main upload component with drag-and-drop functionality
- **`cropper.js`** - Advanced cropping interface with circular mask

#### CSS (`static/profile/css/`)

- **`profile.css`** - Modern, responsive styling with dark mode support

#### Templates (`templates/profile/`)

- **`upload.html`** - Main upload interface with cropping
- **`crop.html`** - Dedicated cropping page

## API Endpoints

### Upload Endpoints

#### Upload Profile Picture
```http
POST /api/profile/upload
Content-Type: multipart/form-data
X-CSRFToken: <token>

Body:
- file: Image file (JPEG, PNG, WebP, max 5MB)
- crop_coords: "x,y,width,height" (optional)
```

Response:
```json
{
  "success": true,
  "message": "Profile picture uploaded successfully",
  "urls": {
    "thumbnail": "https://cdn.example.com/thumb.jpg",
    "medium": "https://cdn.example.com/medium.jpg",
    "original": "https://cdn.example.com/original.jpg"
  }
}
```

#### Get Presigned Upload URL
```http
POST /api/profile/upload-url
Content-Type: application/json
X-CSRFToken: <token>

Body:
{
  "filename": "profile.jpg"
}
```

Response:
```json
{
  "success": true,
  "upload_url": "https://s3.amazonaws.com/bucket/presigned-url",
  "file_key": "profile-pictures/123/original/uuid.webp",
  "max_file_size": 5242880
}
```

### Management Endpoints

#### Get Profile Status
```http
GET /api/profile/status
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "status": {
    "has_profile_picture": true,
    "profile_picture_url": "https://cdn.example.com/medium.jpg"
  }
}
```

#### Delete Profile Picture
```http
DELETE /api/profile/delete
X-CSRFToken: <token>
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "message": "Profile picture deleted successfully"
}
```

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_profile_bucket_name
AWS_REGION=us-east-1
# AWS_CLOUDFRONT_DOMAIN=your-cdn.cloudfront.net  # Optional - comment out for testing

# Profile Settings (optional)
PROFILE_MAX_FILE_SIZE=5242880  # 5MB in bytes
PROFILE_ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
```

### Dependencies

Added to `requirements.txt`:

```
boto3>=1.34.0          # AWS SDK
Pillow>=10.0.0         # Image processing
Flask-WTF>=1.2.0       # Form validation
WTForms>=3.1.0         # Form handling
```

## Usage

### Basic Upload Flow

1. **User visits upload page**: `/profile/upload`
2. **Selects image**: Via drag-and-drop or file picker
3. **Image validation**: Client and server-side validation
4. **Crop adjustment**: Circular cropping interface with preview
5. **Upload process**: Image processed and uploaded to S3
6. **Database update**: User profile picture URL updated

### Integration with Auth Flow

- **New users**: Automatically redirected to `/profile/upload` after signup/login
- **Existing users**: Can access profile upload via navigation
- **OAuth users**: Can replace OAuth avatar with custom profile picture

### Frontend Integration

```javascript
// Initialize upload component
const profileUpload = new ProfilePictureUpload({
    dropZoneId: 'profile-drop-zone',
    fileInputId: 'profile-file-input',
    previewId: 'profile-preview',
    uploadUrl: '/api/profile/upload',
    validateUrl: '/api/profile/validate',
    onSuccess: (message, data) => {
        console.log('Upload successful:', data);
        // Handle success (e.g., redirect, update UI)
    },
    onError: (error) => {
        console.error('Upload failed:', error);
        // Handle error
    }
});
```

## File Storage

### S3 Structure

```
profile-pictures/
├── {user_id}/
│   ├── thumbnail/
│   │   └── {uuid}.webp
│   ├── medium/
│   │   └── {uuid}.webp
│   └── original/
│       └── {uuid}.webp
```

### Image Specifications

- **Format**: WebP (optimized for web)
- **Sizes**:
  - Thumbnail: 150×150px
  - Medium: 300×300px (primary)
  - Original: 1200×1200px
- **Shape**: Circular with transparent background
- **Quality**: 85% compression with optimization

## Security Features

- **CSRF protection** on all endpoints
- **File type validation** (images only)
- **Size limits** (5MB maximum)
- **Content-Type validation**
- **S3 presigned URLs** with expiration
- **Rate limiting** support
- **Input sanitization**

## Performance Optimizations

- **CloudFront CDN** for fast delivery
- **WebP format** for better compression
- **Progressive loading** with previews
- **Client-side validation** before upload
- **Image optimization** and compression
- **Caching headers** (1 year)

## Mobile Support

- **Touch gestures** for cropping
- **Responsive design** for all screen sizes
- **Camera access** for direct photo capture
- **Optimized UI** for mobile devices

## Browser Support

- **Modern browsers**: Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- **Mobile browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Features**: 
  - Drag-and-drop API
  - File API
  - Canvas API
  - ES6+ JavaScript

## Troubleshooting

### Common Issues

1. **Upload fails with CORS error**
   - Check S3 bucket CORS configuration
   - Verify CloudFront distribution settings

2. **Image processing fails**
   - Verify file format is supported
   - Check file size limits
   - Review image processing logs

3. **Presigned URL expires**
   - URLs expire after 1 hour
   - Generate new URL for upload attempts

4. **Profile picture not displaying**
   - Check CDN configuration
   - Verify S3 object permissions
   - Clear browser cache

### Debug Mode

Enable debug logging by setting:

```python
import logging
logging.getLogger('services.profile').setLevel(logging.DEBUG)
```

## Future Enhancements

- **Face detection** for automatic cropping
- **Image filters** and adjustments
- **Bulk upload** for multiple profiles
- **Avatar templates** and frames
- **Social media import** functionality
- **GDPR compliance** features

## Support

For issues and questions:
1. Check application logs
2. Verify AWS configuration
3. Test with different image formats
4. Review browser console for JavaScript errors

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Dependencies**: Flask 2.2+, AWS S3, Cropper.js
