"""Integration tests for bug reports API."""

import pytest
import json
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
def sample_bug_data():
    """Sample bug report data."""
    return {
        "title": "Test Bug Report",
        "description": "This is a test bug description",
        "steps_to_reproduce": "1. Go to homepage\n2. Click button\n3. See error",
        "expected_behavior": "Button should work",
        "actual_behavior": "Button throws error",
        "browser_info": "Chrome 120.0",
        "operating_system": "macOS 14.0",
        "reporter_email": "test@example.com",
        "reporter_name": "Test User",
        "priority": "medium"
    }


def test_create_bug_report(client, sample_bug_data):
    """Test creating a bug report."""
    response = client.post('/api/bug-reports/', 
                          data=json.dumps(sample_bug_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "Bug report created successfully"
    assert 'bug_report_id' in data
    assert data['bug_report']['title'] == "Test Bug Report"


def test_create_bug_report_missing_required_fields(client):
    """Test creating bug report with missing required fields."""
    response = client.post('/api/bug-reports/', 
                          data=json.dumps({"title": "Test"}),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Title and description are required" in data['error']


def test_get_bug_reports(client, sample_bug_data):
    """Test getting all bug reports."""
    # Create a bug report first
    client.post('/api/bug-reports/', 
               data=json.dumps(sample_bug_data),
               content_type='application/json')
    
    response = client.get('/api/bug-reports/')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'bug_reports' in data
    assert len(data['bug_reports']) == 1
    assert data['total'] == 1


def test_get_bug_report_by_id(client, sample_bug_data):
    """Test getting a specific bug report by ID."""
    # Create a bug report first
    create_response = client.post('/api/bug-reports/', 
                                data=json.dumps(sample_bug_data),
                                content_type='application/json')
    bug_id = create_response.get_json()['bug_report_id']
    
    response = client.get(f'/api/bug-reports/{bug_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == "Test Bug Report"


def test_update_bug_report(client, sample_bug_data):
    """Test updating a bug report."""
    # Create a bug report first
    create_response = client.post('/api/bug-reports/', 
                                data=json.dumps(sample_bug_data),
                                content_type='application/json')
    bug_id = create_response.get_json()['bug_report_id']
    
    # Update the bug report
    update_data = {
        "status": "resolved",
        "resolution_notes": "Fixed the issue"
    }
    
    response = client.put(f'/api/bug-reports/{bug_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Bug report updated successfully"
    assert data['bug_report']['status'] == "resolved"


def test_delete_bug_report(client, sample_bug_data):
    """Test deleting a bug report."""
    # Create a bug report first
    create_response = client.post('/api/bug-reports/', 
                                data=json.dumps(sample_bug_data),
                                content_type='application/json')
    bug_id = create_response.get_json()['bug_report_id']
    
    # Delete the bug report
    response = client.delete(f'/api/bug-reports/{bug_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Bug report deleted successfully"


def test_get_bug_statistics(client, sample_bug_data):
    """Test getting bug report statistics."""
    # Create a bug report first
    client.post('/api/bug-reports/', 
               data=json.dumps(sample_bug_data),
               content_type='application/json')
    
    response = client.get('/api/bug-reports/stats')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_reports' in data
    assert 'by_status' in data
    assert 'by_priority' in data
    assert data['total_reports'] == 1
