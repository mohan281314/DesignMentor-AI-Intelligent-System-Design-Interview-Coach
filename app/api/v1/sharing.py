"""Public sharing endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.share_service import ShareService

router = APIRouter(prefix="/share", tags=["Sharing"])


@router.post("/create")
async def create_share_link(
    resource_type: str,
    resource_id: int,
    expires_in_days: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a public shareable link for a design, interview, or diagram.

    - resource_type: "design" | "interview" | "diagram"
    - resource_id: ID of the resource to share
    - expires_in_days: Optional expiration (None = never expires)
    """
    try:
        link = ShareService.create_link(
            db=db,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=current_user.id,
            expires_in_days=expires_in_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "public_id":   link.public_id,
        "share_url":   f"/share/{link.public_id}",
        "expires_at":  link.expires_at.isoformat() if link.expires_at else None,
        "resource_type": resource_type,
    }


@router.get("/{public_id}")
async def get_shared_resource(
    public_id: str,
    db: Session = Depends(get_db),
):
    """
    Resolve and return a shared resource by its public ID.
    No authentication required — anyone with the link can view.
    """
    result = ShareService.resolve_link(db, public_id)
    if not result:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    return result


@router.delete("/{public_id}")
async def deactivate_share_link(
    public_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate a share link (owner only)."""
    if not ShareService.deactivate_link(db, public_id, current_user.id):
        raise HTTPException(status_code=404, detail="Share link not found")
    return {"message": "Share link deactivated"}
