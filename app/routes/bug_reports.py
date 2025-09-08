"""Bug reports API routes."""

from typing import Tuple, Union
from flask import Blueprint, Response, jsonify, request
from app.models.bug_report import db, BugReport, BugStatus, BugPriority
from app.utils.database import get_bug_statistics

bug_reports_bp = Blueprint('bug_reports', __name__, url_prefix='/api/bug-reports')


@bug_reports_bp.route('/', methods=['POST'])
def create_bug_report() -> Union[Response, Tuple[Response, int]]:
    """Create a new bug report."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("title") or not data.get("description"):
            return jsonify({"error": "Title and description are required"}), 400
        
        # Validate title length
        if len(data.get("title", "")) > 200:
            return jsonify({"error": "Title must be 200 characters or less"}), 400
        
        # Validate description length
        if len(data.get("description", "")) > 10000:
            return jsonify({"error": "Description must be 10,000 characters or less"}), 400
        
        # Create new bug report
        bug_report = BugReport(
            title=data.get("title"),
            description=data.get("description"),
            steps_to_reproduce=data.get("steps_to_reproduce"),
            expected_behavior=data.get("expected_behavior"),
            actual_behavior=data.get("actual_behavior"),
            browser_info=data.get("browser_info"),
            operating_system=data.get("operating_system"),
            user_agent=data.get("user_agent"),
            url_where_bug_occurred=data.get("url_where_bug_occurred"),
            screenshot_url=data.get("screenshot_url"),
            reporter_email=data.get("reporter_email"),
            reporter_name=data.get("reporter_name"),
            priority=BugPriority(data.get("priority", "medium"))
        )
        
        db.session.add(bug_report)
        db.session.commit()
        
        return jsonify({
            "message": "Bug report created successfully",
            "bug_report_id": bug_report.id,
            "bug_report": bug_report.to_dict()
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bug_reports_bp.route('/', methods=['GET'])
def get_bug_reports() -> Union[Response, Tuple[Response, int]]:
    """Get all bug reports with optional filtering."""
    try:
        # Get query parameters
        status = request.args.get("status")
        priority = request.args.get("priority")
        limit = request.args.get("limit", type=int)
        offset = request.args.get("offset", 0, type=int)
        
        # Validate pagination parameters
        if limit and (limit < 1 or limit > 100):
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
        
        if offset < 0:
            return jsonify({"error": "Offset must be non-negative"}), 400
        
        # Build query
        query = BugReport.query
        
        if status:
            try:
                status_enum = BugStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({"error": "Invalid status value"}), 400
        
        if priority:
            try:
                priority_enum = BugPriority(priority)
                query = query.filter_by(priority=priority_enum)
            except ValueError:
                return jsonify({"error": "Invalid priority value"}), 400
        
        # Apply pagination
        if limit:
            query = query.limit(limit)
        query = query.offset(offset)
        
        # Order by creation date (newest first)
        query = query.order_by(BugReport.created_at.desc())
        
        bug_reports = query.all()
        
        return jsonify({
            "bug_reports": [report.to_dict() for report in bug_reports],
            "total": BugReport.query.count(),
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bug_reports_bp.route('/<int:bug_id>', methods=['GET'])
def get_bug_report(bug_id: int) -> Union[Response, Tuple[Response, int]]:
    """Get a specific bug report by ID."""
    try:
        bug_report = BugReport.query.get_or_404(bug_id)
        return jsonify(bug_report.to_dict())
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bug_reports_bp.route('/<int:bug_id>', methods=['PUT'])
def update_bug_report(bug_id: int) -> Union[Response, Tuple[Response, int]]:
    """Update a bug report."""
    try:
        bug_report = BugReport.query.get_or_404(bug_id)
        data = request.get_json()
        
        # Update fields if provided
        if "title" in data:
            if len(data["title"]) > 200:
                return jsonify({"error": "Title must be 200 characters or less"}), 400
            bug_report.title = data["title"]
        
        if "description" in data:
            if len(data["description"]) > 10000:
                return jsonify({"error": "Description must be 10,000 characters or less"}), 400
            bug_report.description = data["description"]
        
        if "status" in data:
            try:
                bug_report.status = BugStatus(data["status"])
                bug_report.is_resolved = bug_report.status in [BugStatus.RESOLVED, BugStatus.CLOSED]
            except ValueError:
                return jsonify({"error": "Invalid status value"}), 400
        
        if "priority" in data:
            try:
                bug_report.priority = BugPriority(data["priority"])
            except ValueError:
                return jsonify({"error": "Invalid priority value"}), 400
        
        if "resolution_notes" in data:
            bug_report.resolution_notes = data["resolution_notes"]
        
        if "is_resolved" in data:
            bug_report.is_resolved = data["is_resolved"]
        
        db.session.commit()
        
        return jsonify({
            "message": "Bug report updated successfully",
            "bug_report": bug_report.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bug_reports_bp.route('/<int:bug_id>', methods=['DELETE'])
def delete_bug_report(bug_id: int) -> Union[Response, Tuple[Response, int]]:
    """Delete a bug report."""
    try:
        bug_report = BugReport.query.get_or_404(bug_id)
        db.session.delete(bug_report)
        db.session.commit()
        
        return jsonify({"message": "Bug report deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bug_reports_bp.route('/stats', methods=['GET'])
def get_bug_stats() -> Union[Response, Tuple[Response, int]]:
    """Get bug report statistics."""
    try:
        stats = get_bug_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
