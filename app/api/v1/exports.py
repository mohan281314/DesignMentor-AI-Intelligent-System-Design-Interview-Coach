"""PDF export endpoints for designs and interviews."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.interview import Interview
from app.models.user import User
from app.services.design_service import DesignService
from app.utils.pdf_generator import generate_design_pdf, generate_interview_pdf

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/designs/{design_id}/pdf")
async def export_design_pdf(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export a saved design as a PDF file."""
    design = DesignService.get_design_by_id(db, design_id, current_user.id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    pdf_bytes = generate_design_pdf(
        topic=design.topic,
        content=design.content,
        author_name=current_user.full_name,
    )

    # Detect content type (PDF vs HTML fallback)
    content_type = "application/pdf"
    filename = f"design-{design.topic.lower().replace(' ', '-')}.pdf"

    if pdf_bytes[:4] != b"%PDF":  # HTML fallback
        content_type = "text/html"
        filename = filename.replace(".pdf", ".html")

    return Response(
        content=pdf_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/interviews/{interview_id}/pdf")
async def export_interview_pdf(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export a completed interview report as a PDF file."""
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    turns_data = [
        {
            "turn_number": t.turn_number,
            "question":    t.question,
            "answer":      t.answer,
            "evaluation":  t.evaluation,
        }
        for t in interview.turns
    ]
    scores = {
        "overall":       interview.score_overall,
        "correctness":   interview.score_correctness,
        "scalability":   interview.score_scalability,
        "tradeoffs":     interview.score_tradeoffs,
        "communication": interview.score_communication,
        "depth":         interview.score_depth,
    }

    pdf_bytes = generate_interview_pdf(
        topic=interview.topic,
        turns=turns_data,
        scores=scores,
        author_name=current_user.full_name,
    )

    content_type = "application/pdf"
    filename = f"interview-{interview.topic.lower().replace(' ', '-')}.pdf"

    if pdf_bytes[:4] != b"%PDF":
        content_type = "text/html"
        filename = filename.replace(".pdf", ".html")

    return Response(
        content=pdf_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
