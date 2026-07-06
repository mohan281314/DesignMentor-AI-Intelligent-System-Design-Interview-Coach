"""
User and UserProfile models.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.design import Design
    from app.models.interview import Interview


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth users
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # OAuth
    oauth_provider = Column(String(50), nullable=True)  # "google", "github", None
    oauth_id = Column(String(255), nullable=True, unique=True)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    designs = relationship("Design", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="user", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    """Extended user profile with performance tracking and preferences."""
    
    __tablename__ = "user_profiles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Performance Scores (0-10 scale, averaged across all interviews)
    score_correctness = Column(Float, default=0.0, nullable=False)
    score_scalability = Column(Float, default=0.0, nullable=False)
    score_tradeoffs = Column(Float, default=0.0, nullable=False)
    score_communication = Column(Float, default=0.0, nullable=False)
    score_depth = Column(Float, default=0.0, nullable=False)
    
    # Aggregate stats
    total_interviews = Column(Integer, default=0, nullable=False)
    total_designs = Column(Integer, default=0, nullable=False)
    total_diagrams = Column(Integer, default=0, nullable=False)
    
    # Experience level (calculated from performance)
    experience_level = Column(String(50), default="beginner", nullable=False)  # beginner, intermediate, advanced, expert
    
    # Weakness areas (comma-separated topics)
    weak_topics = Column(Text, nullable=True)  # "databases,caching,load-balancing"
    
    # Strengths
    strong_topics = Column(Text, nullable=True)
    
    # Learning preferences
    preferred_difficulty = Column(String(50), default="medium", nullable=False)  # easy, medium, hard
    preferred_topics = Column(Text, nullable=True)  # User's interests
    
    # Spaced repetition tracking
    last_practice_date = Column(DateTime(timezone=True), nullable=True)
    next_practice_date = Column(DateTime(timezone=True), nullable=True)
    
    # UI Preferences
    theme = Column(String(20), default="dark", nullable=False)  # dark, light
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, level={self.experience_level})>"
    
    @property
    def average_score(self) -> float:
        """Calculate overall average performance score."""
        scores = [
            self.score_correctness,
            self.score_scalability,
            self.score_tradeoffs,
            self.score_communication,
            self.score_depth,
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    def update_scores(self, new_scores: dict[str, float]) -> None:
        """
        Update performance scores with weighted average.
        
        Args:
            new_scores: Dict with keys: correctness, scalability, tradeoffs, communication, depth
        """
        total = self.total_interviews
        weight = total / (total + 1) if total > 0 else 0
        
        self.score_correctness = (self.score_correctness * weight) + (new_scores.get("correctness", 0) * (1 - weight))
        self.score_scalability = (self.score_scalability * weight) + (new_scores.get("scalability", 0) * (1 - weight))
        self.score_tradeoffs = (self.score_tradeoffs * weight) + (new_scores.get("tradeoffs", 0) * (1 - weight))
        self.score_communication = (self.score_communication * weight) + (new_scores.get("communication", 0) * (1 - weight))
        self.score_depth = (self.score_depth * weight) + (new_scores.get("depth", 0) * (1 - weight))
