"""Tests for AI fallback templates."""

import pytest
from src.ai.fallback import (
    get_fallback_dialogue,
    get_fallback_outcome,
    get_fallback_scene_description,
)


class TestFallbackDialogue:
    def test_fallback_dialogue_enigmatic_greeting(self):
        result = get_fallback_dialogue("enigmatic", "greeting")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_fallback_dialogue_hostile(self):
        result = get_fallback_dialogue("hostile", "hostile")
        assert "die" in result.lower() or "meaningless" in result.lower() or len(result) > 5

    def test_fallback_dialogue_unknown_mood_uses_neutral(self):
        result = get_fallback_dialogue("unknown_mood", "greeting")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fallback_dialogue_unknown_type_uses_greeting(self):
        result = get_fallback_dialogue("neutral", "unknown_type")
        assert isinstance(result, str)


class TestFallbackOutcome:
    def test_fallback_outcome_success(self):
        result = get_fallback_outcome("Persuasion", success=True)
        assert "succeeds" in result.lower() or "success" in result.lower()

    def test_fallback_outcome_failure(self):
        result = get_fallback_outcome("Stealth", success=False)
        assert "fail" in result.lower() or "against" in result.lower()


class TestFallbackSceneDescription:
    def test_fallback_scene_description_returns_string(self):
        result = get_fallback_scene_description("tavern_entry")
        assert isinstance(result, str)
        assert len(result) > 10

    def test_fallback_scene_description_generic_for_unknown_scene(self):
        result = get_fallback_scene_description("unknown_scene_xyz")
        assert isinstance(result, str)
        assert len(result) > 0
