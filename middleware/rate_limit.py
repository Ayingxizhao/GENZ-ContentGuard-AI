"""
Rate limiting middleware for anonymous users
Tracks API usage by IP address with daily limits
Borrowed from Flask-Limiter patterns
"""
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
import logging

# In-memory storage for anonymous user rate limiting
# Structure: {ip_address: {'count': int, 'reset_time': datetime}}
_anonymous_limits = {}

# Anonymous user daily limit
ANONYMOUS_DAILY_LIMIT = 100


def _get_client_ip():
    """
    Get client IP address from request
    Handles proxy headers (X-Forwarded-For)
    """
    if request.headers.get('X-Forwarded-For'):
        # Get first IP in chain (original client)
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip


def _cleanup_expired_limits():
    """Remove expired entries from anonymous limits dict"""
    now = datetime.utcnow()
    expired_ips = [
        ip for ip, data in _anonymous_limits.items()
        if data['reset_time'] < now
    ]
    for ip in expired_ips:
        del _anonymous_limits[ip]


def check_anonymous_rate_limit():
    """
    Check if anonymous user (by IP) has exceeded daily limit
    Returns: (allowed: bool, remaining: int, limit: int, reset_time: datetime)
    """
    ip = _get_client_ip()
    now = datetime.utcnow()

    # Cleanup expired entries periodically
    _cleanup_expired_limits()

    # Get or create limit entry for this IP
    if ip not in _anonymous_limits:
        # First request from this IP today
        reset_time = datetime(now.year, now.month, now.day) + timedelta(days=1)
        _anonymous_limits[ip] = {
            'count': 0,
            'reset_time': reset_time
        }

    limit_data = _anonymous_limits[ip]

    # Check if limit period has reset
    if now >= limit_data['reset_time']:
        # Reset counter for new day
        reset_time = datetime(now.year, now.month, now.day) + timedelta(days=1)
        limit_data['count'] = 0
        limit_data['reset_time'] = reset_time

    # Check if limit exceeded
    allowed = limit_data['count'] < ANONYMOUS_DAILY_LIMIT
    remaining = max(0, ANONYMOUS_DAILY_LIMIT - limit_data['count'])

    return allowed, remaining, ANONYMOUS_DAILY_LIMIT, limit_data['reset_time']


def increment_anonymous_usage():
    """Increment usage count for current IP"""
    ip = _get_client_ip()
    now = datetime.utcnow()
    
    # Ensure IP entry exists
    if ip not in _anonymous_limits:
        reset_time = datetime(now.year, now.month, now.day) + timedelta(days=1)
        _anonymous_limits[ip] = {
            'count': 0,
            'reset_time': reset_time
        }
        logging.warning(f"[Rate Limit] IP {ip} not in limits dict, creating entry")
    
    # Check if we need to reset
    if now >= _anonymous_limits[ip]['reset_time']:
        reset_time = datetime(now.year, now.month, now.day) + timedelta(days=1)
        _anonymous_limits[ip]['count'] = 0
        _anonymous_limits[ip]['reset_time'] = reset_time
        logging.info(f"[Rate Limit] Reset counter for {ip}")
    
    # Increment
    _anonymous_limits[ip]['count'] += 1
    logging.info(f"[Rate Limit] Anonymous request from {ip}: {_anonymous_limits[ip]['count']}/{ANONYMOUS_DAILY_LIMIT}")


def anonymous_rate_limit(f):
    """
    Decorator to enforce rate limiting on anonymous users
    Should be applied to API endpoints that need rate limiting
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        # Skip rate limiting for authenticated users (they have their own limits)
        if current_user.is_authenticated:
            return f(*args, **kwargs)

        # Check anonymous rate limit
        allowed, remaining, limit, reset_time = check_anonymous_rate_limit()

        if not allowed:
            # Limit exceeded - return error with login prompt
            return jsonify({
                'error': 'Daily API limit exceeded for anonymous users',
                'daily_limit': limit,
                'remaining': 0,
                'reset_time': reset_time.isoformat(),
                'hint': 'Sign in for 200 requests per day',
                'actions': {
                    'login': '/auth/login',
                    'signup': '/auth/signup'
                }
            }), 429

        # Increment usage counter
        increment_anonymous_usage()

        # Add rate limit info to response headers
        response = f(*args, **kwargs)

        # If response is a tuple (response, status_code), handle it
        if isinstance(response, tuple):
            resp_obj, status_code = response[0], response[1]
        else:
            resp_obj, status_code = response, 200

        # Add rate limit headers if response is JSON-like
        if hasattr(resp_obj, 'headers'):
            resp_obj.headers['X-RateLimit-Limit'] = str(limit)
            resp_obj.headers['X-RateLimit-Remaining'] = str(remaining - 1)
            resp_obj.headers['X-RateLimit-Reset'] = reset_time.isoformat()

        return resp_obj if not isinstance(response, tuple) else (resp_obj, status_code)

    return decorated_function


def get_anonymous_usage_info():
    """
    Get current anonymous user's usage info
    Returns: dict with usage statistics
    """
    ip = _get_client_ip()
    allowed, remaining, limit, reset_time = check_anonymous_rate_limit()

    usage = _anonymous_limits.get(ip, {}).get('count', 0)
    
    logging.info(f"[Rate Limit] get_anonymous_usage_info for {ip}: usage={usage}, remaining={remaining}")
    logging.debug(f"[Rate Limit] Full limits dict: {_anonymous_limits}")

    return {
        'ip': ip,
        'usage': usage,
        'limit': limit,
        'remaining': remaining,
        'reset_time': reset_time.isoformat()
    }
