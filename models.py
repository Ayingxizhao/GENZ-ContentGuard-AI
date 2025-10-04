"""
Database models for ContentGuard AI
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for OAuth authentication and usage tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)
    
    # OAuth provider info
    provider = db.Column(db.String(50), nullable=False)  # 'google' or 'github'
    provider_user_id = db.Column(db.String(255), nullable=False)
    
    # Usage tracking
    api_calls_count = db.Column(db.Integer, default=0, nullable=False)
    api_calls_today = db.Column(db.Integer, default=0, nullable=False)
    last_api_call = db.Column(db.DateTime, nullable=True)
    daily_limit = db.Column(db.Integer, default=100, nullable=False)  # 100 calls/day default
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint on provider + provider_user_id
    __table_args__ = (
        db.UniqueConstraint('provider', 'provider_user_id', name='unique_provider_user'),
    )
    
    def __repr__(self):
        return f'<User {self.email} ({self.provider})>'
    
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
