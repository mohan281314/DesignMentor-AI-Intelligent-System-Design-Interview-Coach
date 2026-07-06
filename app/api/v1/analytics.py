"""Analytics and performance tracking endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/performance")
async def get_performance_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive performance summary.
    Includes radar chart data, trend over time, topic breakdown,
    and identified weak dimensions.
    """
    return AnalyticsService.get_performance_summary(db, current_user.id)


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized practice recommendations.
    Based on weak areas, untried topics, and spaced repetition.
    """
    return AnalyticsService.get_recommendations(db, current_user.id)


@router.get("/activity")
async def get_activity_feed(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent user activity for dashboard feed."""
    return AnalyticsService.get_activity_feed(db, current_user.id, limit)
