"""
Interview service — persists interview sessions and evaluates performance.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.interview import Interview, InterviewTurn
from app.models.user import UserProfile
from app.models.analytics import UserActivity, PerformanceMetric


class InterviewService:
    """Business logic for persistent interview sessions with scoring."""

    @staticmethod
    def create_interview(db: Session, user_id: int, topic: str) -> Interview:
        """Create a new interview session."""
        interview = Interview(
            user_id=user_id,
            topic=topic,
            status="in_progress",
        )
        db.add(interview)

        activity = UserActivity(
            user_id=user_id,
            activity_type="interview_started",
            description=f"Started interview on: {topic}",
            topic=topic,
        )
        db.add(activity)

        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def add_turn(
        db: Session,
        interview: Interview,
        question: str,
        answer: str,
        evaluation: str,
    ) -> InterviewTurn:
        """
        Add a Q&A turn and extract scores from the evaluation text.
        """
        scores = InterviewService._extract_scores(evaluation)
        strengths, weaknesses, suggestions = InterviewService._extract_insights(evaluation)

        turn = InterviewTurn(
            interview_id=interview.id,
            turn_number=interview.total_turns + 1,
            question=question,
            answer=answer,
            evaluation=evaluation,
            answer_word_count=len(answer.split()),
            score_correctness=scores.get("correctness"),
            score_scalability=scores.get("scalability"),
            score_tradeoffs=scores.get("tradeoffs"),
            score_communication=scores.get("communication"),
            score_depth=scores.get("depth"),
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
        )
        db.add(turn)

        interview.total_turns += 1
        db.flush()
        return turn

    @staticmethod
    def complete_interview(db: Session, interview: Interview, user_id: int) -> Interview:
        """Mark interview complete, update scores and user profile."""
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()
        db.flush()

        # Reload turns
        turns = interview.turns
        if turns:
            interview.calculate_scores()

        # Update user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile.total_interviews += 1
            new_scores = {
                "correctness":   interview.score_correctness,
                "scalability":   interview.score_scalability,
                "tradeoffs":     interview.score_tradeoffs,
                "communication": interview.score_communication,
                "depth":         interview.score_depth,
            }
            profile.update_scores(new_scores)
            profile.experience_level = InterviewService._calc_level(profile.average_score)

        # Log activity and metrics
        activity = UserActivity(
            user_id=user_id,
            activity_type="interview_completed",
            description=f"Completed interview on: {interview.topic}",
            topic=interview.topic,
        )
        db.add(activity)

        for dim, val in {
            "correctness":   interview.score_correctness,
            "scalability":   interview.score_scalability,
            "tradeoffs":     interview.score_tradeoffs,
            "communication": interview.score_communication,
            "depth":         interview.score_depth,
        }.items():
            metric = PerformanceMetric(
                user_id=user_id,
                metric_type="interview_score",
                metric_name=dim,
                metric_value=val,
                topic=interview.topic,
                related_resource_type="interview",
                related_resource_id=interview.id,
            )
            db.add(metric)

        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def get_user_interviews(
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> tuple[list[Interview], int]:
        """Get paginated list of user interviews."""
        query = db.query(Interview).filter(Interview.user_id == user_id)
        if status_filter:
            query = query.filter(Interview.status == status_filter)
        total = query.count()
        interviews = (
            query.order_by(Interview.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return interviews, total

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_scores(evaluation: str) -> dict[str, float]:
        """
        Parse scores out of the evaluation markdown.
        Looks for patterns like "Correctness: 7/10" or "**Score**: 8".
        """
        scores: dict[str, float] = {}
        patterns = {
            "correctness":   r"correctness[^0-9]*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            "scalability":   r"scalabilit[^0-9]*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            "tradeoffs":     r"trade.?off[^0-9]*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            "communication": r"communicat[^0-9]*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            "depth":         r"depth[^0-9]*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
        }
        for dim, pattern in patterns.items():
            m = re.search(pattern, evaluation, re.IGNORECASE)
            if m:
                val = float(m.group(1))
                scores[dim] = min(val, 10.0)  # cap at 10
        return scores

    @staticmethod
    def _extract_insights(
        evaluation: str,
    ) -> tuple[list[str], list[str], list[str]]:
        """Extract strengths, weaknesses, and suggestions from evaluation text."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        suggestions: list[str] = []

        # Very simple heuristic — look for labeled sections
        for line in evaluation.split("\n"):
            stripped = line.strip().lstrip("•-*123456789. ")
            if not stripped:
                continue
            lower = stripped.lower()
            if any(k in lower for k in ("strength", "good", "excellent", "well done")):
                strengths.append(stripped[:200])
            elif any(k in lower for k in ("weakness", "missing", "improve", "lack")):
                weaknesses.append(stripped[:200])
            elif any(k in lower for k in ("suggest", "recommend", "consider", "should")):
                suggestions.append(stripped[:200])

        return strengths[:5], weaknesses[:5], suggestions[:5]

    @staticmethod
    def _calc_level(avg_score: float) -> str:
        """Map average score to experience level label."""
        if avg_score >= 8.5:
            return "expert"
        if avg_score >= 7.0:
            return "advanced"
        if avg_score >= 5.0:
            return "intermediate"
        return "beginner"
