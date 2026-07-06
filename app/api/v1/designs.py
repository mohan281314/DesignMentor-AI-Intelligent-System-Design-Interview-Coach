"""Design generation and history endpoints."""

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional, get_db
from app.chains import run_design_chain
from app.models.user import User
from app.services.design_service import DesignService

router = APIRouter(prefix="/designs", tags=["Designs"])


@router.post("/generate")
async def generate_design(
    topic: str,
    save: bool = True,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Generate a complete system design.
    If authenticated and save=True, saves to database for future access.
    """
    start = time.time()
    content = await run_design_chain(topic)
    elapsed = int(time.time() - start)

    result = {
        "topic": topic,
        "design": content,
        "generation_time_seconds": elapsed,
    }

    if current_user and save:
        design = DesignService.save_design(
            db=db,
            user_id=current_user.id,
            topic=topic,
            content=content,
            generation_time_seconds=elapsed,
        )
        result["id"] = design.id
        result["saved"] = True
    else:
        result["saved"] = False

    return result


@router.get("/")
async def list_my_designs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    topic: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved designs for current user."""
    designs, total = DesignService.get_user_designs(
        db, current_user.id, limit, offset, topic
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "designs": [
            {
                "id": d.id,
                "topic": d.topic,
                "word_count": d.word_count,
                "created_at": d.created_at.isoformat(),
                "is_public": d.is_public,
            }
            for d in designs
        ],
    }


@router.get("/{design_id}")
async def get_design(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific saved design."""
    design = DesignService.get_design_by_id(db, design_id, current_user.id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return {
        "id": design.id,
        "topic": design.topic,
        "content": design.content,
        "word_count": design.word_count,
        "estimated_reading_time": design.estimated_reading_time,
        "created_at": design.created_at.isoformat(),
        "is_public": design.is_public,
    }


@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_design(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saved design."""
    if not DesignService.delete_design(db, design_id, current_user.id):
        raise HTTPException(status_code=404, detail="Design not found")
