"""OpenAI LLM provider (fallback)."""

from typing import Any

from app.ai.providers.base import BaseLLMProvider
from app.core.config import get_settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider — used as fallback when Groq is rate-limited."""

    @property
    def name(self) -> str:
        return "openai"

    async def invoke(self, messages: list, **kwargs: Any) -> str:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise RuntimeError("langchain-openai not installed")

        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")

        llm = ChatOpenAI(
            model=kwargs.get("model", settings.openai_model),
            temperature=kwargs.get("temperature", settings.openai_temperature),
            max_tokens=kwargs.get("max_tokens", settings.openai_max_tokens),
            api_key=settings.openai_api_key,
        )
        response = await llm.ainvoke(messages)
        return response.content
