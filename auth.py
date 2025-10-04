"""
OAuth authentication handlers for Google and GitHub
"""
import os
from datetime import datetime
from flask import Blueprint, redirect, url_for, session, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from authlib.integrations.flask_client import OAuth
from models import db, User

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth providers"""
    oauth.init_app(app)
    
    # Google OAuth
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID', 'PLACEHOLDER_GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'PLACEHOLDER_GOOGLE_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # GitHub OAuth
    oauth.register(
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID', 'PLACEHOLDER_GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET', 'PLACEHOLDER_GITHUB_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


@auth_bp.route('/login/<provider>')
def login(provider):
    """Initiate OAuth login flow"""
    if provider not in ['google', 'github']:
        return jsonify({'error': 'Invalid provider'}), 400
    
    # Store the provider in session for callback
    session['oauth_provider'] = provider
    
    # Generate redirect URI
    redirect_uri = url_for('auth.callback', provider=provider, _external=True)
    
    # Redirect to OAuth provider
    return oauth.create_client(provider).authorize_redirect(redirect_uri)


@auth_bp.route('/callback/<provider>')
def callback(provider):
    """Handle OAuth callback"""
    if provider not in ['google', 'github']:
        return jsonify({'error': 'Invalid provider'}), 400
    
    try:
        # Get OAuth token
        client = oauth.create_client(provider)
        token = client.authorize_access_token()
        
        # Get user info from provider
        if provider == 'google':
            user_info = token.get('userinfo')
            email = user_info.get('email')
            name = user_info.get('name')
            avatar_url = user_info.get('picture')
            provider_user_id = user_info.get('sub')
        
        elif provider == 'github':
            # Get user info from GitHub API
            resp = client.get('user', token=token)
            user_info = resp.json()
            email = user_info.get('email')
            
            # If email is private, fetch from emails endpoint
            if not email:
                emails_resp = client.get('user/emails', token=token)
                emails = emails_resp.json()
                # Get primary email
                for email_obj in emails:
                    if email_obj.get('primary'):
                        email = email_obj.get('email')
                        break
            
            name = user_info.get('name') or user_info.get('login')
            avatar_url = user_info.get('avatar_url')
            provider_user_id = str(user_info.get('id'))
        
        if not email:
            return jsonify({'error': 'Could not retrieve email from provider'}), 400
        
        # Find or create user
        user = User.query.filter_by(provider=provider, provider_user_id=provider_user_id).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=name,
                avatar_url=avatar_url,
                provider=provider,
                provider_user_id=provider_user_id,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(user)
        else:
            # Update existing user info
            user.email = email
            user.name = name
            user.avatar_url = avatar_url
            user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        
        # Redirect to home page
        return redirect('/')
    
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return redirect('/?error=auth_failed')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    return redirect('/')


@auth_bp.route('/user')
def get_user():
    """Get current user info (API endpoint)"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    else:
        return jsonify({
            'authenticated': False,
            'user': None
        })


@auth_bp.route('/usage')
@login_required
def get_usage():
    """Get current user's API usage stats"""
    return jsonify({
        'api_calls_count': current_user.api_calls_count,
        'api_calls_today': current_user.api_calls_today,
        'daily_limit': current_user.daily_limit,
        'remaining_calls': current_user.get_remaining_calls(),
        'has_exceeded_limit': current_user.has_exceeded_daily_limit()
    })
