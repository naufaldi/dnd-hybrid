"""Narrative generator for AI-enhanced content."""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .openrouter_client import OpenRouterClient, AIError, RateLimitError
from .prompts import (
    build_scene_enhancement_prompt,
    build_dialogue_prompt,
    build_outcome_prompt,
    build_choices_prompt,
    build_ending_enhancement_prompt,
)
from .fallback import (
    get_fallback_dialogue,
    get_fallback_outcome,
    get_fallback_scene_description,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """Disk-based cache for AI responses."""

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
        if not self.cache_file.exists():
            return
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                if data.get("version") == self.CACHE_VERSION:
                    self._cache = data.get("responses", {})
                else:
                    self._cache = {}
        except (json.JSONDecodeError, IOError):
            self._cache = {}

    def _save_cache(self) -> None:
        try:
            data = {
                "version": self.CACHE_VERSION,
                "updated": datetime.now().isoformat(),
                "responses": self._cache,
            }
            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass

    def _generate_key(self, prompt: str, context_hash: str = "") -> str:
        combined = f"{prompt}:{context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def get(self, key: str, context_hash: str = "") -> Optional[str]:
        entry = self._cache.get(self._generate_key(key, context_hash))
        if entry is None:
            return None
        try:
            cached_time = datetime.fromisoformat(entry.get("cached_at", ""))
            if (datetime.now() - cached_time).days > self.max_age_days:
                return None
        except (ValueError, TypeError):
            return None
        return entry.get("response")

    def set(self, key: str, response: str, model: str, context_hash: str = "") -> None:
        k = self._generate_key(key, context_hash)
        self._cache[k] = {
            "response": response,
            "model": model,
            "cached_at": datetime.now().isoformat(),
        }
        self._save_cache()

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache = {}
        self._save_cache()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = len(self._cache)
        expired = 0
        for e in self._cache.values():
            try:
                cached = datetime.fromisoformat(e.get("cached_at", ""))
                if (datetime.now() - cached).days > self.max_age_days:
                    expired += 1
            except (ValueError, TypeError):
                expired += 1
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
        }


class NarrativeGenerator:
    """Generates AI-enhanced narrative content with fallbacks."""

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

    async def enhance_dialogue(
        self,
        npc_name: str,
        mood: str,
        context: str,
        dialogue_type: str = "greeting",
    ) -> str:
        """Generate enhanced NPC dialogue with caching."""
        if not self.enabled:
            return get_fallback_dialogue(mood, dialogue_type)

        cache_key = f"dialogue_{npc_name}_{mood}_{dialogue_type}"
        context_hash = hashlib.sha256(context.encode()).hexdigest()[:8]
        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = build_dialogue_prompt(npc_name, mood, context, dialogue_type)
        try:
            response = await self.client.generate_dialogue(
                npc_name=npc_name,
                mood=mood,
                context=context,
                prompt_override=prompt,
            )
            response = response.strip()
            if response:
                response = self._clean_dialogue_response(response)
                self.cache.set(cache_key, response, self.client.default_model, context_hash)
                return response
        except (AIError, RateLimitError) as e:
            logger.warning(f"AI dialogue generation failed: {e}")

        return get_fallback_dialogue(mood, dialogue_type)

    @staticmethod
    def _clean_dialogue_response(response: str) -> str:
        original = response.strip()
        if not original:
            return response
        lines = [ln.strip() for ln in original.split("\n") if ln.strip()]
        clean = []
        for line in lines:
            if re.match(r"^\*\*[A-Za-z]+[/:]", line):
                continue
            if re.match(r"^Stranger:", line, re.IGNORECASE):
                line = re.sub(r"^Stranger:\s*", "", line, flags=re.IGNORECASE)
            if re.match(r"^(Okay|Here|Following|Absolutely|Sure)", line, re.IGNORECASE):
                continue
            if "here are" in line.lower() or "options:" in line.lower():
                continue
            clean.append(line)
        if clean:
            response = " ".join(clean)
        if '"' in response:
            m = re.search(r'"([^"]+)"', response)
            if m:
                response = m.group(1)
        response = response.strip()
        return response if response and len(response) >= 3 else original

    async def enhance_scene_description(self, template: str, context: Dict[str, Any]) -> str:
        """Enhance scene description with AI."""
        if not self.enabled:
            return get_fallback_scene_description(
                context.get("scene_id", "exploration")
            )

        cache_key = f"scene_{hashlib.sha256(template.encode()).hexdigest()[:12]}"
        context_hash = str(context.get("act", 1))
        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = build_scene_enhancement_prompt(template, context)
        try:
            response = await self.client.generate_with_fallback(
                prompt, max_tokens=300, temperature=0.7
            )
            if response and response.strip():
                self.cache.set(
                    cache_key, response.strip(), self.client.default_model, context_hash
                )
                return response.strip()
        except (AIError, RateLimitError, Exception) as e:
            logger.warning(f"AI scene enhancement failed: {e}")

        return get_fallback_scene_description(context.get("scene_id", "exploration"))

    async def enhance_description(self, template: str, context: Dict[str, Any]) -> str:
        """Alias for enhance_scene_description for SceneManager compatibility."""
        return await self.enhance_scene_description(template, context)

    async def narrate_outcome(
        self,
        action: str,
        roll_result: int,
        dc: int,
        success: bool,
    ) -> str:
        """Generate narrative outcome for skill checks."""
        if not self.enabled:
            return get_fallback_outcome(action, success)

        cache_key = f"outcome_{action}_{success}"
        context_hash = f"{roll_result}:{dc}"
        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = build_outcome_prompt(action, roll_result, dc, success)
        try:
            response = await self.client.generate_with_fallback(
                prompt, max_tokens=100, temperature=0.7
            )
            if response and response.strip():
                self.cache.set(
                    cache_key, response.strip(), self.client.default_model, context_hash
                )
                return response.strip()
        except (AIError, RateLimitError) as e:
            logger.warning(f"AI outcome narration failed: {e}")

        return get_fallback_outcome(action, success)

    async def generate_choices(
        self,
        scene_context: str,
        character_info: Dict[str, Any],
        story_flags: Dict[str, bool],
        num_choices: int = 2,
    ) -> List[Dict[str, str]]:
        """Generate additional AI choices at decision points."""
        fallback_options = [
            {"text": "Carefully search the area", "approach": "exploration"},
            {"text": "Prepare for danger", "approach": "caution"},
            {"text": "Look for another way forward", "approach": "clever"},
            {"text": "Press forward confidently", "approach": "bold"},
        ]

        if not self.enabled or not self.client:
            return fallback_options[:num_choices]

        prompt = build_choices_prompt(
            scene_context, character_info, story_flags, num_choices
        )
        context_hash = str(story_flags)
        cached = self.cache.get(prompt, context_hash)
        if cached:
            try:
                return json.loads(cached)
            except (json.JSONDecodeError, TypeError):
                pass

        try:
            response = await self.client.generate(
                prompt=prompt, max_tokens=300, temperature=0.8
            )
            if response:
                choices = json.loads(response)
                if isinstance(choices, list):
                    self.cache.set(prompt, response, self.client.default_model, context_hash)
                    return choices
        except Exception as e:
            logger.warning(f"AI choice generation failed: {e}")

        return fallback_options[:num_choices]

    async def enhance_ending(
        self, base_description: str, game_state: Dict[str, Any]
    ) -> str:
        """Enhance ending description with playthrough-specific details."""
        if not self.enabled or not self.client:
            return base_description

        ctx = {
            "flags": game_state.get("flags", {}),
            "choices_made": game_state.get("choices_made", []),
            "scene_history": game_state.get("scene_history", []),
        }
        cache_key = f"ending_{hashlib.sha256(base_description.encode()).hexdigest()[:12]}"
        context_hash = str(ctx.get("flags", {}))
        cached = self.cache.get(cache_key, context_hash)
        if cached:
            return cached

        prompt = build_ending_enhancement_prompt(base_description, ctx)
        try:
            response = await self.client.generate_with_fallback(
                prompt, max_tokens=200, temperature=0.7
            )
            if response and response.strip():
                enhanced = response.strip()
                self.cache.set(
                    cache_key, enhanced, self.client.default_model, context_hash
                )
                return enhanced
        except (AIError, RateLimitError, Exception) as e:
            logger.warning(f"AI ending enhancement failed: {e}")
        return base_description

    def is_enabled(self) -> bool:
        """Check if AI generation is enabled."""
        return self.enabled

    def get_fallback_dialogue(self, mood: str, dialogue_type: str = "greeting") -> str:
        """Get static fallback dialogue when AI is unavailable."""
        return get_fallback_dialogue(mood, dialogue_type)

    def get_fallback_outcome(self, action: str, success: bool) -> str:
        """Get static fallback outcome when AI is unavailable."""
        return get_fallback_outcome(action, success)

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()


def create_ai_service(api_key: Optional[str] = None) -> NarrativeGenerator:
    """Factory to create NarrativeGenerator with OpenRouter client."""
    import os

    from .openrouter_client import OpenRouterClient

    effective_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    client = None
    if effective_key:
        logger.info(
            f"Creating AI service with API key: "
            f"{effective_key[:8]}...{effective_key[-4:] if len(effective_key) > 12 else '***'}"
        )
        client = OpenRouterClient(api_key=effective_key)
    else:
        logger.warning("create_ai_service called without API key - AI will be disabled")
    return NarrativeGenerator(client=client)
