"""AI Service for narrative generation with disk caching."""

import json
import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

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

        has_api_key = bool(client and client.api_key)
        self.enabled = enabled and has_api_key

        if self.enabled:
            logger.info(
                f"AI service enabled with model: {client.default_model if client else 'unknown'}"
            )
        elif not has_api_key:
            logger.warning("AI service disabled: no API key provided")
        elif not enabled:
            logger.info("AI service disabled: explicitly disabled")

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
                response = self.clean_dialogue_response(response)
                self.cache.set(cache_key, response, self.client.default_model, context_hash)
                return response
        except (AIError, RateLimitError) as e:
            logger.warning(f"AI dialogue generation failed: {e}")

        return self.get_fallback_dialogue(mood, dialogue_type)

    @staticmethod
    def clean_dialogue_response(response: str) -> str:
        """Clean AI response from template text, mood markers, and garbage output."""
        original = response
        response = response.strip()
        if not response:
            return original

        lines = response.split("\n")
        clean_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.match(r"^\*\*[A-Za-z]+/[A-Za-z]+:\*\*", line):
                continue

            if re.match(r"^\*\*[A-Za-z]+:\*\*", line):
                continue

            if re.match(r"^Stranger:", line, re.IGNORECASE):
                line = re.sub(r"^Stranger:\s*", "", line, flags=re.IGNORECASE)

            if re.match(r"^(Okay|Here|Following|Absolutely|Sure)", line, re.IGNORECASE):
                continue

            if "here are" in line.lower() or "options:" in line.lower():
                continue

            clean_lines.append(line)

        if clean_lines:
            response = " ".join(clean_lines)

        if '"' in response:
            match = re.search(r'"([^"]+)"', response)
            if match:
                response = match.group(1)
            else:
                match = re.search(r"'([^']+)'", response)
                if match:
                    response = match.group(1)

        response = response.strip()

        if not response or len(response) < 3:
            return original

        return response

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

    async def generate_choices(
        self,
        scene_context: str,
        character_info: Dict[str, Any],
        story_flags: Dict[str, bool],
        num_choices: int = 2,
    ) -> Optional[List[Dict[str, str]]]:
        """Generate additional AI choices at key decision points.

        Args:
            scene_context: Description of current scene and situation
            character_info: Character class, race, stats
            story_flags: Current story flags set
            num_choices: Number of choices to generate

        Returns:
            List of choice dicts with 'text', 'shortcut', 'next_scene' keys,
            or None if generation fails
        """
        if not self.enabled or not self.client:
            return self.get_fallback_choices(num_choices)

        # Build context for prompt
        char_desc = f"{character_info.get('name', 'Hero')} the {character_info.get('race', '')} {character_info.get('class', '')}"

        prompt = f"""Generate {num_choices} creative story choices for a D&D narrative game.

Current Scene: {scene_context}
Player: {char_desc}
Story Progress: {", ".join([k for k, v in story_flags.items() if v]) if story_flags else "Beginning"}

Generate choices that:
- Are in character for a {character_info.get("class", "adventurer")}
- Have different approaches (combat, diplomatic, stealth, etc.)
- Are thematically appropriate for a D&D adventure
- Lead to interesting story developments

For each choice, provide:
1. A short descriptive text (10-20 words)
2. The approach type: combat, diplomatic, stealth, exploration, or clever

Format your response as a JSON list like:
[
  {{"text": "Choice description", "approach": "stealth"}},
  {{"text": "Another choice", "approach": "diplomatic"}}
]

Only output the JSON, no other text:"""

        context_hash = self._generate_key(prompt, str(story_flags))

        # Try cache first
        cached = self.cache.get(prompt, context_hash)
        if cached:
            try:
                import json

                return json.loads(cached)
            except (json.JSONDecodeError, TypeError):
                pass

        # Generate new choices
        try:
            response = await self.client.generate(prompt=prompt, max_tokens=300, temperature=0.8)

            if response:
                # Try to parse as JSON
                import json

                choices = json.loads(response)
                if isinstance(choices, list):
                    # Cache the response
                    self.cache.set(prompt, response, self.client.default_model, context_hash)
                    return choices

        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"AI choice generation failed: {e}")

        # Fallback to static choices
        return self.get_fallback_choices(num_choices)

    def get_fallback_choices(self, num_choices: int = 2) -> List[Dict[str, str]]:
        """Get fallback static choices when AI is unavailable."""
        fallback_options = [
            {"text": "Carefully search the area", "approach": "exploration"},
            {"text": "Prepare for danger", "approach": "caution"},
            {"text": "Look for another way forward", "approach": "clever"},
            {"text": "Press forward confidently", "approach": "bold"},
        ]
        return fallback_options[:num_choices]

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
    effective_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    client = None
    if effective_key:
        masked = f"{effective_key[:8]}...{effective_key[-4:]}" if len(effective_key) > 12 else "***"
        logger.info(f"Creating AI service with API key: {masked}")
        client = OpenRouterClient(api_key=effective_key)
    else:
        logger.warning("create_ai_service called without API key - AI will be disabled")
    return AIService(client=client)
