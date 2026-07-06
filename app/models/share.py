"""
ShareLink model for public sharing of designs, interviews, and diagrams.
"""

import secrets
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ShareLink(Base):
    """Public share link for resources."""
    
    __tablename__ = "share_links"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique public ID for URL
    public_id = Column(String(32), unique=True, index=True, nullable=False)
    
    # Resource type and ID
    resource_type = Column(String(50), nullable=False, index=True)  # "design", "interview", "diagram"
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    diagram_id = Column(Integer, ForeignKey("diagrams.id"), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    design = relationship("Design", back_populates="share_links")
    interview = relationship("Interview", back_populates="share_links")
    diagram = relationship("Diagram", back_populates="share_links")
    
    def __repr__(self) -> str:
        return f"<ShareLink(public_id={self.public_id}, type={self.resource_type})>"
    
    @staticmethod
    def generate_public_id() -> str:
        """Generate a secure random public ID."""
        return secrets.token_urlsafe(16)
    
    @property
    def is_expired(self) -> bool:
        """Check if link has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def url(self) -> str:
        """Generate full share URL."""
        return f"/share/{self.public_id}"
