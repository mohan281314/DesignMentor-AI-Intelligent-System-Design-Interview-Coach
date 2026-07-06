"""
Enhanced session manager with Redis persistence.
Replaces in-memory session storage with Redis-backed sessions.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.db.redis import redis_client

settings = get_settings()


class SessionManager:
    """
    Redis-backed session manager for user sessions.
    
    Stores session data in Redis with automatic expiration.
    Session data includes conversation history, metadata, and context.
    """
    
    def __init__(self):
        self.ttl = settings.session_ttl_seconds
        self.redis = redis_client
    
    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"session:{session_id}"
    
    def _history_key(self, session_id: str) -> str:
        """Generate Redis key for session message history."""
        return f"session:{session_id}:history"
    
    def _metadata_key(self, session_id: str) -> str:
        """Generate Redis key for session metadata."""
        return f"session:{session_id}:meta"
    
    async def create_session(
        self,
        user_id: int | None = None,
        topic: str | None = None,
        session_type: str = "general"
    ) -> str:
        """
        Create a new session.
        
        Args:
            user_id: Optional user ID for authenticated sessions
            topic: Optional topic/context for the session
            session_type: Type of session (general, interview, design, chat)
        
        Returns:
            New session ID
        """
        session_id = str(uuid4())
        
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "topic": topic,
            "type": session_type,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }
        
        await self.redis.set(
            self._session_key(session_id),
            json.dumps(session_data),
            ex=self.ttl
        )
        
        # Initialize empty history
        await self.redis.set(
            self._history_key(session_id),
            json.dumps([]),
            ex=self.ttl
        )
        
        # Initialize empty metadata
        await self.redis.set(
            self._metadata_key(session_id),
            json.dumps({}),
            ex=self.ttl
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session data.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data dict or None if not found
        """
        data = await self.redis.get(self._session_key(session_id))
        if data:
            # Refresh TTL on access
            await self.redis.expire(self._session_key(session_id), self.ttl)
            await self.redis.expire(self._history_key(session_id), self.ttl)
            await self.redis.expire(self._metadata_key(session_id), self.ttl)
            return json.loads(data)
        return None
    
    async def get_or_create_session(
        self,
        session_id: str | None = None,
        user_id: int | None = None,
        topic: str | None = None,
        session_type: str = "general"
    ) -> tuple[str, bool]:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Optional existing session ID
            user_id: Optional user ID
            topic: Optional topic
            session_type: Session type
        
        Returns:
            Tuple of (session_id, was_created)
        """
        if session_id:
            session = await self.get_session(session_id)
            if session:
                # Update last activity
                session["last_activity"] = datetime.utcnow().isoformat()
                await self.redis.set(
                    self._session_key(session_id),
                    json.dumps(session),
                    ex=self.ttl
                )
                return session_id, False
        
        # Create new session
        new_session_id = await self.create_session(user_id, topic, session_type)
        return new_session_id, True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its data.
        
        Args:
            session_id: Session ID to delete
        
        Returns:
            True if session existed and was deleted
        """
        keys = [
            self._session_key(session_id),
            self._history_key(session_id),
            self._metadata_key(session_id),
        ]
        deleted = await self.redis.delete(*keys)
        return deleted > 0
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to session history.
        
        Args:
            session_id: Session ID
            role: Message role ("user" or "assistant")
            content: Message content
        """
        history = await self.get_history(session_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        await self.redis.set(
            self._history_key(session_id),
            json.dumps(history),
            ex=self.ttl
        )
    
    async def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """
        Get message history for session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of message dicts with role, content, timestamp
        """
        data = await self.redis.get(self._history_key(session_id))
        if data:
            return json.loads(data)
        return []
    
    async def get_history_as_text(self, session_id: str) -> str:
        """
        Get message history as formatted text.
        
        Args:
            session_id: Session ID
        
        Returns:
            Formatted string of conversation history
        """
        history = await self.get_history(session_id)
        lines = []
        for msg in history:
            role = msg["role"].capitalize()
            content = msg["content"]
            lines.append(f"{role}: {content}\n")
        return "\n".join(lines)
    
    async def set_metadata(self, session_id: str, key: str, value: Any) -> None:
        """
        Set metadata value for session.
        
        Args:
            session_id: Session ID
            key: Metadata key
            value: Metadata value (will be JSON serialized)
        """
        metadata = await self.get_metadata_all(session_id)
        metadata[key] = value
        
        await self.redis.set(
            self._metadata_key(session_id),
            json.dumps(metadata),
            ex=self.ttl
        )
    
    async def get_metadata(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Get metadata value from session.
        
        Args:
            session_id: Session ID
            key: Metadata key
            default: Default value if key not found
        
        Returns:
            Metadata value or default
        """
        metadata = await self.get_metadata_all(session_id)
        return metadata.get(key, default)
    
    async def get_metadata_all(self, session_id: str) -> dict[str, Any]:
        """
        Get all metadata for session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Metadata dict
        """
        data = await self.redis.get(self._metadata_key(session_id))
        if data:
            return json.loads(data)
        return {}
    
    async def extend_ttl(self, session_id: str, extra_seconds: int = 0) -> bool:
        """
        Extend session TTL.
        
        Args:
            session_id: Session ID
            extra_seconds: Additional seconds to add (0 = reset to default TTL)
        
        Returns:
            True if successful
        """
        ttl = self.ttl + extra_seconds
        
        keys = [
            self._session_key(session_id),
            self._history_key(session_id),
            self._metadata_key(session_id),
        ]
        
        for key in keys:
            await self.redis.expire(key, ttl)
        
        return True
    
    async def list_user_sessions(self, user_id: int) -> list[dict[str, Any]]:
        """
        List all active sessions for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of session data dicts
        """
        # Note: This is a simple implementation
        # For better performance at scale, maintain a separate user->sessions index
        pattern = "session:*"
        cursor = 0
        sessions = []
        
        # Scan for session keys (this is simplified - in production use a proper index)
        # For now, return empty list as we'd need to scan all keys
        # TODO: Implement proper user session indexing
        
        return sessions


# Global session manager instance
session_manager = SessionManager()
