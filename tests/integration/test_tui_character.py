"""TUI Character Creation tests - TDD approach.

These tests define the expected behavior of the character creation screen.
"""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config

config.ensure_directories()


@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    return DNDRoguelikeApp()


@pytest.mark.asyncio
class TestCharacterCreation:
    """Test character creation flow."""

    async def test_character_creation_screen_loads(self, app):
        """Character creation screen should load after clicking New Game."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            screen_name = type(app.screen).__name__
            assert "CharacterCreation" in screen_name

    async def test_character_has_title(self, app):
        """Character creation should have a title."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            title = app.screen.query_one("#cc_title")
            assert title is not None

    async def test_can_type_name(self, app):
        """Should be able to type characters for name."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            for char in "Hero":
                await pilot.press(char)
            await pilot.pause()

    async def test_enter_advances_from_name_to_class(self, app):
        """Pressing Enter should advance from name to class selection."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            assert app.screen.step == 1

    async def test_enter_advances_from_class_to_race(self, app):
        """Pressing Enter on class should advance to race selection."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert app.screen.step == 2

    async def test_has_start_button(self, app):
        """Character creation should have a Start button when complete."""
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            start_btn = app.screen.query_one("#btn_start")
            assert start_btn is not None


@pytest.mark.asyncio
class TestCharacterCreationComplete:
    """Test completing character creation."""

    async def test_full_creation_flow(self):
        """Complete flow: name -> class -> race -> start game."""
        app = DNDRoguelikeApp()

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn_new")
            await pilot.pause()
            for char in "Adventure":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#btn_start")
            await pilot.pause()
            screen_name = type(app.screen).__name__
            assert "Game" in screen_name
