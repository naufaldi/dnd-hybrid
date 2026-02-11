"""AI Service for narrative generation with disk caching."""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import asdict

from ..ai.openrouter_client import OpenRouterClient, AIError, RateLimitError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """Disk-based LRU cache for AI responses."""

    CACHE_VERSION = 1
    DEFAULT_MAX_AGE_DAYS = 30

    def __init__(self, cache_dir: Optional[Path] = None, max_age_days: int = 30):
        if cache_dir is None:
            cache_dir = Path.home() / ".dnd_roguelike" / "cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "ai_cache.json"
        self.max_age_days = max_age_days
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                if data.get("version") == self.CACHE_VERSION:
                    self._cache = data.get("responses", {})
                    logger.info(f"Loaded {len(self._cache)} cached responses")
                else:
                    logger.info("Cache version mismatch, starting fresh")
                    self._cache = {}
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache: {e}")
            self._cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            data = {
                "version": self.CACHE_VERSION,
                "updated": datetime.now().isoformat(),
                "responses": self._cache,
            }
            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save cache: {e}")

    def _generate_key(self, prompt: str, context_hash: str = "") -> str:
        """Generate cache key from prompt and context."""
        combined = f"{prompt}:{context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def get(self, prompt: str, context_hash: str = "") -> Optional[str]:
        """Get cached response if available and not expired."""
        key = self._generate_key(prompt, context_hash)
        entry = self._cache.get(key)

        if entry is None:
            return None

        try:
            cached_time = datetime.fromisoformat(entry.get("cached_at", ""))
            age_days = (datetime.now() - cached_time).days
            if age_days > self.max_age_days:
                del self._cache[key]
                return None
        except (ValueError, TypeError):
            return None

        logger.debug(f"Cache hit for key {key[:8]}...")
        return entry.get("response")

    def set(self, prompt: str, response: str, model: str, context_hash: str = "") -> None:
        """Cache a response."""
        key = self._generate_key(prompt, context_hash)
        self._cache[key] = {
            "response": response,
            "model": model,
            "cached_at": datetime.now().isoformat(),
            "prompt_preview": prompt[:100],
        }
        self._save_cache()
        logger.debug(f"Cached response for key {key[:8]}...")

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache = {}
        self._save_cache()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired = 0
        now = datetime.now()

        for entry in self._cache.values():
            try:
                cached_time = datetime.fromisoformat(entry.get("cached_at", ""))
                if (now - cached_time).days > self.max_age_days:
                    expired += 1
            except (ValueError, TypeError):
                expired += 1

        return {
            "total_entries": total_entries,
            "expired_entries": expired,
            "active_entries": total_entries - expired,
        }


class AIService:
    """Service for AI-enhanced narrative content."""

    FALLBACK_DIALOGUE: Dict[str, Dict[str, str]] = {
        "enigmatic": {
            "greeting": "The figure's eyes glint with secrets untold...",
            "hostile": "You would do well to leave these matters to those who understand them.",
            "neutral": "Perhaps... you might be of use yet.",
            "friendly": "I have watched your journey with interest.",
            "curious": "Tell me more of this quest you speak.",
        },
        "hostile": {
            "greeting": "You dare approach me?!",
            "hostile": "Your words are meaningless. Prepare to die!",
            "neutral": "Speak quickly, before I lose my patience.",
            "friendly": "I... might have misjudged you.",
            "curious": "Why should I trust a stranger?",
        },
        "neutral": {
            "greeting": "A traveler. How unexpected.",
            "hostile": "You push your luck, mortal.",
            "neutral": "We are not enemies... yet.",
            "friendly": "Perhaps we can help each other.",
            "curious": "What brings you to these parts?",
        },
        "friendly": {
            "greeting": "Ah, a friend! Please, come closer.",
            "hostile": "Wait, let's talk about this!",
            "neutral": "I'm glad our paths crossed.",
            "friendly": "It's good to see a friendly face.",
            "curious": "Tell me of your adventures!",
        },
    }

    def __init__(
        self,
        client: Optional[OpenRouterClient] = None,
        cache: Optional[ResponseCache] = None,
        enabled: bool = True,
    ):
        self.client = client
        self.cache = cache or ResponseCache()
        self.enabled = enabled and bool(client and client.api_key)

        if not self.enabled:
            logger.info("AI service disabled (no API key or disabled)")

    async def enhance_dialogue(
        self,
        npc_name: str,
        mood: str,
        context: str,
        dialogue_type: str = "greeting",
    ) -> str:
        """Generate enhanced NPC dialogue with caching."""
        if not self.enabled:
            return self.get_fallback_dialogue(mood, dialogue_type)

        cache_key = f"dialogue_{npc_name}_{mood}_{dialogue_type}"
        context_hash = hashlib.sha256(context.encode()).hexdigest()[:8]

        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = f"""Generate a brief, atmospheric dialogue response for a D&D NPC.

NPC: {npc_name}
Mood: {mood} (enigmatic/hostile/neutral/friendly/curious)
Type: {dialogue_type} (greeting/response/question/threat/promise)
Context: {context}

Requirements:
- 1-2 sentences maximum
- Match the mood exactly
- No action descriptions, just spoken words
- Use evocative, mysterious language

Dialogue:"""

        try:
            response = await self.client.generate_dialogue(
                npc_name=npc_name,
                mood=mood,
                context=context,
                prompt_override=prompt,
            )
            response = response.strip()
            if response:
                self.cache.set(cache_key, response, self.client.default_model, context_hash)
                return response
        except (AIError, RateLimitError) as e:
            logger.warning(f"AI dialogue generation failed: {e}")

        return self.get_fallback_dialogue(mood, dialogue_type)

    async def narrate_outcome(
        self,
        action: str,
        roll_result: int,
        dc: int,
        success: bool,
    ) -> str:
        """Generate narrative outcome for skill checks with caching."""
        if not self.enabled:
            return self.get_fallback_outcome(action, success)

        cache_key = f"outcome_{action}_{success}"
        context_hash = f"{roll_result}:{dc}"

        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = f"""Generate a brief narrative outcome for a D&D skill check.

Action: {action}
Roll: {roll_result} vs DC {dc}
Result: {"SUCCESS" if success else "FAILURE"}

Requirements:
- 1-2 sentences
- Dramatic and evocative
- Show consequences of success or failure

Outcome:"""

        try:
            response = await self.client.generate_outcome(
                action=action,
                roll_result=roll_result,
                dc=dc,
                success=success,
            )
            response = response.strip()
            if response:
                self.cache.set(cache_key, response, self.client.default_model, context_hash)
                return response
        except (AIError, RateLimitError) as e:
            logger.warning(f"AI outcome generation failed: {e}")

        return self.get_fallback_outcome(action, success)

    def get_fallback_dialogue(self, mood: str, dialogue_type: str = "greeting") -> str:
        """Get static fallback dialogue when AI is unavailable."""
        mood_templates = self.FALLBACK_DIALOGUE.get(mood, self.FALLBACK_DIALOGUE["neutral"])
        return mood_templates.get(dialogue_type, mood_templates["greeting"])

    def get_fallback_outcome(self, action: str, success: bool) -> str:
        """Get static fallback outcome when AI is unavailable."""
        if success:
            return f"Your {action} succeeds! Luck favors the bold."
        return f"Your {action} fails. The odds were against you."

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

    def is_enabled(self) -> bool:
        """Check if AI service is enabled."""
        return self.enabled


def create_ai_service(api_key: Optional[str] = None) -> AIService:
    """Factory function to create an AI service."""
    client = None
    if api_key or os.environ.get("OPENROUTER_API_KEY"):
        client = OpenRouterClient(api_key=api_key)
    return AIService(client=client)
