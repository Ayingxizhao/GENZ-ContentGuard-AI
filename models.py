"""
Database models for ContentGuard AI
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for OAuth and email/password authentication with usage tracking"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)
    profile_picture_url = db.Column(db.String(512), nullable=True)

    # Email/password authentication
    password_hash = db.Column(db.String(255), nullable=True)

    # OAuth provider info (nullable for email/password users)
    provider = db.Column(db.String(50), nullable=True)  # 'google', 'github', or None for email/password
    provider_user_id = db.Column(db.String(255), nullable=True)

    # Usage tracking
    api_calls_count = db.Column(db.Integer, default=0, nullable=False)
    api_calls_today = db.Column(db.Integer, default=0, nullable=False)
    last_api_call = db.Column(db.DateTime, nullable=True)
    daily_limit = db.Column(db.Integer, default=200, nullable=False)  # 200 calls/day for authenticated users
    
    # Gemini-specific usage tracking
    gemini_calls_count = db.Column(db.Integer, default=0, nullable=False)
    gemini_calls_today = db.Column(db.Integer, default=0, nullable=False)
    last_gemini_call = db.Column(db.DateTime, nullable=True)
    gemini_daily_limit = db.Column(db.Integer, default=10, nullable=False)  # 10 Gemini calls/day

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Admin role (development only)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Unique constraint on provider + provider_user_id (only for OAuth users)
    __table_args__ = (
        db.Index('idx_provider_user', 'provider', 'provider_user_id'),
    )
    
    def __repr__(self):
        return f'<User {self.email} ({self.provider})>'

    def set_password(self, password):
        """Hash and set user password (for email/password authentication)"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(cls, email, password=None, name=None, provider=None, provider_user_id=None, avatar_url=None):
        """Create a new user (email/password or OAuth)"""
        user = cls(
            email=email,
            name=name,
            provider=provider,
            provider_user_id=provider_user_id,
            avatar_url=avatar_url,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        if password:
            user.set_password(password)
        return user

    def increment_api_usage(self):
        """Increment API usage counter and check if limit exceeded"""
        now = datetime.utcnow()
        
        # Reset daily counter if it's a new day
        if self.last_api_call:
            last_call_date = self.last_api_call.date()
            today = now.date()
            if last_call_date < today:
                self.api_calls_today = 0
        
        self.api_calls_count += 1
        self.api_calls_today += 1
        self.last_api_call = now
        db.session.commit()
        # Refresh to ensure we have the latest values
        db.session.refresh(self)
    
    def has_exceeded_daily_limit(self):
        """Check if user has exceeded their daily API limit (never for admins)"""
        if self.is_admin:
            return False  # Admins never exceed limits
        return self.api_calls_today >= self.daily_limit
    
    def get_remaining_calls(self):
        """Get remaining API calls for today (unlimited for admins)"""
        if self.is_admin:
            return 999999  # Unlimited for admins (JSON-serializable)
        return max(0, self.daily_limit - self.api_calls_today)
    
    def get_remaining_gemini_calls(self):
        """Get remaining Gemini API calls for today (unlimited for admins)"""
        if self.is_admin:
            return 999999  # Unlimited for admins (JSON-serializable)
        return max(0, self.gemini_daily_limit - self.gemini_calls_today)
    
    def has_exceeded_gemini_limit(self):
        """Check if user has exceeded their daily Gemini limit (never for admins)"""
        if self.is_admin:
            return False  # Admins never exceed limits
        return self.gemini_calls_today >= self.gemini_daily_limit
    
    def get_usage_percentage(self, model='huggingface'):
        """Get usage percentage for a specific model"""
        if model == 'gemini':
            if self.gemini_daily_limit == 0:
                return 0
            return (self.gemini_calls_today / self.gemini_daily_limit) * 100
        else:
            if self.daily_limit == 0:
                return 0
            return (self.api_calls_today / self.daily_limit) * 100
    
    def get_reset_time(self):
        """Get the time when daily limits reset (tomorrow midnight UTC)"""
        from datetime import timedelta
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return tomorrow
    
    def get_seconds_until_reset(self):
        """Get seconds until daily limit reset"""
        reset_time = self.get_reset_time()
        now = datetime.utcnow()
        delta = reset_time - now
        return max(0, int(delta.total_seconds()))
    
    def make_admin(self):
        """Promote user to admin role (development only)"""
        import os
        if os.getenv('FLASK_ENV', '').lower() != 'development':
            raise RuntimeError("Admin creation only allowed in development")
        self.is_admin = True
        db.session.commit()
    
    def remove_admin(self):
        """Remove admin role from user (development only)"""
        import os
        if os.getenv('FLASK_ENV', '').lower() != 'development':
            raise RuntimeError("Admin modification only allowed in development")
        self.is_admin = False
        db.session.commit()
    
    @classmethod
    def get_admins(cls):
        """Get all admin users (development only)"""
        import os
        if os.getenv('FLASK_ENV', '').lower() != 'development':
            return []
        return cls.query.filter_by(is_admin=True).all()
    
    @classmethod
    def create_admin_user(cls, email, password=None, name=None):
        """Create a new admin user (development only)"""
        import os
        if os.getenv('FLASK_ENV', '').lower() != 'development':
            raise RuntimeError("Admin creation only allowed in development")
        
        user = cls(
            email=email,
            name=name or 'Admin',
            is_admin=True,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        if password:
            user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def get_detailed_usage_stats(self):
        """Get comprehensive usage statistics for both models"""
        now = datetime.utcnow()
        
        # Check if we need to reset daily counters
        if self.last_api_call:
            last_call_date = self.last_api_call.date()
            today = now.date()
            if last_call_date < today:
                self.api_calls_today = 0
        
        if self.last_gemini_call:
            last_call_date = self.last_gemini_call.date()
            today = now.date()
            if last_call_date < today:
                self.gemini_calls_today = 0
        
        reset_time = self.get_reset_time()
        seconds_until_reset = self.get_seconds_until_reset()
        
        return {
            'user_id': self.id,
            'email': self.email,
            'huggingface': {
                'calls_today': self.api_calls_today,
                'daily_limit': self.daily_limit,
                'remaining': self.get_remaining_calls(),
                'total_calls': self.api_calls_count,
                'percentage_used': round(self.get_usage_percentage('huggingface'), 1),
                'last_call': self.last_api_call.isoformat() if self.last_api_call else None
            },
            'gemini': {
                'calls_today': self.gemini_calls_today,
                'daily_limit': self.gemini_daily_limit,
                'remaining': self.get_remaining_gemini_calls(),
                'total_calls': self.gemini_calls_count,
                'percentage_used': round(self.get_usage_percentage('gemini'), 1),
                'last_call': self.last_gemini_call.isoformat() if self.last_gemini_call else None
            },
            'reset_time': reset_time.isoformat(),
            'seconds_until_reset': seconds_until_reset,
            'has_exceeded_hf_limit': self.has_exceeded_daily_limit(),
            'has_exceeded_gemini_limit': self.has_exceeded_gemini_limit()
        }
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'profile_picture_url': self.profile_picture_url,
            'provider': self.provider,
            'is_admin': self.is_admin,
            'api_calls_count': self.api_calls_count,
            'api_calls_today': self.api_calls_today,
            'daily_limit': self.daily_limit,
            'remaining_calls': self.get_remaining_calls(),
            'gemini_calls_count': self.gemini_calls_count,
            'gemini_calls_today': self.gemini_calls_today,
            'gemini_daily_limit': self.gemini_daily_limit,
            'remaining_gemini_calls': self.get_remaining_gemini_calls(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
