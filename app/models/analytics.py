"""
Analytics models for performance tracking and user activity.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PerformanceMetric(Base):
    """Time-series performance metrics for tracking improvement."""
    
    __tablename__ = "performance_metrics"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Metric data
    metric_type = Column(String(50), nullable=False, index=True)  # "interview_score", "design_quality", etc.
    metric_name = Column(String(100), nullable=False)  # "correctness", "scalability", etc.
    metric_value = Column(Float, nullable=False)
    
    # Context
    topic = Column(String(200), nullable=True, index=True)
    related_resource_type = Column(String(50), nullable=True)  # "interview", "design"
    related_resource_id = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="performance_metrics")
    
    def __repr__(self) -> str:
        return f"<PerformanceMetric(user_id={self.user_id}, type={self.metric_type}, value={self.metric_value})>"


class UserActivity(Base):
    """User activity log for analytics and recommendations."""
    
    __tablename__ = "user_activities"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity data
    activity_type = Column(String(50), nullable=False, index=True)  # "design_generated", "interview_started", etc.
    description = Column(Text, nullable=True)
    
    # Context
    topic = Column(String(200), nullable=True, index=True)
    extra_data = Column(JSON, nullable=True)  # Additional structured data (renamed from 'metadata' - reserved by SQLAlchemy)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<UserActivity(user_id={self.user_id}, type={self.activity_type})>"
