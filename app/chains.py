"""
LangChain chains for DesignMentor AI.

Supports:
  - Groq (default, free tier) with automatic retry on rate-limit
  - OpenAI as optional fallback
  - Exponential back-off so 429s are transparent to the caller
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# ---------------------------------------------------------------------------
# Retry / back-off constants
# ---------------------------------------------------------------------------
_MAX_RETRIES   = 4          # attempts before giving up
_RETRY_BASE    = 5          # seconds – first wait
_RETRY_MAX     = 60         # seconds – cap on back-off sleep
_RATE_LIMIT_CODES = {429}   # HTTP status codes that trigger retry


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _system_message() -> SystemMessage:
    return SystemMessage(content=_load_prompt("system.txt"))


# ---------------------------------------------------------------------------
# LLM factory  (Groq + optional OpenAI fallback)
# ---------------------------------------------------------------------------

def _get_llm(**overrides: Any) -> ChatGroq:
    """Return a ChatGroq instance with optional parameter overrides."""
    settings = get_settings()
    return ChatGroq(
        model=settings.groq_model,
        temperature=overrides.get("temperature", settings.openai_temperature),
        max_tokens=overrides.get("max_tokens", settings.openai_max_tokens),
        api_key=settings.groq_api_key,
    )


def _get_openai_llm(**overrides: Any):
    """Return an OpenAI ChatLLM (used as fallback when Groq quota exhausted)."""
    try:
        from langchain_openai import ChatOpenAI
        settings = get_settings()
        if not settings.openai_api_key:
            return None
        return ChatOpenAI(
            model=getattr(settings, "openai_model", "gpt-4-turbo-preview"),
            temperature=overrides.get("temperature", settings.openai_temperature),
            max_tokens=overrides.get("max_tokens", settings.openai_max_tokens),
            api_key=settings.openai_api_key,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Resilient invoke  (handles rate-limits transparently)
# ---------------------------------------------------------------------------

async def _invoke_with_retry(
    messages: list,
    llm_kwargs: dict | None = None,
    fallback_to_openai: bool = True,
) -> str:
    """
    Invoke the LLM with exponential back-off on rate-limit (429) errors.

    Flow:
      1. Try Groq up to _MAX_RETRIES times with growing sleep.
      2. If still failing AND fallback_to_openai is True AND an OpenAI key
         exists, try OpenAI once.
      3. Otherwise raise a user-friendly HTTPException.

    Args:
        messages: List of LangChain message objects.
        llm_kwargs: Optional kwargs forwarded to _get_llm().
        fallback_to_openai: Whether to try OpenAI when Groq fails.

    Returns:
        LLM response content string.
    """
    from fastapi import HTTPException, status

    llm_kwargs = llm_kwargs or {}
    last_error: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            llm = _get_llm(**llm_kwargs)
            response = await llm.ainvoke(messages)
            return response.content

        except Exception as exc:
            last_error = exc
            exc_str = str(exc).lower()

            # Detect rate-limit / quota errors
            is_rate_limit = (
                "429" in exc_str
                or "rate limit" in exc_str
                or "too many requests" in exc_str
                or "rate_limit" in exc_str
            )

            if is_rate_limit and attempt < _MAX_RETRIES:
                # Extract retry-after if present, otherwise use exponential back-off
                retry_after = _parse_retry_after(exc_str)
                wait = retry_after or min(_RETRY_BASE * (2 ** (attempt - 1)), _RETRY_MAX)
                logger.warning(
                    "Groq rate limit hit (attempt %d/%d). Retrying in %.0fs…",
                    attempt, _MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                continue

            # Non-rate-limit error – log and break
            logger.error("LLM call failed (attempt %d): %s", attempt, exc)
            break

    # --- Fallback to OpenAI ---
    if fallback_to_openai:
        openai_llm = _get_openai_llm(**llm_kwargs)
        if openai_llm is not None:
            try:
                logger.info("Falling back to OpenAI after Groq failure.")
                response = await openai_llm.ainvoke(messages)
                return response.content
            except Exception as exc:
                logger.error("OpenAI fallback also failed: %s", exc)
                last_error = exc

    # Nothing worked – raise a clean error for the API layer
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "The AI service is temporarily rate-limited. "
            "Please wait 60 seconds and try again. "
            f"(detail: {last_error})"
        ),
    )


def _parse_retry_after(error_text: str) -> float | None:
    """Try to extract 'retry after N seconds' from error message."""
    match = re.search(r"retry.{0,20}?(\d+(?:\.\d+)?)\s*s", error_text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


# ===========================================================================
# 1. Design Generator
# ===========================================================================

async def run_design_chain(topic: str) -> str:
    """Generate a complete production-grade system design for the given topic."""
    template = _load_prompt("design_generator.txt")
    prompt = template.format(topic=topic)
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages)


# ===========================================================================
# 2. Interview Question Generator
# ===========================================================================

async def run_interview_start_chain(topic: str, history: str = "") -> str:
    """Generate the opening interview question for a topic."""
    template = _load_prompt("interview_questions.txt")
    prompt = template.format(topic=topic, history=history or "(no history yet)")
    messages = [_system_message(), HumanMessage(content=prompt)]
    text = await _invoke_with_retry(messages, {"temperature": 0.5})
    return _extract_first_question(text)


async def run_next_question_chain(topic: str, history: str) -> str:
    """Generate the next interview question based on conversation history."""
    template = _load_prompt("interview_questions.txt")
    prompt = template.format(topic=topic, history=history)
    messages = [_system_message(), HumanMessage(content=prompt)]
    text = await _invoke_with_retry(messages, {"temperature": 0.5})
    return _extract_first_question(text)


def _extract_first_question(text: str) -> str:
    """Pull the first question out of a multi-question response."""
    parts = re.split(r"\n{2,}|\n(?=\d+[\.\)])", text.strip())
    for part in parts:
        part = part.strip()
        if part and "?" in part:
            return part
    return text.strip()


# ===========================================================================
# 3. Answer Evaluator
# ===========================================================================

async def run_evaluation_chain(
    question: str,
    user_answer: str,
    reference: str | None = None,
) -> str:
    """Evaluate a user's answer with scoring across 5 dimensions."""
    template = _load_prompt("answer_evaluator.txt")
    prompt = template.format(
        question=question,
        user_answer=user_answer,
        reference=reference or "(none provided)",
    )
    messages = [_system_message(), HumanMessage(content=prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.3})


# ===========================================================================
# 4. Diagram Generator  (multi-type)
# ===========================================================================

_DIAGRAM_PROMPT_MAP: dict[str, str] = {
    "flowchart": "diagram_generator.txt",
    "c4":        "diagram_c4.txt",
    "sequence":  "diagram_sequence.txt",
    "erd":       "diagram_erd.txt",
    "dataflow":  "diagram_dataflow.txt",
}


async def run_diagram_chain(
    topic: str,
    design_summary: str,
    diagram_type: str = "flowchart",
) -> dict[str, Any]:
    """
    Generate a Mermaid diagram and parse the output.

    Args:
        topic: System name (e.g. "Uber")
        design_summary: Brief description of the system
        diagram_type: One of flowchart | c4 | sequence | erd | dataflow
    """
    prompt_file = _DIAGRAM_PROMPT_MAP.get(diagram_type, "diagram_generator.txt")
    template = _load_prompt(prompt_file)
    prompt = template.format(topic=topic, design_summary=design_summary)
    messages = [_system_message(), HumanMessage(content=prompt)]
    content = await _invoke_with_retry(messages, {"temperature": 0.4})
    result = _parse_diagram_response(content)
    result["diagram_type"] = diagram_type
    return result


def _parse_diagram_response(content: str) -> dict[str, Any]:
    """Parse LLM response into structured mermaid_code / explanation / suggestions."""
    # Extract Mermaid code block
    mermaid_match = re.search(r"```(?:mermaid)?\s*([\s\S]+?)```", content, re.IGNORECASE)
    mermaid_code = mermaid_match.group(1).strip() if mermaid_match else ""

    # Remainder (explanation + suggestions)
    remainder = (
        content
        if not mermaid_match
        else (content[: mermaid_match.start()] + content[mermaid_match.end():]).strip()
    )

    # Extract bullet suggestions
    suggestion_lines = re.findall(r"(?:^|\n)\s*[-*\d]+[.)]\s*(.+)", remainder)
    suggestions = [s.strip() for s in suggestion_lines if s.strip()][:3]

    # Clean explanation text
    explanation_text = re.sub(r"\n\s*[-*\d]+[.)]\s*.+", "", remainder).strip()
    explanation_text = re.sub(r"(?i)suggestions?:?\s*", "", explanation_text).strip()

    return {
        "mermaid_code": mermaid_code or content,
        "explanation": explanation_text or "(see diagram above)",
        "suggestions": suggestions or [],
    }


# ===========================================================================
# 5. Feedback & Learning Resources
# ===========================================================================

async def run_feedback_chain(topic: str, history: str = "") -> str:
    """Generate a post-interview learning report with resources and tips."""
    template = _load_prompt("feedback_resources.txt")
    base_prompt = template.format(topic=topic)
    if history and history != "(no history yet)":
        full_prompt = f"{base_prompt}\n\n---\n**Conversation History**:\n\n{history}"
    else:
        full_prompt = base_prompt
    messages = [_system_message(), HumanMessage(content=full_prompt)]
    return await _invoke_with_retry(messages, {"temperature": 0.4})


# ===========================================================================
# 6. Free-form Coaching Chat (with full history)
# ===========================================================================

async def run_chat_chain(
    user_message: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Carry on a context-aware coaching conversation."""
    messages: list[Any] = [_system_message()]
    for item in history or []:
        role    = item.get("role", "user")
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_message))
    return await _invoke_with_retry(messages)
