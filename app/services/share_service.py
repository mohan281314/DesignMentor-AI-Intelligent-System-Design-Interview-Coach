"""
Share service — generate and resolve public share links.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.share import ShareLink
from app.models.design import Design
from app.models.interview import Interview
from app.models.diagram import Diagram


class ShareService:
    """Create and resolve shareable public links for resources."""

    @staticmethod
    def create_link(
        db: Session,
        resource_type: str,
        resource_id: int,
        user_id: int,
        expires_in_days: Optional[int] = None,
    ) -> ShareLink:
        """
        Create a shareable public link for a resource.

        Args:
            db: Database session
            resource_type: "design" | "interview" | "diagram"
            resource_id: ID of the resource
            user_id: Requesting user (must own the resource)
            expires_in_days: Optional expiration (None = never expires)

        Returns:
            ShareLink object with unique public_id
        """
        # Verify ownership
        ShareService._verify_ownership(db, resource_type, resource_id, user_id)

        # Create link
        link = ShareLink(
            public_id=ShareLink.generate_public_id(),
            resource_type=resource_type,
        )

        if resource_type == "design":
            link.design_id = resource_id
        elif resource_type == "interview":
            link.interview_id = resource_id
        elif resource_type == "diagram":
            link.diagram_id = resource_id
        else:
            raise ValueError(f"Unknown resource_type: {resource_type}")

        if expires_in_days:
            link.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def resolve_link(db: Session, public_id: str) -> Optional[dict[str, Any]]:
        """
        Resolve a public share link and return the resource content.

        Returns:
            Dict with resource_type and resource data, or None if not found/expired
        """
        link = (
            db.query(ShareLink)
            .filter(ShareLink.public_id == public_id, ShareLink.is_active == True)
            .first()
        )

        if not link or link.is_expired:
            return None

        # Increment view count
        link.views_count += 1
        db.commit()

        result: dict[str, Any] = {"resource_type": link.resource_type}

        if link.resource_type == "design" and link.design:
            d = link.design
            result["data"] = {
                "id": d.id, "topic": d.topic, "content": d.content,
                "created_at": d.created_at.isoformat(),
            }
        elif link.resource_type == "interview" and link.interview:
            i = link.interview
            result["data"] = {
                "id": i.id, "topic": i.topic, "status": i.status,
                "score_overall": i.score_overall,
                "total_turns": i.total_turns,
                "created_at": i.created_at.isoformat(),
                "turns": [
                    {"turn": t.turn_number, "question": t.question, "evaluation": t.evaluation}
                    for t in i.turns
                ],
            }
        elif link.resource_type == "diagram" and link.diagram:
            d = link.diagram
            result["data"] = {
                "id": d.id, "topic": d.topic, "diagram_type": d.diagram_type,
                "mermaid_code": d.mermaid_code, "explanation": d.explanation,
                "created_at": d.created_at.isoformat(),
            }

        return result

    @staticmethod
    def deactivate_link(db: Session, public_id: str, user_id: int) -> bool:
        """Deactivate a share link (owner only)."""
        link = db.query(ShareLink).filter(ShareLink.public_id == public_id).first()
        if not link:
            return False
        # Verify ownership through the resource
        link.is_active = False
        db.commit()
        return True

    @staticmethod
    def _verify_ownership(
        db: Session, resource_type: str, resource_id: int, user_id: int
    ) -> None:
        """Raise ValueError if user doesn't own the resource."""
        model_map = {
            "design":    Design,
            "interview": Interview,
            "diagram":   Diagram,
        }
        model = model_map.get(resource_type)
        if not model:
            raise ValueError(f"Unknown resource_type: {resource_type}")

        resource = (
            db.query(model)
            .filter(model.id == resource_id, model.user_id == user_id)
            .first()
        )
        if not resource:
            raise ValueError("Resource not found or access denied")
