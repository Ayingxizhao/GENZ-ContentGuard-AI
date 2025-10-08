"""
OAuth authentication handlers for Google and GitHub
"""
import os
from datetime import datetime
from flask import Blueprint, redirect, url_for, session, request, jsonify, render_template
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

        # Find user by provider credentials first
        user = User.query.filter_by(provider=provider, provider_user_id=provider_user_id).first()

        if not user:
            # Check if user exists with this email (for account merging)
            user = User.query.filter_by(email=email).first()

            if user:
                # Merge OAuth with existing account
                # Link OAuth provider to existing email/password account
                user.provider = provider
                user.provider_user_id = provider_user_id
                if not user.name:
                    user.name = name
                if not user.avatar_url:
                    user.avatar_url = avatar_url
                user.last_login = datetime.utcnow()
            else:
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
            # Update existing OAuth user info
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


# ============================================================================
# Email/Password Authentication Routes
# ============================================================================

@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    """Show signup page"""
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Show login page"""
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('login.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user with email/password"""
    from utils.validators import validate_email, validate_password, validate_name

    try:
        data = request.get_json() or {}

        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        name = (data.get('name') or '').strip() or None

        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return jsonify({'error': email_error}), 400

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return jsonify({'error': password_error}), 400

        # Validate name if provided
        if name:
            name_valid, name_error = validate_name(name)
            if not name_valid:
                return jsonify({'error': name_error}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'An account with this email already exists'}), 400

        # Create new user
        user = User.create_user(email=email, password=password, name=name)
        db.session.add(user)
        db.session.commit()

        # Log the user in
        login_user(user, remember=True)

        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/login-email', methods=['POST'])
def login_email():
    """Login with email/password"""
    from utils.validators import validate_email

    try:
        data = request.get_json() or {}

        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        remember = data.get('remember', True)

        # Validate email format
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return jsonify({'error': email_error}), 400

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if this is an OAuth-only account
        if user.provider and not user.password_hash:
            return jsonify({
                'error': f'This account uses {user.provider.title()} login. Please use the {user.provider.title()} button to sign in.'
            }), 400

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Log the user in
        login_user(user, remember=remember)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500
