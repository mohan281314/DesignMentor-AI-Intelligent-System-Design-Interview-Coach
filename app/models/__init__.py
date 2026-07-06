"""
SQLAlchemy models for DesignMentor AI.

Import all models here to ensure they're registered with SQLAlchemy Base.
"""

from app.db.base import Base
from app.models.user import User, UserProfile
from app.models.design import Design
from app.models.interview import Interview, InterviewTurn
from app.models.diagram import Diagram
from app.models.share import ShareLink
from app.models.analytics import PerformanceMetric, UserActivity

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "Design",
    "Interview",
    "InterviewTurn",
    "Diagram",
    "ShareLink",
    "PerformanceMetric",
    "UserActivity",
]
