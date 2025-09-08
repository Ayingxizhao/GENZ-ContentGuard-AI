"""Bug report model and related enums."""

from datetime import datetime
from enum import Enum
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Index, Integer, String, Text

db = SQLAlchemy()


class BugStatus(Enum):
    """Enum for bug report status."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class BugPriority(Enum):
    """Enum for bug priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BugReport(db.Model):
    """Model for storing bug reports."""

    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    browser_info = Column(String(100), nullable=True)
    operating_system = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)
    url_where_bug_occurred = Column(String(500), nullable=True)
    screenshot_url = Column(String(500), nullable=True)
    reporter_email = Column(String(100), nullable=True, index=True)
    reporter_name = Column(String(100), nullable=True)
    status = Column(SQLEnum(BugStatus), default=BugStatus.OPEN, nullable=False, index=True)
    priority = Column(SQLEnum(BugPriority), default=BugPriority.MEDIUM, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolution_notes = Column(Text, nullable=True)

    # Indexes for better query performance
    __table_args__ = (
        Index("idx_bug_reports_status_priority", "status", "priority"),
        Index("idx_bug_reports_created_at", "created_at"),
        Index("idx_bug_reports_reporter_email", "reporter_email"),
    )

    def to_dict(self) -> dict:
        """Convert bug report to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "steps_to_reproduce": self.steps_to_reproduce,
            "expected_behavior": self.expected_behavior,
            "actual_behavior": self.actual_behavior,
            "browser_info": self.browser_info,
            "operating_system": self.operating_system,
            "user_agent": self.user_agent,
            "url_where_bug_occurred": self.url_where_bug_occurred,
            "screenshot_url": self.screenshot_url,
            "reporter_email": self.reporter_email,
            "reporter_name": self.reporter_name,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_resolved": self.is_resolved,
            "resolution_notes": self.resolution_notes,
        }

    def update_status(self, new_status: BugStatus, resolution_notes: Optional[str] = None) -> None:
        """Update bug status and resolution notes."""
        self.status = new_status
        self.is_resolved = new_status in [BugStatus.RESOLVED, BugStatus.CLOSED]
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<BugReport {self.id}: {self.title}>"
