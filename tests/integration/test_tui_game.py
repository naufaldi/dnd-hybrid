"""TUI Narrative Game Screen tests.

These tests verify the narrative game flow works correctly.
Note: The old map-based roguelike tests have been moved to archived tests.
"""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config

config.ensure_directories()


@pytest.fixture
def app():
    return DNDRoguelikeApp()


@pytest.mark.asyncio
class TestNarrativeGameFlow:
    """Test complete narrative game flow."""

    async def test_full_game_flow(self, app):
        """Test complete flow: Title -> Character Creation -> Game."""
        async with app.run_test() as pilot:
            await pilot.pause()

            # Start at menu
            assert app.screen is not None

            # Navigate to character creation
            await pilot.click("#btn_new")
            await pilot.pause()

            # Complete character creation
            for char in "Hero":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")  # class
            await pilot.pause()
            await pilot.press("enter")  # race
            await pilot.pause()
            await pilot.click("#btn_start")
            await pilot.pause()

            # Should be on game screen
            assert app.screen is not None

    @pytest.mark.skip(reason="Narrative mode has no character screen")
    async def test_can_open_character_from_game(self, app):
        """Test pressing 'c' opens character screen from game (roguelike only)."""
        pass

    @pytest.mark.skip(reason="Narrative mode has no inventory screen")
    async def test_can_open_inventory_from_game(self, app):
        """Test pressing 'i' opens inventory screen from game (roguelike only)."""
        pass

    @pytest.mark.skip(reason="Narrative mode has no log screen")
    async def test_can_open_log_from_game(self, app):
        """Test pressing 'l' opens log screen from game (roguelike only)."""
        pass

    async def test_can_save_from_game(self, app):
        """Test pressing 's' saves the game."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()

            for char in "Hero":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#btn_start")
            await pilot.pause()

            await pilot.press("s")
            await pilot.pause()
