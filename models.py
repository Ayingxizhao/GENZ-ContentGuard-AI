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

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

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
    
    def has_exceeded_daily_limit(self):
        """Check if user has exceeded their daily API limit"""
        return self.api_calls_today >= self.daily_limit
    
    def get_remaining_calls(self):
        """Get remaining API calls for today"""
        return max(0, self.daily_limit - self.api_calls_today)
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'provider': self.provider,
            'api_calls_count': self.api_calls_count,
            'api_calls_today': self.api_calls_today,
            'daily_limit': self.daily_limit,
            'remaining_calls': self.get_remaining_calls(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
