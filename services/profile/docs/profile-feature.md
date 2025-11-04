# Profile Picture Feature Documentation

## Overview
ContentGuard AI includes a complete profile picture upload system with circular cropping, multiple size generation, and AWS S3 storage integration.

## Architecture

### Backend Components
- **`models.py`**: User model with `profile_picture_url` field and admin unlimited API access
- **`routes/profile/upload.py`**: API endpoints for upload and validation
- **`routes/profile/management.py`**: Profile picture management endpoints
- **`services/profile/`**: Core service layer
  - **`profile_service.py`**: Main orchestration service
  - **`storage_handler.py`**: AWS S3 operations
  - **`image_processor.py`**: Image processing and validation

### Architecture Implementation Details

#### 1. **Service Layer Pattern**
The system uses a **3-tier service architecture**:

```
Routes (API Layer) → Services (Business Logic) → Handlers (Data Access)
```

**Why this works:**
- **Separation of concerns**: Each layer has a single responsibility
- **Testability**: Services can be tested independently
- **Reusability**: Storage handler can be used by other features

#### 2. **Image Processing Pipeline**

**Step-by-step flow:**
```python
# 1. File Upload (upload.py)
file = request.files['file']
file_data = file.read()

# 2. Validation (image_processor.py)
is_valid, message = ImageProcessor.validate_file(file_data, filename)

# 3. Processing (image_processor.py) 
success, processed_images = ImageProcessor.process_profile_picture(
    file_data, crop_coords
)
# Returns: {'small': bytes, 'medium': bytes, 'large': bytes}

# 4. Storage (storage_handler.py)
success, urls = StorageHandler.upload_multiple_sizes(user_id, processed_images)
# Returns: {'thumbnail': 's3://...', 'medium': 's3://...', 'original': 's3://...'}

# 5. Database Update (profile_service.py)
profile_service.update_user_profile_url(user_id, urls)
```

#### 3. **Circular Cropping Achievement**

**Technical implementation:**
```python
def apply_circular_crop(image, crop_coords):
    # Create circular mask using numpy arrays
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw white circle on black background
    draw.ellipse([0, 0, image.size[0], image.size[1]], fill=255)
    
    # Apply mask to image
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0))
    result.putalpha(mask)
    
    return result
```

#### 4. **S3 Storage Strategy**

**Folder structure achievement:**
```python
def generate_file_key(user_id, size):
    """Generate unique S3 key with user-based organization"""
    import uuid
    file_uuid = str(uuid.uuid4())
    return f"profile-pictures/{user_id}/{size}/{file_uuid}.webp"
```

**Benefits:**
- **Scalability**: 10,000 users × 3 sizes = 30,000 files, well organized
- **Security**: User isolation prevents access to other users' files
- **Cleanup**: Easy to delete all files for a user: `delete_prefix(f"profile-pictures/{user_id}/")`

#### 5. **Frontend State Management**

**Component-based approach:**
```javascript
class ProfilePictureUpload {
    constructor(options) {
        this.currentFile = null;     // File state
        this.cropper = null;         // Cropper instance
        this.isUploading = false;    // Upload state
    }
    
    handleFileSelect(file) {
        this.currentFile = file;     // Update state
        this.showPreview(file);      // UI update
        this.autoUpload();           // Trigger upload
    }
}
```

#### 6. **Cache-Busting Strategy**

**Problem**: Browser caches old profile pictures
**Solution**: URL-based cache invalidation
```javascript
const imageUrl = user.profile_picture_url;
const urlWithTimestamp = imageUrl.includes('profile-pictures') 
    ? `${imageUrl}?t=${Date.now()}`  // Add timestamp to break cache
    : imageUrl;
```

#### 7. **Admin Security Architecture**

**Multi-layer security:**
```python
def create_admin_user(cls, email, password, name):
    # Layer 1: Environment check
    if os.getenv('FLASK_ENV', '').lower() != 'development':
        raise RuntimeError("Admin creation only allowed in development")
    
    # Layer 2: Feature flag check  
    if os.getenv('ENABLE_ADMIN_ROUTES', '').lower() != 'true':
        raise RuntimeError("Admin routes disabled")
    
    # Layer 3: Database-level protection
    user = cls(email=email, is_admin=True, ...)
```

#### 8. **Error Propagation Pattern**

**Consistent error handling:**
```python
# Service layer returns consistent tuple format
def upload_profile_picture(user_id, file, crop_coords):
    try:
        # ... processing logic ...
        return True, {"urls": urls, "message": "Success"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return False, {"error": "Upload failed"}

# Route layer handles the response
success, result = profile_service.upload_profile_picture(...)
if success:
    return jsonify(result), 200
else:
    return jsonify(result), 400
```

#### 9. **Database Schema Achievement**

**Minimal but effective:**
```sql
-- Single field stores the medium size URL (used for display)
ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(512);

-- Admin functionality for testing
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
```

**Why single field?**
- **Simplicity**: Don't need to store all 3 URLs in database
- **Flexibility**: Other sizes can be derived from the medium URL
- **Performance**: Faster queries with single indexed field

#### 10. **Integration Points**

**How it connects to existing system:**
```python
# 1. Auth integration (auth.py)
def login_email():
    # Add profile_picture_url to login response
    return jsonify({
        "user": current_user.to_dict(),  # Includes profile_picture_url
        "redirect_to_profile": not current_user.profile_picture_url
    })

# 2. Main UI integration (index.html)
// JavaScript prioritizes uploaded picture over OAuth avatar
const imageUrl = user.profile_picture_url || user.avatar_url;

# 3. Admin system integration (admin_routes.py)
// Admin users get unlimited API access for testing
if current_user.is_admin:
    return 999999  // Instead of float('inf')
```

### Key Architectural Decisions

1. **Service Layer**: Enables testing and reusability
2. **Component-Based Frontend**: Maintainable and modular
3. **S3 for Storage**: Scalable and cost-effective
4. **WebP Format**: Better compression than JPEG/PNG
5. **Circular Cropping**: Modern social media style
6. **Cache-Busting**: Prevents stale avatar issues
7. **Environment-Gated Admin**: Safe for public repositories

### Frontend Components
- **`templates/profile/upload.html`**: Upload interface with drag-and-drop
- **`templates/profile/crop.html`**: Circular cropping interface
- **`static/profile/js/upload.js`**: Upload handling and validation
- **`static/profile/js/cropper.js`**: Advanced cropping functionality
- **`static/profile/css/profile.css`**: Responsive styling

## Features

### Upload Process
1. **File Selection**: Drag-and-drop or click to select
2. **Validation**: File type (JPEG/PNG/WebP) and size (5MB max) checks
3. **Preview**: Real-time image preview with circular mask
4. **Cropping**: Circular crop with adjustable controls
5. **Processing**: Automatic resizing to multiple sizes
6. **Storage**: Upload to AWS S3 with organized folder structure

### Generated Sizes
- **Thumbnail**: 150x150px (for UI avatars)
- **Medium**: 300x300px (for profile views)
- **Original**: 1200x1200px (for high-res display)

### Storage Structure
```
s3://your-bucket/profile-pictures/
├── {user_id}/
│   ├── thumbnail/{uuid}.webp
│   ├── medium/{uuid}.webp
│   └── original/{uuid}.webp
```

## API Endpoints

### Upload Endpoints
- `POST /api/profile/upload` - Upload and process profile picture
- `POST /api/profile/validate` - Validate file before upload
- `GET /api/profile/status` - Get current profile picture status
- `DELETE /api/profile/delete` - Remove profile picture

### Management Endpoints
- `GET /profile/upload` - Profile upload page
- `GET /profile/crop` - Image cropping interface

## Security Features

### Access Control
- **Authentication Required**: All endpoints require login
- **CSRF Protection**: All forms protected with CSRF tokens
- **File Validation**: Server-side file type and size validation
- **Admin Controls**: Admin users have unlimited API access for testing

### Safe for Public Repositories
- **Environment Gated**: Admin functionality only in development
- **No Hardcoded Credentials**: All AWS config via environment variables
- **Input Sanitization**: All user inputs validated and sanitized

## Configuration

### Environment Variables
```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
AWS_CLOUDFRONT_DOMAIN=your-cdn.domain.com  # Optional

# Profile Settings
PROFILE_MAX_FILE_SIZE=5242880
PROFILE_ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
```

### Database Schema
```sql
ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(512);
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
```

## User Interface Integration

### Navigation Access
- **Desktop**: User dropdown → "Profile Picture" option
- **Mobile**: Side menu → "Profile Picture" button
- **Direct**: `/profile/upload` URL

### Avatar Display
- **Priority**: Uploaded profile picture > OAuth avatar > Generated initials
- **Cache Busting**: Timestamps prevent browser caching issues
- **Responsive**: Works across all device sizes

## Admin Features

### Development-Only Admin System
- **Unlimited API Access**: 999,999 calls per day for testing
- **User Management**: Create, promote, and manage admin accounts
- **Usage Statistics**: Complete system usage monitoring
- **Security**: Environment-gated, safe for public GitHub

### Admin Account Creation
```bash
# Set environment variables
export FLASK_ENV=development
export ENABLE_ADMIN_ROUTES=true

# Create admin account
python admin/create_admin.py
```

## Technical Implementation

### Image Processing Pipeline
1. **Validation**: Check file type, size, and format
2. **Resizing**: Generate multiple sizes using Pillow
3. **Circular Mask**: Apply circular cropping with anti-aliasing
4. **Format Conversion**: Convert to WebP for optimal compression
5. **Quality Optimization**: Balance quality and file size

### S3 Storage Features
- **Automatic Cleanup**: Delete old images when uploading new ones
- **Unique Filenames**: UUID-based naming prevents collisions
- **Organized Structure**: User-based folder organization
- **Public Access**: Configurable bucket permissions

### Error Handling
- **Client-Side**: Real-time validation and user feedback
- **Server-Side**: Comprehensive logging and error responses
- **Graceful Degradation**: Fallback to default avatars on errors

## Usage Examples

### Basic Upload
```javascript
// Handled automatically by ProfilePictureUpload class
const uploader = new ProfilePictureUpload({
    uploadUrl: '/api/profile/upload',
    onSuccess: (message, data) => {
        console.log('Upload successful:', data.urls);
    }
});
```

### Admin Account Testing
```bash
# Login with admin credentials
Email: admin@test.com
Password: admin123

# Test admin features
curl -X GET http://localhost:5001/admin/test \
  -H "Authorization: Bearer <admin-token>"
```

## Troubleshooting

### Common Issues
1. **Upload Fails**: Check AWS credentials and bucket permissions
2. **Images Not Showing**: Verify S3 bucket public access settings
3. **Avatar Not Updating**: Clear browser cache or check `profile_picture_url` field
4. **Admin Access Denied**: Ensure `FLASK_ENV=development` and `ENABLE_ADMIN_ROUTES=true`

### Debug Logging
```python
# Backend logs show detailed upload process
print(f"*** UPLOAD RESULT: success={success}, result={result}")

# Frontend console shows upload progress
console.log('Starting upload for file:', file.name);
```

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Environment**: Development & Production Ready
