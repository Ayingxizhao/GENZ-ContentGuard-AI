"""
Gemini-specific rate limiting middleware
Enforces per-user (10/day) and global (40/day) limits
"""
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional
from flask import request

# Global limit tracking
GEMINI_GLOBAL_DAILY_LIMIT = 40
GEMINI_USER_DAILY_LIMIT = 10
GEMINI_COOLDOWN_SECONDS = 180  # 3 minutes cooldown between calls

# Cache key for global tracking
GEMINI_GLOBAL_KEY = "gemini_global_usage"

# In-memory storage for anonymous user cooldown tracking
# Structure: {ip_address: {'last_call': timestamp, 'call_count': int, 'window_start': timestamp}}
_anonymous_gemini_cooldowns = {}

# Burst allowance for anonymous users
ANONYMOUS_BURST_CALLS = 2  # Allow 2 calls before enforcing cooldown


def get_gemini_cache():
    """Get cache instance for global limit tracking"""
    from cache_service import get_cache
    return get_cache()


def check_gemini_global_limit() -> Tuple[bool, int, int, Optional[datetime]]:
    """
    Check if global Gemini daily limit has been exceeded
    
    Returns:
        Tuple of (allowed, remaining, limit, reset_time)
    """
    cache = get_gemini_cache()
    
    # Get current usage from cache
    usage_data = cache.get(GEMINI_GLOBAL_KEY)
    
    now = datetime.utcnow()
    today = now.date()
    
    if usage_data is None:
        # No usage yet today
        return True, GEMINI_GLOBAL_DAILY_LIMIT, GEMINI_GLOBAL_DAILY_LIMIT, _get_next_reset_time(now)
    
    # Check if usage data is from today
    usage_date = usage_data.get('date')
    usage_count = usage_data.get('count', 0)
    
    if usage_date != today.isoformat():
        # New day, reset counter
        return True, GEMINI_GLOBAL_DAILY_LIMIT, GEMINI_GLOBAL_DAILY_LIMIT, _get_next_reset_time(now)
    
    # Check if limit exceeded
    remaining = max(0, GEMINI_GLOBAL_DAILY_LIMIT - usage_count)
    allowed = usage_count < GEMINI_GLOBAL_DAILY_LIMIT
    
    return allowed, remaining, GEMINI_GLOBAL_DAILY_LIMIT, _get_next_reset_time(now)


def increment_gemini_global_usage() -> None:
    """Increment global Gemini usage counter"""
    cache = get_gemini_cache()
    
    now = datetime.utcnow()
    today = now.date()
    
    usage_data = cache.get(GEMINI_GLOBAL_KEY)
    
    if usage_data is None or usage_data.get('date') != today.isoformat():
        # New day or first usage
        new_data = {
            'date': today.isoformat(),
            'count': 1
        }
    else:
        # Increment existing count
        new_data = {
            'date': today.isoformat(),
            'count': usage_data.get('count', 0) + 1
        }
    
    # Cache with default TTL (cache is already configured with TTL)
    cache.set(GEMINI_GLOBAL_KEY, new_data)
    
    logging.info(f"Gemini global usage: {new_data['count']}/{GEMINI_GLOBAL_DAILY_LIMIT}")


def _get_next_reset_time(now: datetime) -> datetime:
    """Get next UTC midnight reset time"""
    tomorrow = now.date() + timedelta(days=1)
    return datetime.combine(tomorrow, datetime.min.time())


def check_user_gemini_limit(user) -> Tuple[bool, int, int]:
    """
    Check if user has exceeded their Gemini daily limit
    
    Args:
        user: User model instance
        
    Returns:
        Tuple of (allowed, remaining, limit)
    """
    if not user or not hasattr(user, 'gemini_calls_today'):
        # User not authenticated or model not updated
        return False, 0, GEMINI_USER_DAILY_LIMIT
    
    # Reset counter if new day
    now = datetime.utcnow()
    if user.last_gemini_call:
        last_call_date = user.last_gemini_call.date()
        today = now.date()
        if last_call_date < today:
            user.gemini_calls_today = 0
            from models import db
            db.session.commit()
    
    remaining = max(0, GEMINI_USER_DAILY_LIMIT - user.gemini_calls_today)
    allowed = user.gemini_calls_today < GEMINI_USER_DAILY_LIMIT
    
    return allowed, remaining, GEMINI_USER_DAILY_LIMIT


def _get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


def check_anonymous_gemini_cooldown() -> Tuple[bool, Optional[int]]:
    """
    Check cooldown for anonymous users (tracked by IP)
    Allows ANONYMOUS_BURST_CALLS before enforcing cooldown
    
    Returns:
        Tuple of (allowed, seconds_remaining)
    """
    ip = _get_client_ip()
    now = datetime.utcnow()
    
    if ip not in _anonymous_gemini_cooldowns:
        # No previous call from this IP - initialize
        _anonymous_gemini_cooldowns[ip] = {
            'last_call': now,
            'call_count': 0,
            'window_start': now
        }
        return True, None
    
    cooldown_data = _anonymous_gemini_cooldowns[ip]
    last_call = cooldown_data['last_call']
    call_count = cooldown_data.get('call_count', 0)
    window_start = cooldown_data.get('window_start', last_call)
    
    time_since_last_call = (now - last_call).total_seconds()
    time_since_window_start = (now - window_start).total_seconds()
    
    # Reset window if cooldown period has passed
    if time_since_window_start >= GEMINI_COOLDOWN_SECONDS:
        _anonymous_gemini_cooldowns[ip] = {
            'last_call': now,
            'call_count': 0,
            'window_start': now
        }
        return True, None
    
    # Allow burst calls
    if call_count < ANONYMOUS_BURST_CALLS:
        return True, None
    
    # Enforce cooldown after burst
    if time_since_window_start < GEMINI_COOLDOWN_SECONDS:
        seconds_remaining = int(GEMINI_COOLDOWN_SECONDS - time_since_window_start)
        return False, seconds_remaining
    
    # Cooldown period passed
    return True, None


def update_anonymous_gemini_cooldown() -> None:
    """Update last call timestamp and increment call count for anonymous user"""
    ip = _get_client_ip()
    now = datetime.utcnow()
    
    if ip not in _anonymous_gemini_cooldowns:
        _anonymous_gemini_cooldowns[ip] = {
            'last_call': now,
            'call_count': 1,
            'window_start': now
        }
    else:
        cooldown_data = _anonymous_gemini_cooldowns[ip]
        cooldown_data['last_call'] = now
        cooldown_data['call_count'] = cooldown_data.get('call_count', 0) + 1
    
    logging.info(f"Updated Gemini cooldown for IP: {ip}, calls: {_anonymous_gemini_cooldowns[ip]['call_count']}")


def check_user_gemini_cooldown(user) -> Tuple[bool, Optional[int]]:
    """
    Check if user needs to wait before making another Gemini API call
    Enforces 3-minute cooldown between calls
    
    Args:
        user: User model instance (can be None for anonymous users)
        
    Returns:
        Tuple of (allowed, seconds_remaining)
        - allowed: True if cooldown period has passed
        - seconds_remaining: Number of seconds to wait (None if allowed)
    """
    if not user or not hasattr(user, 'last_gemini_call'):
        # No previous call recorded, allow
        return True, None
    
    if not user.last_gemini_call:
        # First call ever, allow
        return True, None
    
    now = datetime.utcnow()
    time_since_last_call = (now - user.last_gemini_call).total_seconds()
    
    if time_since_last_call < GEMINI_COOLDOWN_SECONDS:
        # Still in cooldown period
        seconds_remaining = int(GEMINI_COOLDOWN_SECONDS - time_since_last_call)
        return False, seconds_remaining
    
    # Cooldown period passed
    return True, None


def increment_user_gemini_usage(user) -> None:
    """
    Increment user's Gemini usage counter
    
    Args:
        user: User model instance
    """
    if not user or not hasattr(user, 'gemini_calls_today'):
        return
    
    from models import db
    now = datetime.utcnow()
    
    # Reset if new day
    if user.last_gemini_call:
        last_call_date = user.last_gemini_call.date()
        today = now.date()
        if last_call_date < today:
            user.gemini_calls_today = 0
    
    user.gemini_calls_count += 1
    user.gemini_calls_today += 1
    user.last_gemini_call = now
    
    db.session.commit()
    
    logging.info(f"User {user.id} Gemini usage: {user.gemini_calls_today}/{GEMINI_USER_DAILY_LIMIT}")


def check_gemini_rate_limits(user=None) -> Tuple[bool, dict]:
    """
    Check all Gemini rate limits: cooldown, global daily limit, and user daily limit
    
    Args:
        user: Optional User model instance (for authenticated users)
        
    Returns:
        Tuple of (allowed, error_response_dict)
    """
    # Check cooldown - only for anonymous users
    # Authenticated users rely on daily limits (10/day) instead of cooldown
    if not user:
        # Anonymous user - check IP-based cooldown with burst allowance
        cooldown_allowed, seconds_remaining = check_anonymous_gemini_cooldown()
        
        if not cooldown_allowed:
            minutes_remaining = seconds_remaining // 60
            seconds_part = seconds_remaining % 60
            wait_time = f"{minutes_remaining}m {seconds_part}s" if minutes_remaining > 0 else f"{seconds_part}s"
            
            return False, {
                'error': 'Gemini API cooldown active',
                'cooldown_seconds': GEMINI_COOLDOWN_SECONDS,
                'seconds_remaining': seconds_remaining,
                'wait_time': wait_time,
                'hint': f'Please wait {wait_time} before making another Gemini API request. Sign in to remove cooldowns and get 10 requests per day.',
                'actions': {
                    'login': '/auth/login',
                    'signup': '/auth/signup'
                }
            }
    
    # Check global limit
    global_allowed, global_remaining, global_limit, reset_time = check_gemini_global_limit()
    
    if not global_allowed:
        return False, {
            'error': 'Gemini API daily limit exceeded for all users',
            'global_limit': global_limit,
            'global_remaining': 0,
            'reset_time': reset_time.isoformat() if reset_time else None,
            'hint': 'The Gemini model has reached its daily quota. Please try the ContentGuard Model or try again tomorrow.'
        }
    
    # Check user limit if authenticated
    if user:
        user_allowed, user_remaining, user_limit = check_user_gemini_limit(user)
        
        if not user_allowed:
            return False, {
                'error': 'Your daily Gemini API limit exceeded',
                'user_limit': user_limit,
                'user_remaining': 0,
                'global_remaining': global_remaining,
                'hint': f'You have used all {user_limit} Gemini requests for today. Try the ContentGuard Model or wait until tomorrow.'
            }
    
    # All limits OK - return rate limit info
    rate_limit_info = {
        'global_remaining': global_remaining,
        'global_limit': global_limit
    }
    
    if user:
        user_allowed, user_remaining, user_limit = check_user_gemini_limit(user)
        rate_limit_info['user_remaining'] = user_remaining
        rate_limit_info['user_limit'] = user_limit
    
    return True, rate_limit_info
