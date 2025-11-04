"""
Admin Routes for ContentGuard AI

Development-only admin routes for testing and debugging.
These routes are only loaded when ENABLE_ADMIN_ROUTES=true and FLASK_ENV=development.
"""

import os
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User
from . import is_admin_enabled, require_admin_enabled

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin_enabled():
    """Check if admin functionality is enabled before any admin request"""
    if not is_admin_enabled():
        return jsonify({'error': 'Admin functionality is disabled'}), 403

@admin_bp.route('/test')
@login_required
def admin_test():
    """Admin test page - only accessible by admins"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({
        'message': 'Admin access confirmed',
        'user': current_user.to_dict(),
        'admin_features': [
            'Unlimited API calls',
            'Unlimited Gemini calls',
            'User management',
            'Usage statistics',
            'Profile picture testing',
            'System monitoring'
        ],
        'environment': {
            'admin_routes_enabled': True,
            'flask_env': os.getenv('FLASK_ENV'),
            'debug_mode': os.getenv('FLASK_ENV') == 'development'
        }
    })

@admin_bp.route('/users')
@login_required
def admin_users():
    """List all users - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    users = User.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': users.total,
            'pages': users.pages,
            'has_next': users.has_next,
            'has_prev': users.has_prev
        }
    })

@admin_bp.route('/promote/<int:user_id>', methods=['POST'])
@login_required
def admin_promote_user(user_id):
    """Promote user to admin - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        user.make_admin()
        return jsonify({
            'message': f'User {user.email} promoted to admin',
            'user': user.to_dict()
        })
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 403

@admin_bp.route('/demote/<int:user_id>', methods=['POST'])
@login_required
def admin_demote_user(user_id):
    """Remove admin role from user - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Don't allow demoting yourself
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot demote yourself'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        user.remove_admin()
        return jsonify({
            'message': f'Admin role removed from {user.email}',
            'user': user.to_dict()
        })
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 403

@admin_bp.route('/create', methods=['POST'])
@login_required
def admin_create_user():
    """Create a new user (admin or regular) - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    make_admin = data.get('is_admin', False)
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400
    
    try:
        if make_admin:
            user = User.create_admin_user(email, password, name)
        else:
            user = User.create_user(email, password, name)
            db.session.add(user)
            db.session.commit()
        
        return jsonify({
            'message': f'User {email} created successfully',
            'user': user.to_dict()
        }), 201
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@admin_bp.route('/stats')
@login_required
def admin_stats():
    """Get system statistics - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    total_users = User.query.count()
    admin_users = User.get_admins()
    oauth_users = User.query.filter(User.provider.isnot(None)).count()
    email_users = total_users - oauth_users
    
    return jsonify({
        'statistics': {
            'total_users': total_users,
            'admin_users': len(admin_users),
            'oauth_users': oauth_users,
            'email_users': email_users,
            'admin_list': [admin.to_dict() for admin in admin_users]
        }
    })

@admin_bp.route('/reset-limits/<int:user_id>', methods=['POST'])
@login_required
def admin_reset_limits(user_id):
    """Reset API limits for a user - admin only"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Reset daily counters
    user.api_calls_today = 0
    user.gemini_calls_today = 0
    db.session.commit()
    
    return jsonify({
        'message': f'API limits reset for {user.email}',
        'user': user.to_dict()
    })
