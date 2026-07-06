"""Persistent mock interview endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.chains import run_evaluation_chain, run_interview_start_chain, run_next_question_chain
from app.models.user import User
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["Interviews"])

MAX_TURNS = 5


@router.post("/start")
async def start_interview(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new persistent interview session."""
    interview = InterviewService.create_interview(db, current_user.id, topic)
    first_question = await run_interview_start_chain(topic)

    # Store first question in session via interview metadata
    return {
        "interview_id":    interview.id,
        "topic":           topic,
        "first_question":  first_question,
        "turn_number":     1,
        "max_turns":       MAX_TURNS,
        "status":          "in_progress",
    }


@router.post("/{interview_id}/answer")
async def submit_answer(
    interview_id: int,
    question: str,
    answer: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an answer, receive evaluation and next question."""
    interview = db.query(__import__("app.models.interview", fromlist=["Interview"]).Interview).filter_by(
        id=interview_id, user_id=current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview already completed")

    # Evaluate answer
    evaluation = await run_evaluation_chain(question=question, user_answer=answer)

    # Persist turn
    turn = InterviewService.add_turn(db, interview, question, answer, evaluation)

    is_complete = interview.total_turns >= MAX_TURNS

    if is_complete:
        interview = InterviewService.complete_interview(db, interview, current_user.id)
        next_question = None
    else:
        # Build history for next question context
        history = "\n".join([
            f"Q{t.turn_number}: {t.question}\nA{t.turn_number}: {t.answer}"
            for t in interview.turns
        ])
        next_question = await run_next_question_chain(interview.topic, history)

    return {
        "interview_id": interview_id,
        "turn_number":  turn.turn_number,
        "evaluation":   evaluation,
        "scores": {
            "correctness":   turn.score_correctness,
            "scalability":   turn.score_scalability,
            "tradeoffs":     turn.score_tradeoffs,
            "communication": turn.score_communication,
            "depth":         turn.score_depth,
        },
        "next_question":    next_question,
        "is_complete":      is_complete,
        "overall_score":    interview.score_overall if is_complete else None,
    }


@router.get("/")
async def list_my_interviews(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's interview history."""
    interviews, total = InterviewService.get_user_interviews(
        db, current_user.id, limit, offset, status_filter
    )
    return {
        "total": total,
        "interviews": [
            {
                "id":            i.id,
                "topic":         i.topic,
                "status":        i.status,
                "score_overall": round(i.score_overall, 2),
                "total_turns":   i.total_turns,
                "started_at":    i.started_at.isoformat(),
                "completed_at":  i.completed_at.isoformat() if i.completed_at else None,
            }
            for i in interviews
        ],
    }


@router.get("/{interview_id}")
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full interview detail including all turns."""
    from app.models.interview import Interview
    interview = db.query(Interview).filter_by(id=interview_id, user_id=current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return {
        "id":               interview.id,
        "topic":            interview.topic,
        "status":           interview.status,
        "scores": {
            "overall":       round(interview.score_overall, 2),
            "correctness":   round(interview.score_correctness, 2),
            "scalability":   round(interview.score_scalability, 2),
            "tradeoffs":     round(interview.score_tradeoffs, 2),
            "communication": round(interview.score_communication, 2),
            "depth":         round(interview.score_depth, 2),
        },
        "total_turns":      interview.total_turns,
        "started_at":       interview.started_at.isoformat(),
        "completed_at":     interview.completed_at.isoformat() if interview.completed_at else None,
        "turns": [
            {
                "turn_number": t.turn_number,
                "question":    t.question,
                "answer":      t.answer,
                "evaluation":  t.evaluation,
                "scores": {
                    "correctness":   t.score_correctness,
                    "scalability":   t.score_scalability,
                    "tradeoffs":     t.score_tradeoffs,
                    "communication": t.score_communication,
                    "depth":         t.score_depth,
                },
            }
            for t in interview.turns
        ],
    }
