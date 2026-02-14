"""OpenRouter API client for AI narrative generation."""

import os
import asyncio
import hashlib
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AIError(Exception):
    """Exception raised when AI generation fails."""

    pass


class RateLimitError(AIError):
    """Raised when rate limit is exceeded."""

    pass


@dataclass
class RateLimiter:
    """Token bucket rate limiter for API calls."""

    requests_per_minute: int = 30
    _requests: list = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            self._requests = [r for r in self._requests if r > cutoff]

            if len(self._requests) >= self.requests_per_minute:
                wait_time = 60 - (now - self._requests[0]).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()

            self._requests.append(now)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0


class OpenRouterClient:
    """Client for OpenRouter AI API."""

    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "openrouter/free"
    FALLBACK_MODELS = [
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-7b-instruct",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 15,
        retry_config: Optional[RetryConfig] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.default_model = self.DEFAULT_MODEL
        self.timeout = aiohttp.ClientTimeout(
            total=timeout, connect=min(10, timeout // 2), sock_read=min(10, timeout // 2)
        )
        self.retry_config = retry_config or RetryConfig()
        self.rate_limiter = RateLimiter()

        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        use_retry: bool = True,
    ) -> str:
        """Generate text using OpenRouter API."""
        if not self.api_key:
            raise AIError("No API key configured")

        url = f"{self.BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dnd-hybrid",
            "X-Title": "AI Dungeon Chronicles",
        }
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if use_retry:
            return await self._generate_with_retry(url, headers, payload)

        return await self._make_request(url, headers, payload)

    async def _generate_with_retry(self, url: str, headers: dict, payload: dict) -> str:
        """Generate with exponential backoff retry."""
        config = self.retry_config
        last_error = None

        for attempt in range(config.max_retries):
            try:
                await self.rate_limiter.acquire()
                return await self._make_request(url, headers, payload)
            except (aiohttp.ClientError, AIError) as e:
                last_error = e
                if attempt < config.max_retries - 1:
                    delay = min(
                        config.base_delay * (config.exponential_base**attempt),
                        config.max_delay,
                    )
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{config.max_retries}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retries exhausted: {e}")

        raise AIError(f"Max retries exceeded. Last error: {last_error}")

    async def _make_request(self, url: str, headers: dict, payload: dict) -> str:
        """Make a single API request."""
        try:
            session = await self._get_session()
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 429:
                    # Parse Retry-After header if available
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                        logger.warning(f"Rate limited by API, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                    raise RateLimitError("Rate limit exceeded")
                if response.status == 401:
                    raise AIError("Invalid API key")
                if response.status != 200:
                    error_text = await response.text()
                    raise AIError(f"API returned status {response.status}: {error_text}")

                data = await response.json()
                if "choices" not in data or not data["choices"]:
                    raise AIError("Invalid response format: no choices returned")

                # Validate nested structure before accessing
                first_choice = data["choices"][0]
                if not isinstance(first_choice, dict):
                    raise AIError("Invalid response format: choice is not an object")
                if "message" not in first_choice:
                    raise AIError("Invalid response format: no message in choice")
                message = first_choice["message"]
                if not isinstance(message, dict) or "content" not in message:
                    raise AIError("Invalid response format: no content in message")

                content = message["content"]
                if not content or not isinstance(content, str):
                    raise AIError("Invalid response format: empty or invalid content")

                return content

        except aiohttp.ClientError as e:
            raise AIError(f"Network error: {e}")
        except KeyError as e:
            raise AIError(f"Invalid response format: {e}")

    async def generate_with_fallback(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.7
    ) -> str:
        """Generate text with fallback models on error."""
        models_to_try = [self.default_model] + self.FALLBACK_MODELS

        last_error = None
        for model in models_to_try:
            try:
                logger.info(f"Trying model: {model}")
                return await self.generate(
                    prompt, model=model, max_tokens=max_tokens, temperature=temperature
                )
            except (AIError, RateLimitError) as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e
                continue

        raise AIError(f"All models failed. Last error: {last_error}")

    async def enhance_description(self, template: str, context: dict) -> str:
        """Enhance a scene description with AI."""
        prompt = f"""Enhance this scene description for a D&D interactive fiction game.
Keep the core facts and tone. Add 2-3 sentences of atmospheric detail.

Base description:
{template}

Context:
- Player class: {context.get("player_class", "unknown")}
- Current act: {context.get("act", 1)}

Enhanced description:"""
        return await self.generate_with_fallback(prompt, max_tokens=300)

    async def generate_dialogue(
        self, npc_name: str, mood: str, context: str, prompt_override: Optional[str] = None
    ) -> str:
        """Generate NPC dialogue."""
        if prompt_override:
            prompt = prompt_override
        else:
            prompt = f"""Generate 1-2 sentences of dialogue for a D&D NPC.
The dialogue should match the specified mood exactly.

NPC: {npc_name}
Mood: {mood} (hostile/neutral/friendly/enigmatic/curious/wary)
Context: {context}

Dialogue:"""
        return await self.generate_with_fallback(prompt, max_tokens=100)

    async def generate_outcome(self, action: str, roll_result: int, dc: int, success: bool) -> str:
        """Generate narrative outcome description."""
        prompt = f"""Generate a 1-2 sentence narrative description of what happens when:
Action: {action}
Roll: {roll_result}
Difficulty: {dc}
Result: {"SUCCESS" if success else "FAILURE"}

Narrative:"""
        return await self.generate_with_fallback(prompt, max_tokens=100)


def create_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Factory function to create an OpenRouter client."""
    return OpenRouterClient(api_key=api_key)
