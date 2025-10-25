"""
API Usage Statistics Routes
Provides detailed usage information for authenticated and anonymous users
Borrowed from Flask best practices for API design
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging

usage_bp = Blueprint('usage', __name__, url_prefix='/api/usage')


@usage_bp.route('', methods=['GET'])
def get_usage_stats():
    """
    Get detailed API usage statistics
    Returns different data based on authentication status:
    - Authenticated users: Full breakdown of HuggingFace and Gemini usage
    - Anonymous users: IP-based rate limit information
    """
    if current_user.is_authenticated:
        # Return detailed stats for authenticated users
        try:
            stats = current_user.get_detailed_usage_stats()
            return jsonify({
                'authenticated': True,
                'stats': stats
            }), 200
        except Exception as e:
            logging.error(f"Error getting user stats: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve usage statistics',
                'hint': 'Please try again later'
            }), 500
    else:
        # Return anonymous user stats (IP-based)
        from middleware.rate_limit import get_anonymous_usage_info, check_anonymous_rate_limit
        from middleware.gemini_rate_limit import check_anonymous_gemini_cooldown, GEMINI_COOLDOWN_SECONDS
        
        try:
            # Get HuggingFace rate limit info
            hf_info = get_anonymous_usage_info()
            
            # Get Gemini cooldown info
            gemini_allowed, seconds_remaining = check_anonymous_gemini_cooldown()
            
            # Calculate reset time for anonymous users (daily reset)
            now = datetime.utcnow()
            reset_time = datetime(now.year, now.month, now.day) + timedelta(days=1)
            seconds_until_reset = max(0, int((reset_time - now).total_seconds()))
            
            return jsonify({
                'authenticated': False,
                'stats': {
                    'ip': hf_info['ip'],
                    'huggingface': {
                        'calls_today': hf_info['usage'],
                        'daily_limit': hf_info['limit'],
                        'remaining': hf_info['remaining'],
                        'percentage_used': round((hf_info['usage'] / hf_info['limit']) * 100, 1) if hf_info['limit'] > 0 else 0
                    },
                    'gemini': {
                        'cooldown_active': not gemini_allowed,
                        'cooldown_seconds': GEMINI_COOLDOWN_SECONDS,
                        'seconds_remaining': seconds_remaining if not gemini_allowed else 0,
                        'hint': 'Sign in to get 10 Gemini requests per day without cooldown'
                    },
                    'reset_time': reset_time.isoformat(),
                    'seconds_until_reset': seconds_until_reset,
                    'upgrade_hint': 'Sign in for 200 HuggingFace requests and 10 Gemini requests per day'
                }
            }), 200
        except Exception as e:
            logging.error(f"Error getting anonymous stats: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve usage statistics',
                'hint': 'Please try again later'
            }), 500


@usage_bp.route('/summary', methods=['GET'])
@login_required
def get_usage_summary():
    """
    Get a quick summary of usage for authenticated users
    Useful for displaying in UI headers/dropdowns
    """
    try:
        return jsonify({
            'huggingface': {
                'used': current_user.api_calls_today,
                'limit': current_user.daily_limit,
                'remaining': current_user.get_remaining_calls()
            },
            'gemini': {
                'used': current_user.gemini_calls_today,
                'limit': current_user.gemini_daily_limit,
                'remaining': current_user.get_remaining_gemini_calls()
            },
            'seconds_until_reset': current_user.get_seconds_until_reset()
        }), 200
    except Exception as e:
        logging.error(f"Error getting usage summary: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve usage summary'
        }), 500


@usage_bp.route('/history', methods=['GET'])
@login_required
def get_usage_history():
    """
    Get historical usage data for authenticated users
    Returns total lifetime usage across both models
    """
    try:
        return jsonify({
            'user_id': current_user.id,
            'email': current_user.email,
            'total_usage': {
                'huggingface': current_user.api_calls_count,
                'gemini': current_user.gemini_calls_count,
                'combined': current_user.api_calls_count + current_user.gemini_calls_count
            },
            'account_created': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_hf_call': current_user.last_api_call.isoformat() if current_user.last_api_call else None,
            'last_gemini_call': current_user.last_gemini_call.isoformat() if current_user.last_gemini_call else None
        }), 200
    except Exception as e:
        logging.error(f"Error getting usage history: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve usage history'
        }), 500
