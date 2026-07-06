"""
DesignMentor AI v2.1 — Unique Feature Endpoints

All 7 premium features that differentiate this platform:
  POST /api/v1/unique/personas               — list all AI interviewer personas
  POST /api/v1/unique/persona-interview/start — start persona-based interview
  POST /api/v1/unique/persona-interview/answer — continue persona interview
  POST /api/v1/unique/failure-analysis        — production failure mode analysis
  POST /api/v1/unique/design/experience-aware — level-calibrated design
  POST /api/v1/unique/memory-coach            — memory-powered coaching chat
  POST /api/v1/unique/design-battle           — user vs AI design battle
  POST /api/v1/unique/roadmap                 — personalised 30-day learning plan
  POST /api/v1/unique/design-critique         — adversarial design review
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional, get_db
from app.chains_v21 import (
    CRITIQUE_MODES,
    LEVEL_DESCRIPTIONS,
    get_available_personas,
    run_design_battle,
    run_design_critique,
    run_experience_aware_design,
    run_failure_mode_analysis,
    run_learning_roadmap,
    run_memory_coach,
    run_persona_interview_followup,
    run_persona_interview_start,
)
from app.models.user import User, UserProfile

router = APIRouter(prefix="/unique", tags=["v2.1 Unique Features"])


# ─── Request / Response Models ────────────────────────────────────────────────


class PersonaInterviewStartRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Netflix"])
    persona_id: str = Field(default="google_staff", examples=["netflix_architect"])


class PersonaInterviewAnswerRequest(BaseModel):
    topic: str
    persona_id: str
    answer: str = Field(..., min_length=1, max_length=10_000)
    history: str = Field(default="", description="Full conversation history as text")
    turn_number: int = Field(default=1, ge=1)
    max_turns: int = Field(default=5, ge=1, le=10)


class FailureAnalysisRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    design_summary: str = Field(
        ..., min_length=20, max_length=8000,
        description="Paste your full system design here for analysis"
    )


class ExperienceAwareDesignRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Twitter"])
    level: str = Field(
        default="sde3",
        description="sde1 | sde2 | sde3 | staff | principal"
    )
    years_exp: int = Field(default=5, ge=0, le=40)
    tech_stack: str = Field(
        default="general",
        max_length=200,
        examples=["Python, PostgreSQL, Redis, AWS"]
    )
    target_companies: str = Field(
        default="any",
        max_length=200,
        examples=["google"]
    )


class MemoryCoachRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    history: Optional[list[dict]] = Field(
        default=None,
        description="Recent conversation history [{role, content}]"
    )


class DesignBattleRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Instagram"])
    user_design: str = Field(
        ..., min_length=100, max_length=15_000,
        description="Your complete system design (markdown)"
    )


class RoadmapRequest(BaseModel):
    target_companies: str = Field(default="FAANG", max_length=200)
    target_level: str = Field(
        default="SDE-3",
        description="SDE-1 | SDE-2 | SDE-3 | Staff | Principal"
    )
    timeline_weeks: int = Field(default=4, ge=1, le=12)


class DesignCritiqueRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Uber"])
    design: str = Field(
        ..., min_length=100, max_length=15_000,
        description="Your complete system design to critique (markdown)"
    )
    mode: str = Field(
        default="adversarial",
        description="google | amazon | netflix | startup | adversarial"
    )


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _build_user_profile_dict(db: Session, user: User) -> dict:
    """Build a user profile dict for the memory/roadmap chains."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    # Gather past interview topics from activity log
    from app.models.analytics import UserActivity
    past_activities = (
        db.query(UserActivity)
        .filter(
            UserActivity.user_id == user.id,
            UserActivity.activity_type == "interview_completed",
        )
        .order_by(UserActivity.created_at.desc())
        .limit(10)
        .all()
    )
    past_topics = ", ".join(a.topic for a in past_activities if a.topic) or "none yet"

    if not profile:
        return {
            "experience_level": "beginner",
            "average_score":    0.0,
            "weak_topics":      None,
            "strong_topics":    None,
            "past_topics":      past_topics,
            "total_interviews": 0,
            "preferred_topics": None,
        }

    return {
        "experience_level": profile.experience_level,
        "average_score":    profile.average_score,
        "weak_topics":      profile.weak_topics,
        "strong_topics":    profile.strong_topics,
        "past_topics":      past_topics,
        "total_interviews": profile.total_interviews,
        "preferred_topics": profile.preferred_topics,
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("/personas")
async def list_personas():
    """
    Get all available AI interviewer personas.

    Returns a list of personas with their name and style summary.
    Use the returned `id` in persona-interview endpoints.
    """
    return {
        "personas": get_available_personas(),
        "total": len(get_available_personas()),
    }


@router.get("/levels")
async def list_experience_levels():
    """Get all available experience levels for experience-aware design."""
    return {
        "levels": [
            {"id": k, "description": v}
            for k, v in LEVEL_DESCRIPTIONS.items()
        ]
    }


@router.get("/critique-modes")
async def list_critique_modes():
    """Get all available design critique modes."""
    return {
        "modes": [
            {"id": k, "company": v["company"]}
            for k, v in CRITIQUE_MODES.items()
        ]
    }


# ── 1. Persona Interviews ─────────────────────────────────────────────────────


@router.post("/persona-interview/start")
async def start_persona_interview(req: PersonaInterviewStartRequest):
    """
    Start an interview with a specific AI persona interviewer.

    Choose from: google_staff, meta_e5, netflix_architect, amazon_sde3,
                 kind_mentor, brutal_critic, startup_cto
    """
    result = await run_persona_interview_start(req.topic, req.persona_id)
    return result


@router.post("/persona-interview/answer")
async def answer_persona_interview(req: PersonaInterviewAnswerRequest):
    """
    Submit your answer during a persona interview.

    The persona will react in character and ask a follow-up question
    (or give final feedback on the last turn).
    """
    result = await run_persona_interview_followup(
        topic=req.topic,
        persona_id=req.persona_id,
        user_answer=req.answer,
        history=req.history,
        turn_number=req.turn_number,
        max_turns=req.max_turns,
    )
    return result


# ── 2. Failure Mode Analysis ──────────────────────────────────────────────────


@router.post("/failure-analysis")
async def analyze_failure_modes(req: FailureAnalysisRequest):
    """
    Analyze your system design for production failure modes.

    Simulates real-world failures: cascading failures, single points of failure,
    thundering herd, data consistency issues, security gaps.
    Returns chaos engineering experiments and a resilience score.
    """
    analysis = await run_failure_mode_analysis(req.topic, req.design_summary)
    return {
        "topic":    req.topic,
        "analysis": analysis,
    }


# ── 3. Experience-Aware Design ────────────────────────────────────────────────


@router.post("/design/experience-aware")
async def generate_experience_aware_design(req: ExperienceAwareDesignRequest):
    """
    Generate a system design calibrated to your exact seniority level.

    Levels: sde1 (0-2yr), sde2 (2-4yr), sde3 (5-8yr), staff (8-12yr), principal (12+yr)

    The design adjusts depth, complexity, trade-off reasoning, and talking
    points to match what's expected at your target level.
    """
    if req.level not in LEVEL_DESCRIPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid level '{req.level}'. Valid values: {list(LEVEL_DESCRIPTIONS.keys())}"
        )

    design = await run_experience_aware_design(
        topic=req.topic,
        level=req.level,
        years_exp=req.years_exp,
        tech_stack=req.tech_stack,
        target_companies=req.target_companies,
    )
    return {
        "topic":            req.topic,
        "level":            req.level,
        "years_exp":        req.years_exp,
        "target_companies": req.target_companies,
        "design":           design,
    }


# ── 4. Memory-Powered Coach ───────────────────────────────────────────────────


@router.post("/memory-coach")
async def memory_coach_chat(
    req: MemoryCoachRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Chat with your memory-powered personal coach.

    When authenticated, the coach remembers your past weaknesses, interview history,
    and learning patterns — giving advice specifically tailored to YOU.
    Anonymous users get generic coaching.
    """
    if current_user:
        user_profile = _build_user_profile_dict(db, current_user)
    else:
        # Guest: empty profile
        user_profile = {
            "experience_level": "unknown",
            "average_score":    0.0,
            "weak_topics":      None,
            "strong_topics":    None,
            "past_topics":      "none",
            "total_interviews": 0,
            "preferred_topics": None,
        }

    reply = await run_memory_coach(
        message=req.message,
        user_profile=user_profile,
        history=req.history,
    )
    return {
        "reply":         reply,
        "is_personalised": current_user is not None,
    }


# ── 5. Design Battle ──────────────────────────────────────────────────────────


@router.post("/design-battle")
async def design_battle(req: DesignBattleRequest):
    """
    Challenge the AI to a Design Battle!

    You and the AI both design the same system. An impartial AI judge
    scores both on 5 criteria and declares a winner with full reasoning.

    Note: This uses 2 LLM calls (AI design + judging) so takes ~30 seconds.
    """
    result = await run_design_battle(req.topic, req.user_design)
    return result


# ── 6. Smart Learning Roadmap ─────────────────────────────────────────────────


@router.post("/roadmap")
async def generate_learning_roadmap(
    req: RoadmapRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Generate your personalised 30-day system design learning roadmap.

    When authenticated, the roadmap is calibrated to your actual performance
    data, weak areas, and past interview topics.
    """
    if current_user:
        user_profile = _build_user_profile_dict(db, current_user)
    else:
        user_profile = {
            "experience_level": "beginner",
            "average_score":    0.0,
            "weak_topics":      "databases, caching, consistency",
            "strong_topics":    "basic API design",
            "past_topics":      "URL Shortener",
            "total_interviews": 0,
            "preferred_topics": None,
        }

    roadmap = await run_learning_roadmap(
        user_profile=user_profile,
        target_companies=req.target_companies,
        target_level=req.target_level,
        timeline_weeks=req.timeline_weeks,
    )
    return {
        "target_companies":  req.target_companies,
        "target_level":      req.target_level,
        "timeline_weeks":    req.timeline_weeks,
        "is_personalised":   current_user is not None,
        "roadmap":           roadmap,
    }


# ── 7. Design Critique ────────────────────────────────────────────────────────


@router.post("/design-critique")
async def critique_design(req: DesignCritiqueRequest):
    """
    Submit your design for an adversarial expert review.

    Modes:
    - **adversarial**: Finds every possible flaw (hardest)
    - **google**: Google-style review (scale, elegance, simplicity)
    - **amazon**: Amazon-style (operations, cost, customer obsession)
    - **netflix**: Netflix-style (resilience, chaos, continuous delivery)
    - **startup**: Startup lens (pragmatism, speed, avoid over-engineering)
    """
    if req.mode not in CRITIQUE_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Valid: {list(CRITIQUE_MODES.keys())}"
        )

    critique = await run_design_critique(req.topic, req.design, req.mode)
    return {
        "topic":   req.topic,
        "mode":    req.mode,
        "critique": critique,
    }
