"""Database utility functions."""

import os

from flask import Flask

from app.models.bug_report import BugPriority, BugReport, BugStatus, db


def init_database(app: Flask) -> None:
    """Initialize database with Flask app."""
    # Configure database URI
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Handle PostgreSQL URL format from Render
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Fallback to local SQLite for development
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bug_reports.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Create tables
        db.create_all()
        print("Database initialized successfully")


def create_sample_bug_report() -> BugReport:
    """Create a sample bug report for testing."""
    sample_report = BugReport(
        title="Sample Bug Report",
        description="This is a sample bug report for testing purposes.",
        steps_to_reproduce="1. Navigate to the homepage\n2. Click on the analyze button\n3. Observe the error",
        expected_behavior="The analyze button should work correctly",
        actual_behavior="The analyze button throws an error",
        browser_info="Chrome 120.0",
        operating_system="macOS 14.0",
        reporter_email="test@example.com",
        reporter_name="Test User",
        status=BugStatus.OPEN,
        priority=BugPriority.MEDIUM,
    )
    return sample_report


def get_bug_reports_count() -> int:
    """Get total count of bug reports."""
    return BugReport.query.count()


def get_bug_reports_by_status(status: BugStatus) -> list:
    """Get bug reports filtered by status."""
    return BugReport.query.filter_by(status=status).all()


def get_bug_reports_by_priority(priority: BugPriority) -> list:
    """Get bug reports filtered by priority."""
    return BugReport.query.filter_by(priority=priority).all()


def get_bug_statistics() -> dict:
    """Get comprehensive bug report statistics."""
    total_reports = BugReport.query.count()

    # Status counts
    status_counts = {}
    for status in BugStatus:
        status_counts[status.value] = BugReport.query.filter_by(status=status).count()

    # Priority counts
    priority_counts = {}
    for priority in BugPriority:
        priority_counts[priority.value] = BugReport.query.filter_by(priority=priority).count()

    # Recent reports (last 30 days)
    from datetime import datetime, timedelta

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_reports = BugReport.query.filter(BugReport.created_at >= thirty_days_ago).count()

    return {
        "total_reports": total_reports,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "recent_reports": recent_reports,
    }
