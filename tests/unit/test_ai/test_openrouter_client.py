"""Tests for OpenRouter AI client."""

import pytest
from unittest.mock import AsyncMock, patch
from src.ai.openrouter_client import OpenRouterClient, AIError


class TestOpenRouterClient:
    """Test OpenRouter client functionality."""

    @pytest.fixture
    def client(self):
        return OpenRouterClient(api_key="test_key")

    def test_client_initialization(self, client):
        """Test client initializes with correct defaults."""
        assert client.api_key == "test_key"
        assert client.default_model is not None
        assert (
            "free" in client.default_model.lower() or "openrouter" in client.default_model.lower()
        )

    def test_client_no_api_key(self):
        """Test client can be created without API key."""
        client = OpenRouterClient()
        assert client.api_key == ""

    def test_client_custom_model(self):
        """Test client can use custom model."""
        client = OpenRouterClient(api_key="key")
        client.default_model = "custom/model"
        assert client.default_model == "custom/model"

    @pytest.mark.asyncio
    async def test_generate_without_api_key(self, client):
        """Test generate raises error without API key."""
        client.api_key = ""
        with pytest.raises(AIError, match="No API key"):
            await client.generate("Test prompt")

    @pytest.mark.asyncio
    async def test_enhance_description_generates_prompt(self, client):
        """Test enhance_description creates proper prompt."""
        with patch.object(client, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Enhanced text"

            result = await client.enhance_description(
                "A dark cave.", {"player_class": "fighter", "act": 1}
            )

            # Verify generate was called
            mock_gen.assert_called_once()
            call_args = mock_gen.call_args
            prompt = call_args[0][0]

            # Verify prompt contains relevant info
            assert "A dark cave" in prompt
            assert "fighter" in prompt
            assert "1" in prompt

    @pytest.mark.asyncio
    async def test_generate_dialogue_generates_prompt(self, client):
        """Test generate_dialogue creates proper prompt."""
        with patch.object(client, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = '"Hello."'

            result = await client.generate_dialogue(
                "Guard Captain", "hostile", "You approached without permission"
            )

            mock_gen.assert_called_once()
            call_args = mock_gen.call_args
            prompt = call_args[0][0]

            assert "Guard Captain" in prompt
            assert "hostile" in prompt

    @pytest.mark.asyncio
    async def test_generate_outcome_generates_prompt(self, client):
        """Test generate_outcome creates proper prompt."""
        with patch.object(client, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "You succeed!"

            result = await client.generate_outcome(
                action="Attack goblin", roll_result=18, dc=12, success=True
            )

            mock_gen.assert_called_once()
            call_args = mock_gen.call_args
            prompt = call_args[0][0]

            assert "Attack goblin" in prompt
            assert "18" in prompt
            assert "SUCCESS" in prompt
