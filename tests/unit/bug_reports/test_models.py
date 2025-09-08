"""Unit tests for bug report models."""

import pytest
from datetime import datetime
from app import create_app
from app.models.bug_report import db, BugReport, BugStatus, BugPriority
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create test application."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_bug_report():
    """Create sample bug report."""
    return BugReport(
        title="Test Bug",
        description="This is a test bug report",
        reporter_email="test@example.com",
        status=BugStatus.OPEN,
        priority=BugPriority.MEDIUM
    )


def test_bug_report_creation(app, sample_bug_report):
    """Test bug report creation."""
    with app.app_context():
        db.session.add(sample_bug_report)
        db.session.commit()
        
        assert sample_bug_report.id is not None
        assert sample_bug_report.title == "Test Bug"
        assert sample_bug_report.status == BugStatus.OPEN
        assert sample_bug_report.priority == BugPriority.MEDIUM


def test_bug_report_to_dict(app, sample_bug_report):
    """Test bug report to_dict method."""
    with app.app_context():
        db.session.add(sample_bug_report)
        db.session.commit()
        
        bug_dict = sample_bug_report.to_dict()
        
        assert bug_dict['title'] == "Test Bug"
        assert bug_dict['status'] == "open"
        assert bug_dict['priority'] == "medium"
        assert 'created_at' in bug_dict
        assert 'updated_at' in bug_dict


def test_bug_report_status_update(app, sample_bug_report):
    """Test bug report status update."""
    with app.app_context():
        db.session.add(sample_bug_report)
        db.session.commit()
        
        sample_bug_report.update_status(BugStatus.RESOLVED, "Fixed the issue")
        
        assert sample_bug_report.status == BugStatus.RESOLVED
        assert sample_bug_report.is_resolved is True
        assert sample_bug_report.resolution_notes == "Fixed the issue"


def test_bug_status_enum():
    """Test bug status enum values."""
    assert BugStatus.OPEN.value == "open"
    assert BugStatus.IN_PROGRESS.value == "in_progress"
    assert BugStatus.RESOLVED.value == "resolved"
    assert BugStatus.CLOSED.value == "closed"


def test_bug_priority_enum():
    """Test bug priority enum values."""
    assert BugPriority.LOW.value == "low"
    assert BugPriority.MEDIUM.value == "medium"
    assert BugPriority.HIGH.value == "high"
    assert BugPriority.CRITICAL.value == "critical"
