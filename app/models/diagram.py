"""
Diagram model for architecture visualizations.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Diagram(Base):
    """Architecture diagram model."""
    
    __tablename__ = "diagrams"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Diagram data
    topic = Column(String(200), nullable=False, index=True)
    diagram_type = Column(String(50), default="flowchart", nullable=False)  # flowchart, c4, sequence, erd, dataflow
    mermaid_code = Column(Text, nullable=False)
    design_summary = Column(Text, nullable=True)
    
    # Metadata
    explanation = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)  # JSON array of improvement suggestions
    
    # Sharing
    is_public = Column(Boolean, default=False, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    # AI generation metadata
    llm_provider = Column(String(50), nullable=True)
    llm_model = Column(String(100), nullable=True)
    generation_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="diagrams")
    share_links = relationship("ShareLink", back_populates="diagram", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Diagram(id={self.id}, topic={self.topic}, type={self.diagram_type})>"
