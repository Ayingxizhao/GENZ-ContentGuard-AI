"""
Access logging middleware
Automatically logs all requests for analytics and unique user tracking
"""
from flask import request, g
from flask_login import current_user
import time
import logging


def _get_client_ip():
    """
    Get client IP address from request
    Handles proxy headers (X-Forwarded-For) for deployments behind reverse proxies
    """
    if request.headers.get('X-Forwarded-For'):
        # Get first IP in chain (original client)
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip


def init_access_logging(app):
    """
    Initialize access logging middleware for Flask app

    Automatically logs:
    - User ID (if authenticated) or hashed IP (if anonymous)
    - Endpoint accessed
    - HTTP method and status code
    - User agent details (browser, OS, device)
    - Response time

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request_logger():
        """
        Record request start time
        """
        g.request_start_time = time.time()

    @app.after_request
    def after_request_logger(response):
        """
        Log access after request is processed
        """
        try:
            # Skip logging for static files and health checks
            if request.endpoint in ['static', 'health']:
                return response

            # Calculate response time
            response_time_ms = None
            if hasattr(g, 'request_start_time'):
                response_time_ms = int((time.time() - g.request_start_time) * 1000)

            # Get user identification
            user_id = current_user.id if current_user.is_authenticated else None
            ip_address = _get_client_ip() if not user_id else None

            # Get request details
            endpoint = request.endpoint or request.path
            method = request.method
            status_code = response.status_code
            user_agent = request.headers.get('User-Agent')

            # Log access (async in production, sync for now given low traffic)
            from models_analytics import AccessLog
            AccessLog.log_access(
                user_id=user_id,
                ip_address=ip_address,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                user_agent_string=user_agent,
                response_time_ms=response_time_ms
            )

            # Log to console for debugging
            user_info = f"user:{user_id}" if user_id else f"anon:{ip_address}"
            logging.info(
                f"ACCESS: {user_info} {method} {endpoint} "
                f"-> {status_code} ({response_time_ms}ms)"
            )

        except Exception as e:
            # Don't break the response if logging fails
            logging.error(f"Access logging failed: {str(e)}")

        return response

    logging.info("Access logging middleware initialized")
