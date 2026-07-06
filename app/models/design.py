"""
Design model for storing generated system designs.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Design(Base):
    """Saved system design model."""
    
    __tablename__ = "designs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Design data
    topic = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Markdown content
    
    # Metadata
    word_count = Column(Integer, default=0, nullable=False)
    estimated_reading_time = Column(Integer, default=0, nullable=False)  # minutes
    
    # Tags for organization
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Sharing
    is_public = Column(Boolean, default=False, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    # AI generation metadata
    llm_provider = Column(String(50), nullable=True)  # "groq", "openai"
    llm_model = Column(String(100), nullable=True)
    generation_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="designs")
    share_links = relationship("ShareLink", back_populates="design", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Design(id={self.id}, topic={self.topic}, user_id={self.user_id})>"
