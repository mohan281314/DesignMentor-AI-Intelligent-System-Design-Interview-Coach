"""
DesignMentor AI v2.1 — Unique Feature Chains

New capabilities:
  1. AI Persona Interviewers   — choose your interviewer character
  2. Failure Mode Analyzer     — production failure simulation
  3. Experience-Aware Design   — level-calibrated designs
  4. Memory-Powered Coach      — long-term memory coaching
  5. Design Battle Mode        — user vs AI judged duel
  6. Smart Learning Roadmap    — 30-day personalised plan
  7. Design Critique Mode      — adversarial design review
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

# Reuse the retry + LLM factory from the main chains module
from app.chains import _invoke_with_retry, _load_prompt, _system_message

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ===========================================================================
# PERSONA DEFINITIONS
# ===========================================================================

PERSONAS: dict[str, dict[str, str]] = {
    "google_staff": {
        "name": "Alex Chen — Ex-Google Staff Engineer",
        "description": (
            "15 years at Google, built core infrastructure for Search and YouTube. "
            "Deeply technical, loves distributed systems. Former tech lead for a 200-person org."
        ),
        "questioning_style": (
            "Starts broad, quickly drills into specifics. Loves asking 'How does that work at Google scale?' "
            "and 'What happens when this component fails?' Expects precise numbers and deep trade-off reasoning."
        ),
        "feedback_tone": (
            "Direct and technical. Praises clever optimisations. Critical of hand-wavy answers. "
            "Uses phrases like 'At Google we would...' and 'Have you considered the tail latency here?'"
        ),
    },
    "meta_e5": {
        "name": "Sarah Park — Meta E5 Engineer",
        "description": (
            "8 years at Meta, worked on News Feed ranking and real-time messaging infrastructure. "
            "Expert in large-scale data systems and developer experience."
        ),
        "questioning_style": (
            "Very pragmatic. Focuses on business impact and user experience alongside technical correctness. "
            "Loves asking about data modelling and API design. Challenges assumptions about scale."
        ),
        "feedback_tone": (
            "Encouraging but thorough. Connects technical decisions to product impact. "
            "Uses Meta's Move Fast philosophy — expects candidates to identify the simplest solution first."
        ),
    },
    "netflix_architect": {
        "name": "Marcus Rivera — Netflix Principal Architect",
        "description": (
            "12 years at Netflix, designed the Chaos Engineering programme and led the cloud migration. "
            "Obsessed with resilience, observability, and developer autonomy."
        ),
        "questioning_style": (
            "Starts with failure scenarios immediately. 'What happens when your database goes down?' "
            "Expects chaos engineering thinking, deep monitoring, and graceful degradation."
        ),
        "feedback_tone": (
            "Passionate about resilience. Will push back hard on any single point of failure. "
            "Rewards candidates who proactively discuss failure modes without being asked."
        ),
    },
    "amazon_sde3": {
        "name": "Priya Sharma — Amazon SDE-3, AWS Platform",
        "description": (
            "10 years at Amazon, built core AWS services. Customer obsession is real for her — "
            "every decision traces back to customer impact and SLA."
        ),
        "questioning_style": (
            "Uses the Amazon Leadership Principles as a lens. Asks about customer impact, "
            "cost optimisation, and operational excellence. Loves the 'working backwards' approach."
        ),
        "feedback_tone": (
            "Structured and thorough. Expects candidates to think about cost, operability, and "
            "the 6-pager document you'd write to justify this system. Presses on SLA and SLO definitions."
        ),
    },
    "kind_mentor": {
        "name": "Dr. Jamie Wu — Kind Mentor & Engineering Coach",
        "description": (
            "20 years in software engineering, now an executive coach who helps engineers "
            "crack FAANG interviews. Patient, encouraging, and pedagogical."
        ),
        "questioning_style": (
            "Guides with hints rather than gotchas. If the candidate is stuck, offers a nudge. "
            "Asks questions to help the candidate think rather than to trip them up."
        ),
        "feedback_tone": (
            "Warm and constructive. Always finds something to praise before pointing out gaps. "
            "Frames weaknesses as growth opportunities. Uses 'What if you considered...' framing."
        ),
    },
    "brutal_critic": {
        "name": "Viktor Sokolov — Brutal Critic, ex-CTO",
        "description": (
            "Ex-CTO of two unicorns, now does advisory. Has seen hundreds of system designs fail in production. "
            "Zero tolerance for hand-waving or buzzword-driven architecture."
        ),
        "questioning_style": (
            "Attacks every weakness immediately. 'This won't work at 1M users, here's why.' "
            "Asks the hardest possible follow-ups. Does not accept vague answers."
        ),
        "feedback_tone": (
            "Blunt to the point of uncomfortable. 'I've seen this architecture fail three times.' "
            "But always technically correct — every critique has a valid engineering basis. "
            "If you survive Viktor, you'll ace any real interview."
        ),
    },
    "startup_cto": {
        "name": "Emma Liu — Startup CTO",
        "description": (
            "CTO of a Series B startup, previously at Stripe. Focused on pragmatism, "
            "speed to market, and building with small teams. Hates over-engineering."
        ),
        "questioning_style": (
            "Challenges complexity. 'Do you really need Kafka here or is a Postgres queue enough?' "
            "Prioritises shipping, iterating, and choosing boring technology. Asks about team size constraints."
        ),
        "feedback_tone": (
            "Refreshingly practical. Praises simplicity. Critical of premature optimisation. "
            "Often says 'Build it simple first, scale when you need to.'"
        ),
    },
}


# ===========================================================================
# 1. AI Persona Interviewer Chains
# ===========================================================================

async def run_persona_interview_start(
    topic: str,
    persona_id: str = "google_staff",
) -> dict[str, Any]:
    """
    Start an interview with a specific AI persona interviewer.

    Returns the first question and the persona details.
    """
    persona = PERSONAS.get(persona_id, PERSONAS["google_staff"])
    template = _load_prompt("persona_interviewer.txt")

    task = (
        f"Ask your opening question to begin the system design interview for: {topic}\n\n"
        "Make it a single, clear opening question that reflects your persona. "
        "Do NOT give away the answer or provide hints. Just the question."
    )

    prompt = template.format(
        persona_name=persona["name"],
        persona_description=persona["description"],
        questioning_style=persona["questioning_style"],
        feedback_tone=persona["feedback_tone"],
        topic=topic,
        history="(Interview just started)",
        task=task,
    )
    messages = [HumanMessage(content=prompt)]
    question = await _invoke_with_retry(messages, {"temperature": 0.7})

    return {
        "persona_id":    persona_id,
        "persona_name":  persona["name"],
        "first_question": question,
        "persona_style": persona["questioning_style"],
    }


async def run_persona_interview_followup(
    topic: str,
    persona_id: str,
    user_answer: str,
    history: str,
    turn_number: int,
    max_turns: int,
) -> dict[str, Any]:
    """
    Continue a persona interview: evaluate the answer and generate next question.
    """
    persona = PERSONAS.get(persona_id, PERSONAS["google_staff"])
    template = _load_prompt("persona_interviewer.txt")

    is_last = turn_number >= max_turns

    if is_last:
        task = (
            f"This is the final turn. The candidate just answered: '{user_answer[:500]}'\n\n"
            "Give comprehensive final feedback in your persona's style. "
            "Include: what they did well, critical gaps, and whether you'd advance them to the next round. "
            "Be specific and true to your character."
        )
    else:
        task = (
            f"The candidate just answered: '{user_answer[:500]}'\n\n"
            "1. React briefly to their answer in character (1-2 sentences — acknowledge or push back)\n"
            "2. Ask your next follow-up question that digs deeper or tests a different angle\n\n"
            "Stay in character. Make it feel like a real interview."
        )

    prompt = template.format(
        persona_name=persona["name"],
        persona_description=persona["description"],
        questioning_style=persona["questioning_style"],
        feedback_tone=persona["feedback_tone"],
        topic=topic,
        history=history,
        task=task,
    )
    messages = [HumanMessage(content=prompt)]
    response = await _invoke_with_retry(messages, {"temperature": 0.6})

    return {
        "response":    response,
        "is_complete": is_last,
        "persona_name": persona["name"],
    }


# ===========================================================================
# 2. Failure Mode Analyzer
# ===========================================================================

async def run_failure_mode_analysis(
    topic: str,
    design_summary: str,
) -> str:
    """
    Analyze a system design for production failure modes.

    Args:
        topic: System name
        design_summary: Brief or detailed description of the design

    Returns:
        Comprehensive failure mode analysis as markdown
    """
    template = _load_prompt("failure_mode_analysis.txt")
    prompt = template.format(topic=topic, design_summary=design_summary)
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.4})


# ===========================================================================
# 3. Experience-Aware Design Generator
# ===========================================================================

LEVEL_DESCRIPTIONS: dict[str, str] = {
    "sde1":      "Junior Engineer (SDE-1) — 0-2 years experience",
    "sde2":      "Mid-level Engineer (SDE-2) — 2-4 years experience",
    "sde3":      "Senior Engineer (SDE-3) — 5-8 years experience",
    "staff":     "Staff Engineer — 8-12 years experience, cross-team impact",
    "principal": "Principal Engineer — 12+ years, org-wide technical direction",
}

COMPANY_FOCUS: dict[str, str] = {
    "google":    "Google",
    "meta":      "Meta (Facebook)",
    "amazon":    "Amazon / AWS",
    "microsoft": "Microsoft",
    "apple":     "Apple",
    "netflix":   "Netflix",
    "uber":      "Uber",
    "airbnb":    "Airbnb",
    "stripe":    "Stripe",
    "any":       "top tech companies",
}


async def run_experience_aware_design(
    topic: str,
    level: str = "sde3",
    years_exp: int = 5,
    tech_stack: str = "general",
    target_companies: str = "any",
) -> str:
    """
    Generate a system design calibrated to the user's seniority level.
    """
    template = _load_prompt("experience_aware_design.txt")
    level_desc = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["sde3"])
    company_str = COMPANY_FOCUS.get(target_companies.lower(), target_companies)

    prompt = template.format(
        topic=topic,
        level=level.upper(),
        level_description=level_desc,
        years_exp=years_exp,
        tech_stack=tech_stack if tech_stack else "general backend (Python/Java/Go)",
        target_companies=company_str,
    )
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.5})


# ===========================================================================
# 4. Memory-Powered Coach
# ===========================================================================

async def run_memory_coach(
    message: str,
    user_profile: dict[str, Any],
    history: list[dict[str, str]] | None = None,
) -> str:
    """
    Memory-powered coaching chat that references the user's past performance.

    Args:
        message: User's current question
        user_profile: Dict with level, scores, weak/strong areas, past topics, etc.
        history: Recent conversation history
    """
    from langchain_core.messages import AIMessage

    template = _load_prompt("memory_coach.txt")

    # Build history string
    history_text = ""
    if history:
        lines = []
        for msg in history[-8:]:  # Last 8 turns
            role = "You" if msg["role"] == "user" else "Coach"
            lines.append(f"{role}: {msg['content'][:300]}")
        history_text = "\n".join(lines)

    # Build recent mistakes from profile
    recent_mistakes = user_profile.get("weak_topics") or "none identified yet"
    past_topics     = user_profile.get("past_topics") or "none yet"
    strong_areas    = user_profile.get("strong_topics") or "none identified yet"

    prompt = template.format(
        experience_level=user_profile.get("experience_level", "beginner"),
        overall_score=user_profile.get("average_score", 0.0),
        weak_areas=recent_mistakes,
        strong_areas=strong_areas,
        past_topics=past_topics,
        total_sessions=user_profile.get("total_interviews", 0),
        recent_mistakes=recent_mistakes,
        learning_goals=user_profile.get("preferred_topics") or "improve overall system design skills",
        message=message,
        history=history_text or "(No previous conversation)",
    )

    messages = [HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.7})


# ===========================================================================
# 5. Design Battle Mode
# ===========================================================================

async def generate_ai_battle_design(topic: str) -> str:
    """Generate the AI's own design for the battle topic."""
    from app.chains import run_design_chain
    # Use the existing design chain — the AI designs the same system
    return await run_design_chain(topic)


async def run_design_battle(
    topic: str,
    user_design: str,
) -> dict[str, Any]:
    """
    Run a Design Battle: judge user's design vs an AI-generated design.

    Returns structured battle result with scores and verdict.
    """
    import asyncio

    # Generate AI design in parallel with loading template
    ai_design = await generate_ai_battle_design(topic)

    template = _load_prompt("design_battle.txt")
    prompt = template.format(
        topic=topic,
        user_design=user_design,
        ai_design=ai_design,
    )
    messages = [_system_message(), HumanMessage(content=prompt)]
    judgment = await _invoke_with_retry(messages, {"temperature": 0.3})

    return {
        "topic":      topic,
        "ai_design":  ai_design,
        "judgment":   judgment,
    }


# ===========================================================================
# 6. Smart 30-Day Learning Roadmap
# ===========================================================================

async def run_learning_roadmap(
    user_profile: dict[str, Any],
    target_companies: str = "FAANG",
    target_level: str = "SDE-3",
    timeline_weeks: int = 4,
) -> str:
    """
    Generate a personalised learning roadmap based on user's profile.
    """
    template = _load_prompt("learning_roadmap.txt")

    # Extract profile data
    weak_areas  = user_profile.get("weak_topics") or "databases, caching, consistency"
    strong_areas = user_profile.get("strong_topics") or "basic API design"
    past_topics = user_profile.get("past_topics") or "URL Shortener, Twitter"
    avg_score   = user_profile.get("average_score", 0.0)

    # Estimate target score based on level
    target_score_map = {
        "SDE-1": 5.0, "SDE-2": 6.5, "SDE-3": 7.5,
        "Staff": 8.5, "Principal": 9.0,
    }
    target_score = target_score_map.get(target_level, 7.5)

    prompt = template.format(
        experience_level=user_profile.get("experience_level", "beginner"),
        overall_score=f"{avg_score:.1f}",
        weak_areas=weak_areas,
        strong_areas=strong_areas,
        target_companies=target_companies,
        target_level=target_level,
        timeline_weeks=timeline_weeks,
        practiced_topics=past_topics,
        current_score=f"{avg_score:.1f}",
        target_score=f"{target_score:.1f}",
    )
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.5})


# ===========================================================================
# 7. Design Critique Mode (Adversarial Review)
# ===========================================================================

CRITIQUE_MODES: dict[str, dict[str, str]] = {
    "google": {
        "company": "Google",
        "mode_instructions": (
            "Focus specifically on: scalability to billion users, "
            "distributed systems correctness, and engineering elegance. "
            "Google values simplicity — call out unnecessary complexity."
        ),
    },
    "amazon": {
        "company": "Amazon",
        "mode_instructions": (
            "Evaluate through Amazon's lens: operational excellence, "
            "cost optimisation, customer obsession, and 'two-pizza team' operability. "
            "Does this system have clear ownership and runbooks?"
        ),
    },
    "netflix": {
        "company": "Netflix",
        "mode_instructions": (
            "Evaluate resilience first. Does this design survive chaos engineering? "
            "Is there graceful degradation? Strong observability? Netflix ships hundreds of "
            "deployments per day — is this system safe to deploy continuously?"
        ),
    },
    "startup": {
        "company": "a fast-moving startup",
        "mode_instructions": (
            "Evaluate for pragmatism and speed. Is this over-engineered for the stage? "
            "Could you build this with 3 engineers in 3 months? "
            "What would you cut to ship an MVP in 4 weeks?"
        ),
    },
    "adversarial": {
        "company": "a top tech company",
        "mode_instructions": (
            "Act as the most adversarial reviewer possible. "
            "Find every flaw, challenge every assumption, and probe every trade-off. "
            "This mode is designed to stress-test the design thoroughly."
        ),
    },
}


async def run_design_critique(
    topic: str,
    design: str,
    mode: str = "adversarial",
) -> str:
    """
    Run an adversarial design critique.

    Args:
        topic: System name
        design: The design to critique (markdown text)
        mode: Review mode — 'google', 'amazon', 'netflix', 'startup', 'adversarial'
    """
    mode_config = CRITIQUE_MODES.get(mode, CRITIQUE_MODES["adversarial"])
    template    = _load_prompt("design_critique.txt")

    prompt = template.format(
        company=mode_config["company"],
        topic=topic,
        design=design[:6000],  # Cap to avoid token overflow
        mode=mode.capitalize(),
        mode_instructions=mode_config["mode_instructions"],
    )
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.4})


# ===========================================================================
# Expose personas list for the API
# ===========================================================================

def get_available_personas() -> list[dict[str, str]]:
    """Return list of available interviewer personas for the API."""
    return [
        {
            "id":    persona_id,
            "name":  data["name"],
            "style": data["questioning_style"][:100] + "...",
        }
        for persona_id, data in PERSONAS.items()
    ]
