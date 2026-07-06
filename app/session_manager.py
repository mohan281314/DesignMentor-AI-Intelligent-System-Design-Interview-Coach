"""
In-memory session manager for conversation history.

Each session stores:
- topic: the system being designed/discussed
- messages: ordered list of {role, content} dicts (LangChain-compatible)
- metadata: arbitrary dict for interview state (current question index, scores, etc.)

TTL-based expiry is enforced lazily on access and via a background cleanup task
that FastAPI starts on startup.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal data structures
# ---------------------------------------------------------------------------

_STORE: dict[str, "_Session"] = {}


class _Session:
    __slots__ = ("id", "topic", "messages", "metadata", "created_at", "last_accessed")

    def __init__(self, session_id: str, topic: str = "") -> None:
        self.id = session_id
        self.topic = topic
        self.messages: list[dict[str, str]] = []
        self.metadata: dict[str, Any] = {}
        self.created_at = time.time()
        self.last_accessed = time.time()

    def touch(self) -> None:
        self.last_accessed = time.time()

    def is_expired(self, ttl: int) -> bool:
        return (time.time() - self.last_accessed) > ttl


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_session(topic: str = "") -> str:
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())
    _STORE[session_id] = _Session(session_id, topic)
    logger.debug("Session created: %s (topic=%r)", session_id, topic)
    return session_id


def get_session(session_id: str) -> _Session | None:
    """Return the session if it exists and has not expired, else None."""
    settings = get_settings()
    session = _STORE.get(session_id)
    if session is None:
        return None
    if session.is_expired(settings.session_ttl_seconds):
        del _STORE[session_id]
        logger.debug("Session expired on access: %s", session_id)
        return None
    session.touch()
    return session


def get_or_create_session(session_id: str | None, topic: str = "") -> tuple[str, _Session]:
    """
    Return (session_id, session).
    If session_id is None or the session has expired, create a fresh one.
    """
    if session_id:
        session = get_session(session_id)
        if session:
            if topic and not session.topic:
                session.topic = topic
            return session.id, session

    new_id = create_session(topic)
    return new_id, _STORE[new_id]


def add_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the session history."""
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session not found or expired: {session_id}")
    session.messages.append({"role": role, "content": content})


def get_history(session_id: str) -> list[dict[str, str]]:
    """Return the full message history for a session."""
    session = get_session(session_id)
    if session is None:
        return []
    return list(session.messages)


def get_history_as_text(session_id: str) -> str:
    """Return conversation history as a plain-text transcript."""
    messages = get_history(session_id)
    if not messages:
        return "(no history yet)"
    lines = [f"{m['role'].upper()}: {m['content']}" for m in messages]
    return "\n\n".join(lines)


def set_metadata(session_id: str, key: str, value: Any) -> None:
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session not found or expired: {session_id}")
    session.metadata[key] = value


def get_metadata(session_id: str, key: str, default: Any = None) -> Any:
    session = get_session(session_id)
    if session is None:
        return default
    return session.metadata.get(key, default)


def delete_session(session_id: str) -> bool:
    """Explicitly delete a session. Returns True if it existed."""
    existed = session_id in _STORE
    _STORE.pop(session_id, None)
    return existed


def active_session_count() -> int:
    return len(_STORE)


# ---------------------------------------------------------------------------
# Background cleanup task
# ---------------------------------------------------------------------------


async def _cleanup_loop() -> None:
    """Periodically remove expired sessions to prevent unbounded memory growth."""
    settings = get_settings()
    interval = max(60, settings.session_ttl_seconds // 4)
    while True:
        await asyncio.sleep(interval)
        ttl = settings.session_ttl_seconds
        expired = [sid for sid, s in list(_STORE.items()) if s.is_expired(ttl)]
        for sid in expired:
            _STORE.pop(sid, None)
        if expired:
            logger.info("Cleaned up %d expired session(s)", len(expired))


async def start_cleanup_task() -> asyncio.Task:  # type: ignore[type-arg]
    """Schedule the cleanup loop as an asyncio background task."""
    task = asyncio.create_task(_cleanup_loop(), name="session-cleanup")
    logger.info("Session cleanup task started (store=%d active sessions)", len(_STORE))
    return task
