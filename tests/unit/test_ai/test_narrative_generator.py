"""Tests for AI narrative generator."""

import tempfile
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, Mock

from src.ai.narrative_generator import NarrativeGenerator, ResponseCache


class TestNarrativeGenerator:
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.api_key = "test_key"
        client.default_model = "openrouter/free"
        client.generate = AsyncMock(return_value="Generated text")
        client.generate_with_fallback = AsyncMock(return_value="Generated text")
        client.generate_dialogue = AsyncMock(return_value='"Hello, traveler."')
        client.generate_outcome = AsyncMock(return_value="You succeed!")
        return client

    @pytest.fixture
    def temp_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    @pytest.fixture
    def generator(self, mock_client, temp_cache):
        cache = ResponseCache(cache_dir=temp_cache)
        return NarrativeGenerator(client=mock_client, enabled=True, cache=cache)

    @pytest.fixture
    def disabled_generator(self):
        return NarrativeGenerator(client=None, enabled=False)

    @pytest.mark.asyncio
    async def test_enhance_dialogue_calls_client(self, generator, mock_client):
        result = await generator.enhance_dialogue(
            npc_name="Stranger", mood="enigmatic", context="Test context"
        )
        mock_client.generate_dialogue.assert_called()
        assert result

    @pytest.mark.asyncio
    async def test_enhance_dialogue_fallback_when_disabled(self, disabled_generator):
        result = await disabled_generator.enhance_dialogue(
            npc_name="Stranger", mood="enigmatic", context="Test"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_enhance_scene_description_calls_client(self, generator, mock_client):
        result = await generator.enhance_scene_description(
            template="A dark cave.", context={"player_class": "fighter", "act": 1}
        )
        mock_client.generate_with_fallback.assert_called()
        assert result

    @pytest.mark.asyncio
    async def test_enhance_scene_description_fallback_when_disabled(self, disabled_generator):
        result = await disabled_generator.enhance_scene_description(
            template="A cave.", context={}
        )
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_narrate_outcome_calls_client(self, generator, mock_client):
        result = await generator.narrate_outcome(
            action="Persuasion", roll_result=15, dc=12, success=True
        )
        mock_client.generate_with_fallback.assert_called()
        assert result

    @pytest.mark.asyncio
    async def test_narrate_outcome_fallback_when_disabled(self, disabled_generator):
        result = await disabled_generator.narrate_outcome(
            action="Stealth", roll_result=5, dc=10, success=False
        )
        assert "fail" in result.lower() or "against" in result.lower()

    def test_is_enabled(self, generator, disabled_generator):
        assert generator.is_enabled() is True
        assert disabled_generator.is_enabled() is False
