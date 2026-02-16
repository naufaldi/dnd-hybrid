"""Tests for AI Service."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.narrative.ai_service import AIService, ResponseCache, create_ai_service
from src.ai.openrouter_client import OpenRouterClient, AIError


class MockOpenRouterClient:
    """Mock OpenRouter client for testing."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.api_key = "test_key"
        self.default_model = "openrouter/free"
        self.call_count = 0

    async def generate_dialogue(self, npc_name, mood, context, prompt_override=None):
        self.call_count += 1
        if self.should_fail:
            raise AIError("Simulated API failure")
        return f"Mock dialogue from {npc_name} ({mood})"

    async def generate_with_fallback(self, prompt, max_tokens=100, temperature=0.7):
        self.call_count += 1
        if self.should_fail:
            raise AIError("Simulated API failure")
        return "Mock outcome narration"

    async def generate_outcome(self, action, roll_result, dc, success):
        self.call_count += 1
        if self.should_fail:
            raise AIError("Simulated API failure")
        return "Mock outcome narration"


class TestResponseCache:
    """Test the response cache."""

    @pytest.fixture
    def cache_dir(self, tmp_path):
        return tmp_path / "cache"

    @pytest.fixture
    def cache(self, cache_dir):
        return ResponseCache(cache_dir=cache_dir, max_age_days=30)

    def test_cache_miss(self, cache):
        """Test cache returns None on miss."""
        result = cache.get("test prompt")
        assert result is None

    def test_cache_set_and_get(self, cache):
        """Test setting and getting cache values."""
        cache.set("test prompt", "test response", "test_model")
        result = cache.get("test prompt")
        assert result == "test response"

    def test_cache_with_context_hash(self, cache):
        """Test cache with context hash."""
        cache.set("prompt", "response1", "model", "context1")
        cache.set("prompt", "response2", "model", "context2")

        assert cache.get("prompt", "context1") == "response1"
        assert cache.get("prompt", "context2") == "response2"

    def test_cache_clear(self, cache):
        """Test clearing cache."""
        cache.set("prompt", "response", "model")
        assert cache.get("prompt") == "response"

        cache.clear()
        assert cache.get("prompt") is None

    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.set("prompt1", "response1", "model")
        cache.set("prompt2", "response2", "model")

        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2


class TestAIService:
    """Test the AI service."""

    @pytest.fixture
    def mock_client(self):
        return MockOpenRouterClient(should_fail=False)

    @pytest.fixture
    def cache_dir(self, tmp_path):
        return tmp_path / "cache"

    @pytest.fixture
    def ai_service(self, mock_client, cache_dir):
        cache = ResponseCache(cache_dir=cache_dir, max_age_days=30)
        return AIService(client=mock_client, enabled=True, cache=cache)

    @pytest.fixture
    def disabled_ai_service(self, cache_dir):
        cache = ResponseCache(cache_dir=cache_dir, max_age_days=30)
        return AIService(client=None, enabled=False, cache=cache)

    @pytest.mark.asyncio
    async def test_enhance_dialogue_success(self, ai_service, mock_client):
        """Test dialogue enhancement with successful API call."""
        result = await ai_service.enhance_dialogue(
            npc_name="Stranger",
            mood="enigmatic",
            context="You approach the mysterious figure",
        )
        assert "Stranger" in result
        assert mock_client.call_count == 1

    @pytest.mark.asyncio
    async def test_enhance_dialogue_cached(self, ai_service, mock_client):
        """Test dialogue enhancement uses cache."""
        result1 = await ai_service.enhance_dialogue(
            npc_name="Stranger",
            mood="enigmatic",
            context="Test context",
        )
        first_call_count = mock_client.call_count
        assert first_call_count == 1

        result2 = await ai_service.enhance_dialogue(
            npc_name="Stranger",
            mood="enigmatic",
            context="Test context",
        )
        assert result1 == result2
        assert mock_client.call_count == 1

    @pytest.mark.asyncio
    async def test_enhance_dialogue_fallback(self, disabled_ai_service):
        """Test dialogue fallback when AI is disabled."""
        result = await disabled_ai_service.enhance_dialogue(
            npc_name="Stranger",
            mood="enigmatic",
            context="Test context",
        )
        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_enhance_dialogue_api_failure(self):
        """Test dialogue falls back on API failure."""
        mock_client = MockOpenRouterClient(should_fail=True)
        ai_service = AIService(client=mock_client, enabled=True)

        result = await ai_service.enhance_dialogue(
            npc_name="Stranger",
            mood="enigmatic",
            context="Test context",
        )
        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_narrate_outcome_success(self, ai_service, mock_client):
        """Test outcome narration with successful API call."""
        result = await ai_service.narrate_outcome(
            action="Persuasion",
            roll_result=18,
            dc=14,
            success=True,
        )
        assert result is not None
        assert mock_client.call_count == 1

    @pytest.mark.asyncio
    async def test_narrate_outcome_fallback(self, disabled_ai_service):
        """Test outcome fallback when AI is disabled."""
        result = await disabled_ai_service.narrate_outcome(
            action="Athletics",
            roll_result=10,
            dc=15,
            success=False,
        )
        assert result is not None
        assert "fail" in result.lower()

    def test_get_fallback_dialogue(self, ai_service):
        """Test fallback dialogue generation."""
        result = ai_service.get_fallback_dialogue("enigmatic", "greeting")
        assert result is not None
        assert len(result) > 0

    def test_get_fallback_outcome_success(self, ai_service):
        """Test fallback outcome for success."""
        result = ai_service.get_fallback_outcome("Persuasion", success=True)
        assert "succeed" in result.lower()

    def test_get_fallback_outcome_failure(self, ai_service):
        """Test fallback outcome for failure."""
        result = ai_service.get_fallback_outcome("Persuasion", success=False)
        assert "fail" in result.lower()

    def test_is_enabled(self, ai_service, disabled_ai_service):
        """Test enabled state check."""
        assert ai_service.is_enabled() is True
        assert disabled_ai_service.is_enabled() is False

    def test_clear_cache(self, ai_service, mock_client):
        """Test cache clearing."""
        import asyncio

        asyncio.run(ai_service.enhance_dialogue("Stranger", "enigmatic", "Test"))
        assert mock_client.call_count == 1

        ai_service.clear_cache()
        asyncio.run(ai_service.enhance_dialogue("Stranger", "enigmatic", "Test"))
        assert mock_client.call_count == 2


class TestCreateAIService:
    """Test the AI service factory function."""

    def test_create_with_api_key(self, monkeypatch):
        """Test creating service with API key."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        service = create_ai_service()
        assert service is not None

    def test_create_without_api_key(self, monkeypatch):
        """Test creating service without API key."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        service = create_ai_service()
        assert service is not None
        assert service.is_enabled() is False
