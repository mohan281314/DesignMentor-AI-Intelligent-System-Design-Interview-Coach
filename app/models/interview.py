"""
Interview and InterviewTurn models for mock interviews.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Interview(Base):
    """Mock interview session model."""
    
    __tablename__ = "interviews"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Interview data
    topic = Column(String(200), nullable=False, index=True)
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    
    # Overall performance scores (0-10 scale, averaged from all turns)
    score_correctness = Column(Float, default=0.0, nullable=False)
    score_scalability = Column(Float, default=0.0, nullable=False)
    score_tradeoffs = Column(Float, default=0.0, nullable=False)
    score_communication = Column(Float, default=0.0, nullable=False)
    score_depth = Column(Float, default=0.0, nullable=False)
    score_overall = Column(Float, default=0.0, nullable=False)
    
    # Stats
    total_turns = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=True)
    
    # AI generation metadata
    llm_provider = Column(String(50), nullable=True)
    llm_model = Column(String(100), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    turns = relationship("InterviewTurn", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewTurn.turn_number")
    share_links = relationship("ShareLink", back_populates="interview", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Interview(id={self.id}, topic={self.topic}, user_id={self.user_id}, status={self.status})>"
    
    def calculate_scores(self) -> None:
        """Calculate overall scores from all turns."""
        if not self.turns or self.total_turns == 0:
            return
        
        total_correctness = 0.0
        total_scalability = 0.0
        total_tradeoffs = 0.0
        total_communication = 0.0
        total_depth = 0.0
        
        for turn in self.turns:
            total_correctness += turn.score_correctness or 0
            total_scalability += turn.score_scalability or 0
            total_tradeoffs += turn.score_tradeoffs or 0
            total_communication += turn.score_communication or 0
            total_depth += turn.score_depth or 0
        
        count = self.total_turns
        self.score_correctness = total_correctness / count
        self.score_scalability = total_scalability / count
        self.score_tradeoffs = total_tradeoffs / count
        self.score_communication = total_communication / count
        self.score_depth = total_depth / count
        
        # Overall is average of all dimension scores
        self.score_overall = (
            self.score_correctness +
            self.score_scalability +
            self.score_tradeoffs +
            self.score_communication +
            self.score_depth
        ) / 5


class InterviewTurn(Base):
    """Individual Q&A turn within an interview."""
    
    __tablename__ = "interview_turns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    
    # Turn data
    turn_number = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    evaluation = Column(Text, nullable=False)  # Markdown evaluation
    
    # Scores for this turn (0-10 scale)
    score_correctness = Column(Float, nullable=True)
    score_scalability = Column(Float, nullable=True)
    score_tradeoffs = Column(Float, nullable=True)
    score_communication = Column(Float, nullable=True)
    score_depth = Column(Float, nullable=True)
    
    # Metadata
    answer_word_count = Column(Integer, default=0, nullable=False)
    answer_time_seconds = Column(Integer, nullable=True)  # Time taken to answer
    
    # Extracted insights (parsed from evaluation)
    strengths = Column(JSON, nullable=True)  # List of strength points
    weaknesses = Column(JSON, nullable=True)  # List of weakness points
    suggestions = Column(JSON, nullable=True)  # List of improvement suggestions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="turns")
    
    def __repr__(self) -> str:
        return f"<InterviewTurn(id={self.id}, interview_id={self.interview_id}, turn={self.turn_number})>"
