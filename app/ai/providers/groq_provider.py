"""Groq LLM provider (default)."""

from typing import Any

from langchain_groq import ChatGroq

from app.ai.providers.base import BaseLLMProvider
from app.core.config import get_settings


class GroqProvider(BaseLLMProvider):
    """Groq inference — fast, free-tier friendly."""

    @property
    def name(self) -> str:
        return "groq"

    async def invoke(self, messages: list, **kwargs: Any) -> str:
        settings = get_settings()
        llm = ChatGroq(
            model=kwargs.get("model", settings.groq_model),
            temperature=kwargs.get("temperature", settings.openai_temperature),
            max_tokens=kwargs.get("max_tokens", settings.openai_max_tokens),
            api_key=settings.groq_api_key,
        )
        response = await llm.ainvoke(messages)
        return response.content
