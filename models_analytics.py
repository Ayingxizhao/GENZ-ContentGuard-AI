"""
Access logging models for user analytics
Tracks unique user visits, endpoint usage, and activity patterns
"""
from datetime import datetime, timedelta
from models import db
import hashlib


class AccessLog(db.Model):
    """
    Logs every request to the service for analytics
    Tracks both authenticated users and anonymous visitors (by hashed IP)
    """
    __tablename__ = 'access_logs'

    id = db.Column(db.Integer, primary_key=True)

    # User identification (one will be populated)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_hash = db.Column(db.String(64), nullable=True, index=True)  # SHA256 hash of IP for privacy

    # Request details
    endpoint = db.Column(db.String(255), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, etc.
    status_code = db.Column(db.Integer, nullable=True)

    # User agent details
    user_agent = db.Column(db.String(512), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # mobile, tablet, pc, bot

    # Performance tracking
    response_time_ms = db.Column(db.Integer, nullable=True)  # Response time in milliseconds

    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_user_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_ip_timestamp', 'ip_hash', 'timestamp'),
        db.Index('idx_endpoint_timestamp', 'endpoint', 'timestamp'),
        db.Index('idx_timestamp_desc', timestamp.desc()),
    )

    def __repr__(self):
        user_info = f"user:{self.user_id}" if self.user_id else f"ip:{self.ip_hash[:8]}..."
        return f'<AccessLog {user_info} {self.method} {self.endpoint} at {self.timestamp}>'

    @staticmethod
    def hash_ip(ip_address):
        """
        Hash IP address with SHA256 for privacy-preserving analytics
        """
        if not ip_address:
            return None
        return hashlib.sha256(ip_address.encode('utf-8')).hexdigest()

    @classmethod
    def log_access(cls, user_id=None, ip_address=None, endpoint=None, method='GET',
                   status_code=None, user_agent_string=None, response_time_ms=None):
        """
        Create and save an access log entry

        Args:
            user_id: Authenticated user ID (if logged in)
            ip_address: Client IP address (will be hashed)
            endpoint: Route endpoint (e.g., /analyze, /health)
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP response status code
            user_agent_string: Raw User-Agent header
            response_time_ms: Response time in milliseconds

        Returns:
            AccessLog instance
        """
        from user_agents import parse

        # Parse user agent
        browser, browser_version, os, device_type = None, None, None, None
        if user_agent_string:
            try:
                ua = parse(user_agent_string)
                browser = ua.browser.family
                browser_version = ua.browser.version_string
                os = ua.os.family

                # Determine device type
                if ua.is_bot:
                    device_type = 'bot'
                elif ua.is_mobile:
                    device_type = 'mobile'
                elif ua.is_tablet:
                    device_type = 'tablet'
                else:
                    device_type = 'pc'
            except Exception as e:
                # If parsing fails, just store raw user agent
                import logging
                logging.warning(f"Failed to parse user agent: {str(e)}")

        # Hash IP address for privacy
        ip_hash = cls.hash_ip(ip_address) if ip_address else None

        # Create log entry
        log = cls(
            user_id=user_id,
            ip_hash=ip_hash,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            user_agent=user_agent_string[:512] if user_agent_string else None,
            browser=browser,
            browser_version=browser_version,
            os=os,
            device_type=device_type,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow()
        )

        db.session.add(log)
        db.session.commit()

        return log

    @classmethod
    def cleanup_old_logs(cls, retention_days=365):
        """
        Delete access logs older than retention period

        Args:
            retention_days: Number of days to retain logs (default: 365 = 1 year)

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted = cls.query.filter(cls.timestamp < cutoff_date).delete()
        db.session.commit()

        import logging
        logging.info(f"Cleaned up {deleted} access logs older than {retention_days} days")

        return deleted

    def to_dict(self):
        """Convert access log to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_hash': self.ip_hash[:8] + '...' if self.ip_hash else None,  # Partial hash for display
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'os': self.os,
            'device_type': self.device_type,
            'response_time_ms': self.response_time_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
