"""Application factory for creating Flask app instances."""

from flask import Flask
from flask_cors import CORS

from app.config import get_config
from app.models.bug_report import db
from app.routes.bug_reports import bug_reports_bp
from app.utils.database import init_database


def create_app(config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)

    # Initialize extensions
    CORS(app)  # Enable CORS for all routes
    db.init_app(app)

    # Initialize database
    init_database(app)

    # Register blueprints
    app.register_blueprint(bug_reports_bp)

    # Register main routes
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)

    return app
