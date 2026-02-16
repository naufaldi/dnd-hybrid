"""AI integration module for narrative generation."""

from .openrouter_client import OpenRouterClient, AIError, RateLimitError
from .prompts import (
    build_scene_enhancement_prompt,
    build_dialogue_prompt,
    build_outcome_prompt,
    build_choices_prompt,
)
from .fallback import (
    get_fallback_dialogue,
    get_fallback_outcome,
    get_fallback_scene_description,
)
from .narrative_generator import NarrativeGenerator, ResponseCache

__all__ = [
    "OpenRouterClient",
    "AIError",
    "RateLimitError",
    "build_scene_enhancement_prompt",
    "build_dialogue_prompt",
    "build_outcome_prompt",
    "build_choices_prompt",
    "get_fallback_dialogue",
    "get_fallback_outcome",
    "get_fallback_scene_description",
    "NarrativeGenerator",
    "ResponseCache",
]
