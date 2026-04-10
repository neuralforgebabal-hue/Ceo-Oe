"""
CEO AI OS - AI Router
Abstracts over multiple AI providers: Groq, OpenAI, Anthropic.
Falls back gracefully if primary provider fails.
"""
import json
from typing import Optional, Dict, Any, List
from core.config import settings
from core.logger import get_logger

logger = get_logger("ai.router")


class AIRouter:
    """Central AI invocation hub with provider fallback."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model = settings.AI_MODEL
        self._groq_client = None
        self._openai_client = None
        self._anthropic_client = None

    def _get_groq(self):
        if not self._groq_client and settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                logger.warning("groq package not installed")
        return self._groq_client

    def _get_openai(self):
        if not self._openai_client and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                logger.warning("openai package not installed")
        return self._openai_client

    def _get_anthropic(self):
        if not self._anthropic_client and settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except ImportError:
                logger.warning("anthropic package not installed")
        return self._anthropic_client

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        """
        Call AI provider and return text response.
        Falls back through providers if primary fails.
        """
        providers = self._build_provider_list()
        last_error = None

        for provider_name in providers:
            try:
                result = await self._call_provider(
                    provider_name, system_prompt, user_message,
                    max_tokens, temperature, json_mode
                )
                if result:
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue

        # Final fallback: return structured error
        logger.error(f"All AI providers failed. Last error: {last_error}")
        return json.dumps({
            "error": "All AI providers unavailable",
            "fallback": True,
            "message": "Please configure an AI provider API key in .env"
        })

    def _build_provider_list(self) -> List[str]:
        order = [self.provider]
        for p in ["groq", "openai", "anthropic"]:
            if p not in order:
                order.append(p)
        return order

    async def _call_provider(self, provider: str, system: str, user: str,
                              max_tokens: int, temperature: float, json_mode: bool) -> str:
        if provider == "groq":
            return await self._call_groq(system, user, max_tokens, temperature, json_mode)
        elif provider == "openai":
            return await self._call_openai(system, user, max_tokens, temperature, json_mode)
        elif provider == "anthropic":
            return await self._call_anthropic(system, user, max_tokens)
        raise ValueError(f"Unknown provider: {provider}")

    async def _call_groq(self, system: str, user: str, max_tokens: int,
                          temperature: float, json_mode: bool) -> str:
        client = self._get_groq()
        if not client:
            raise RuntimeError("Groq client not initialized")

        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.chat.completions.create(**kwargs)
        )
        return response.choices[0].message.content

    async def _call_openai(self, system: str, user: str, max_tokens: int,
                            temperature: float, json_mode: bool) -> str:
        client = self._get_openai()
        if not client:
            raise RuntimeError("OpenAI client not initialized")

        import asyncio
        kwargs = dict(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.chat.completions.create(**kwargs)
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, system: str, user: str, max_tokens: int) -> str:
        client = self._get_anthropic()
        if not client:
            raise RuntimeError("Anthropic client not initialized")

        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
        )
        return response.content[0].text


# Singleton instance
ai_router = AIRouter()
