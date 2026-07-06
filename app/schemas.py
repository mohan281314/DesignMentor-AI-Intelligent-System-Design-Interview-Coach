"""
Pydantic request/response models for all DesignMentor AI endpoints.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class MessageItem(BaseModel):
    """A single turn in a conversation."""

    role: Literal["user", "assistant", "system"]
    content: str


# ---------------------------------------------------------------------------
# /design  –  Generate a full system design
# ---------------------------------------------------------------------------


class DesignRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Instagram"])
    session_id: str | None = Field(
        default=None,
        description="Existing session ID to continue a conversation. "
        "Omit to start a new session.",
    )


class DesignResponse(BaseModel):
    session_id: str
    topic: str
    design: str = Field(..., description="Full markdown system design output")


# ---------------------------------------------------------------------------
# /interview/start  –  Kick off an interview for a topic
# ---------------------------------------------------------------------------


class InterviewStartRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Netflix"])
    session_id: str | None = None


class InterviewStartResponse(BaseModel):
    session_id: str
    topic: str
    first_question: str


# ---------------------------------------------------------------------------
# /interview/answer  –  Submit an answer during an interview
# ---------------------------------------------------------------------------


class InterviewAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Session ID returned by /interview/start")
    answer: str = Field(..., min_length=1, max_length=10_000)


class InterviewAnswerResponse(BaseModel):
    session_id: str
    evaluation: str = Field(..., description="Structured evaluation in markdown")
    next_question: str | None = Field(
        default=None,
        description="Next interview question, or null if the session is complete",
    )
    is_complete: bool = False


# ---------------------------------------------------------------------------
# /evaluate  –  One-shot answer evaluation (no session required)
# ---------------------------------------------------------------------------


class EvaluateRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    user_answer: str = Field(..., min_length=1, max_length=10_000)
    reference: str | None = Field(
        default=None,
        description="Optional reference design or ideal answer to compare against",
    )


class EvaluateResponse(BaseModel):
    evaluation: str = Field(..., description="Scored feedback in markdown")


# ---------------------------------------------------------------------------
# /diagram  –  Generate a Mermaid architecture diagram
# ---------------------------------------------------------------------------


class DiagramRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, examples=["Uber"])
    design_summary: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Text summary of the design to visualise",
    )


class DiagramResponse(BaseModel):
    topic: str
    mermaid_code: str = Field(..., description="Raw Mermaid diagram source")
    explanation: str
    suggestions: list[str]


# ---------------------------------------------------------------------------
# /feedback  –  Post-interview learning report
# ---------------------------------------------------------------------------


class FeedbackRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    session_id: str | None = Field(
        default=None,
        description="If provided, the conversation history for this session is included",
    )


class FeedbackResponse(BaseModel):
    topic: str
    report: str = Field(..., description="Full learning report in markdown")


# ---------------------------------------------------------------------------
# /chat  –  Free-form conversational endpoint
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: Literal["ok", "healthy"] = "ok"
    version: str = "2.0.0"
