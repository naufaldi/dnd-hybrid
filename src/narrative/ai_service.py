"""AI Service for narrative generation - delegates to ai.narrative_generator."""

from ..ai.narrative_generator import (
    NarrativeGenerator,
    ResponseCache,
    create_ai_service,
)

AIService = NarrativeGenerator
__all__ = ["AIService", "ResponseCache", "create_ai_service"]
