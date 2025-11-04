# Admin System Documentation

## Overview

The admin system provides development-only functionality for testing and debugging ContentGuard AI. It's designed to be completely safe for public GitHub repositories.

## Security Features

### 🔒 Environment-Gated Access
Admin functionality only works when:
- `FLASK_ENV=development`
- `ENABLE_ADMIN_ROUTES=true`

### 🛡️ Multiple Security Layers
1. **Environment checks** in admin routes
2. **Development-only validation** in User model methods
3. **Database-level protection** (admin creation only in dev)
4. **Safe for public repos** - no hardcoded credentials

## Setup Instructions

### 1. Environment Configuration
Add these to your local `.env` file (NEVER commit to Git):
```bash
FLASK_ENV=development
ENABLE_ADMIN_ROUTES=true
ADMIN_EMAIL=admin@test.com
ADMIN_PASSWORD=admin123
ADMIN_NAME=Test Admin
```

### 2. Database Setup
Add admin columns to your DigitalOcean database:
```sql
ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(512);
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
```

### 3. Create Admin Account
```bash
conda activate contentguard
python admin/create_admin.py
```

## Admin Features

### 🎯 Unlimited API Access
Admin users have:
- Unlimited API calls (`float('inf')`)
- Unlimited Gemini calls (`float('inf')`)
- Never exceed daily limits

### 📋 Available Routes
All admin routes require:
- `FLASK_ENV=development`
- `ENABLE_ADMIN_ROUTES=true`
- User must be logged in AND be admin

#### `/admin/test`
- **GET**: Test admin access and show features
- **Response**: Admin status and available features

#### `/admin/users`
- **GET**: List all users with pagination
- **Query params**: `page`, `per_page`
- **Response**: User list with full details

#### `/admin/stats`
- **GET**: System statistics
- **Response**: User counts, admin list, breakdown by auth type

#### `/admin/create`
- **POST**: Create new user (admin or regular)
- **Body**: `email`, `password`, `name`, `is_admin`
- **Response**: Created user details

#### `/admin/promote/<user_id>`
- **POST**: Promote user to admin
- **Response**: Updated user details

#### `/admin/demote/<user_id>`
- **POST**: Remove admin role (cannot demote self)
- **Response**: Updated user details

#### `/admin/reset-limits/<user_id>`
- **POST**: Reset daily API limits for user
- **Response**: Updated user details

## Usage Examples

### Create Admin User
```bash
# Using script (recommended)
python admin/create_admin.py

# Manual creation
python -c "
from admin.create_admin import create_admin_user
create_admin_user()
"
```

### Test Admin Access
```bash
# Start application
python run.py

# Login as admin
curl -X POST http://localhost:5000/auth/login-email \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'

# Test admin endpoint
curl -X GET http://localhost:5000/admin/test \
  -H "Authorization: Bearer <your-token>"
```

### View All Users
```bash
curl -X GET "http://localhost:5000/admin/users?page=1&per_page=10" \
  -H "Authorization: Bearer <admin-token>"
```

### Create New Admin
```bash
curl -X POST http://localhost:5000/admin/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "email": "newadmin@test.com",
    "password": "password123",
    "name": "New Admin",
    "is_admin": true
  }'
```

## Database Schema

### Users Table Additions
```sql
-- Profile picture support
profile_picture_url VARCHAR(512)

-- Admin functionality
is_admin BOOLEAN DEFAULT FALSE NOT NULL
```

## Model Changes

### User Model Enhancements
```python
# Unlimited access for admins
def get_remaining_calls(self):
    if self.is_admin:
        return float('inf')
    return max(0, self.daily_limit - self.api_calls_today)

# Development-only admin methods
def make_admin(self):
    if os.getenv('FLASK_ENV', '').lower() != 'development':
        raise RuntimeError("Admin creation only allowed in development")
    self.is_admin = True
    db.session.commit()
```

## Security Considerations

### ✅ Safe for Public GitHub
- No hardcoded credentials
- Environment-gated functionality
- Development-only checks
- No production admin access

### ⚠️ Important Notes
1. **Never commit `.env` file** - contains admin credentials
2. **Only use in development** - production checks prevent usage
3. **Database security** - still need database access to create admins
4. **Admin accounts** - stored in database, not code

### 🚫 Production Protection
Admin functionality automatically disabled in production because:
- `FLASK_ENV` typically set to `production`
- `ENABLE_ADMIN_ROUTES` not set (defaults to disabled)
- Multiple runtime checks prevent admin operations

## Troubleshooting

### Admin Routes Not Working
```bash
# Check environment variables
echo $FLASK_ENV
echo $ENABLE_ADMIN_ROUTES

# Should output:
# development
# true
```

### Admin Creation Fails
```bash
# Verify development environment
python -c "
import os
print('FLASK_ENV:', os.getenv('FLASK_ENV'))
print('ENABLE_ADMIN_ROUTES:', os.getenv('ENABLE_ADMIN_ROUTES'))
"
```

### Database Column Errors
```sql
-- Check if columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'users' AND column_name IN ('profile_picture_url', 'is_admin');
```

## File Structure
```
admin/
├── __init__.py           # Package initialization and security checks
├── admin_routes.py       # Admin API endpoints (dev only)
├── create_admin.py       # Admin creation script (dev only)
└── docs/
    └── admin.md          # This documentation
```

## Best Practices

1. **Use only for testing** - Not for production admin panels
2. **Keep credentials local** - Never commit admin credentials
3. **Test security** - Verify admin routes disabled in production
4. **Document usage** - Keep team informed about admin procedures
5. **Regular cleanup** - Remove test admin accounts when done

---

**Last Updated**: November 2025  
**Environment**: Development Only  
**Security**: Safe for Public Repositories
