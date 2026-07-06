"""
Design service — persists generated designs to the database.
"""

from __future__ import annotations

import time
from typing import Optional

from sqlalchemy.orm import Session

from app.models.design import Design
from app.models.analytics import UserActivity


class DesignService:
    """Business logic for design generation and persistence."""

    @staticmethod
    def save_design(
        db: Session,
        user_id: int,
        topic: str,
        content: str,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.3-70b-versatile",
        generation_time_seconds: Optional[int] = None,
    ) -> Design:
        """Persist a generated design to the database."""
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # ~200 wpm

        design = Design(
            user_id=user_id,
            topic=topic,
            content=content,
            word_count=word_count,
            estimated_reading_time=reading_time,
            llm_provider=llm_provider,
            llm_model=llm_model,
            generation_time_seconds=generation_time_seconds,
        )
        db.add(design)

        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="design_generated",
            description=f"Generated system design for: {topic}",
            topic=topic,
        )
        db.add(activity)

        db.commit()
        db.refresh(design)
        return design

    @staticmethod
    def get_user_designs(
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        topic_filter: Optional[str] = None,
    ) -> tuple[list[Design], int]:
        """Get paginated list of user designs."""
        query = db.query(Design).filter(Design.user_id == user_id)

        if topic_filter:
            query = query.filter(Design.topic.ilike(f"%{topic_filter}%"))

        total = query.count()
        designs = (
            query.order_by(Design.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return designs, total

    @staticmethod
    def get_design_by_id(
        db: Session,
        design_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Design]:
        """Get a design by ID, optionally scoped to a user."""
        query = db.query(Design).filter(Design.id == design_id)
        if user_id:
            query = query.filter(Design.user_id == user_id)
        return query.first()

    @staticmethod
    def delete_design(db: Session, design_id: int, user_id: int) -> bool:
        """Delete a design (only if owned by user)."""
        design = (
            db.query(Design)
            .filter(Design.id == design_id, Design.user_id == user_id)
            .first()
        )
        if not design:
            return False
        db.delete(design)
        db.commit()
        return True
