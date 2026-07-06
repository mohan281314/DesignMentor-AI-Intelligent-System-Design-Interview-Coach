"""
Analytics service — performance tracking, recommendations, spaced repetition.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics import PerformanceMetric, UserActivity
from app.models.interview import Interview
from app.models.user import UserProfile

# Topics available for practice
SYSTEM_DESIGN_TOPICS = [
    "URL Shortener", "Twitter / X", "Instagram", "Netflix", "Uber",
    "WhatsApp", "YouTube", "Dropbox", "Google Search", "Airbnb",
    "Amazon", "Spotify", "TikTok", "Slack", "Discord",
    "Rate Limiter", "Distributed Cache", "Message Queue", "CDN",
    "Notification System", "Payment System", "Ride Sharing", "Food Delivery",
]

TOPIC_CATEGORIES = {
    "storage":        ["Dropbox", "Google Drive", "Distributed File System"],
    "messaging":      ["WhatsApp", "Slack", "Discord", "Notification System", "Message Queue"],
    "streaming":      ["Netflix", "YouTube", "TikTok", "Spotify"],
    "social":         ["Twitter / X", "Instagram", "TikTok"],
    "infrastructure": ["URL Shortener", "Rate Limiter", "Distributed Cache", "CDN"],
    "ecommerce":      ["Amazon", "Airbnb", "Uber", "Food Delivery", "Ride Sharing"],
}


class AnalyticsService:
    """Performance analytics, recommendations, and spaced repetition."""

    @staticmethod
    def get_performance_summary(db: Session, user_id: int) -> dict[str, Any]:
        """
        Return a comprehensive performance summary for the user.
        Includes radar chart data, trend over time, topic breakdown.
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return AnalyticsService._empty_summary()

        # Dimension scores (for radar chart)
        radar = {
            "correctness":   round(profile.score_correctness, 2),
            "scalability":   round(profile.score_scalability, 2),
            "tradeoffs":     round(profile.score_tradeoffs, 2),
            "communication": round(profile.score_communication, 2),
            "depth":         round(profile.score_depth, 2),
        }

        # Trend data — last 10 interview scores
        recent_metrics = (
            db.query(PerformanceMetric)
            .filter(
                PerformanceMetric.user_id == user_id,
                PerformanceMetric.metric_type == "interview_score",
                PerformanceMetric.metric_name == "correctness",  # use as proxy for overall
            )
            .order_by(PerformanceMetric.created_at.desc())
            .limit(10)
            .all()
        )
        trend = [
            {"date": m.created_at.strftime("%Y-%m-%d"), "score": m.metric_value}
            for m in reversed(recent_metrics)
        ]

        # Topic breakdown
        topic_metrics = (
            db.query(
                PerformanceMetric.topic,
                func.avg(PerformanceMetric.metric_value).label("avg_score"),
                func.count(PerformanceMetric.id).label("attempts"),
            )
            .filter(
                PerformanceMetric.user_id == user_id,
                PerformanceMetric.metric_type == "interview_score",
                PerformanceMetric.topic.isnot(None),
            )
            .group_by(PerformanceMetric.topic)
            .all()
        )
        topics = [
            {
                "topic": t.topic,
                "avg_score": round(t.avg_score, 2),
                "attempts": t.attempts,
            }
            for t in topic_metrics
        ]

        # Identify weakest dimensions
        weaknesses = sorted(radar.items(), key=lambda x: x[1])[:2]
        weak_dims = [w[0] for w in weaknesses if w[1] < 6.0]

        return {
            "overall_score":    round(profile.average_score, 2),
            "experience_level": profile.experience_level,
            "total_interviews": profile.total_interviews,
            "total_designs":    profile.total_designs,
            "radar":            radar,
            "trend":            trend,
            "topics":           topics,
            "weak_dimensions":  weak_dims,
        }

    @staticmethod
    def get_recommendations(db: Session, user_id: int) -> list[dict[str, str]]:
        """
        Return personalized topic recommendations based on weak areas.
        Uses simple heuristics + spaced repetition logic.
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return AnalyticsService._default_recommendations()

        recs: list[dict[str, str]] = []

        # Identify weakest dimension
        dims = {
            "correctness":   profile.score_correctness,
            "scalability":   profile.score_scalability,
            "tradeoffs":     profile.score_tradeoffs,
            "communication": profile.score_communication,
            "depth":         profile.score_depth,
        }
        weakest_dim = min(dims, key=dims.get)  # type: ignore[arg-type]

        # Get topics the user hasn't tried yet
        attempted_topics = {
            row.topic
            for row in db.query(PerformanceMetric.topic)
            .filter(PerformanceMetric.user_id == user_id)
            .distinct()
            .all()
            if row.topic
        }

        new_topics = [t for t in SYSTEM_DESIGN_TOPICS if t not in attempted_topics]

        # Recommend based on weak dimension
        dim_tips = {
            "scalability":   "Focus on horizontal scaling, sharding, and load balancing.",
            "tradeoffs":     "Practice explaining CAP theorem, consistency vs availability.",
            "communication": "Structure your answer: requirements → design → trade-offs.",
            "correctness":   "Revisit database design, API contracts, and data flow.",
            "depth":         "Go deeper into caching layers, message queues, and monitoring.",
        }

        if weakest_dim in dim_tips and dims[weakest_dim] < 7.0:
            recs.append({
                "type":        "improvement",
                "title":       f"Improve your {weakest_dim.title()} score",
                "description": dim_tips[weakest_dim],
                "topic":       new_topics[0] if new_topics else "Rate Limiter",
            })

        # Add 2 new topics to try
        for topic in new_topics[:2]:
            recs.append({
                "type":        "new_topic",
                "title":       f"Try: {topic}",
                "description": f"You haven't practiced {topic} yet.",
                "topic":       topic,
            })

        # Spaced repetition: re-practice lowest-scoring past topic
        low_score_topic = (
            db.query(PerformanceMetric.topic, func.avg(PerformanceMetric.metric_value))
            .filter(
                PerformanceMetric.user_id == user_id,
                PerformanceMetric.metric_type == "interview_score",
                PerformanceMetric.topic.isnot(None),
            )
            .group_by(PerformanceMetric.topic)
            .order_by(func.avg(PerformanceMetric.metric_value))
            .first()
        )
        if low_score_topic and low_score_topic[1] < 7.0:
            recs.append({
                "type":        "review",
                "title":       f"Review: {low_score_topic[0]}",
                "description": f"Your score was {low_score_topic[1]:.1f}/10 — practice again.",
                "topic":       low_score_topic[0],
            })

        return recs[:5] or AnalyticsService._default_recommendations()

    @staticmethod
    def get_activity_feed(
        db: Session, user_id: int, limit: int = 10
    ) -> list[dict[str, str]]:
        """Return recent user activity for dashboard feed."""
        activities = (
            db.query(UserActivity)
            .filter(UserActivity.user_id == user_id)
            .order_by(UserActivity.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "type":        a.activity_type,
                "description": a.description or "",
                "topic":       a.topic or "",
                "timestamp":   a.created_at.isoformat(),
            }
            for a in activities
        ]

    # ------------------------------------------------------------------
    @staticmethod
    def _empty_summary() -> dict[str, Any]:
        return {
            "overall_score": 0.0,
            "experience_level": "beginner",
            "total_interviews": 0,
            "total_designs": 0,
            "radar": {k: 0.0 for k in ["correctness","scalability","tradeoffs","communication","depth"]},
            "trend": [],
            "topics": [],
            "weak_dimensions": [],
        }

    @staticmethod
    def _default_recommendations() -> list[dict[str, str]]:
        return [
            {"type": "new_topic", "title": "Try: URL Shortener", "description": "Great starting point for system design.", "topic": "URL Shortener"},
            {"type": "new_topic", "title": "Try: Rate Limiter", "description": "Core infrastructure concept every engineer should know.", "topic": "Rate Limiter"},
            {"type": "new_topic", "title": "Try: Twitter / X", "description": "Classic high-scale social media design challenge.", "topic": "Twitter / X"},
        ]
