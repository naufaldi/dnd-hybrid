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


async def navigate_to_character_creation(app):
    """Helper to navigate from menu to character creation."""
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#btn_new")
        await pilot.pause()
    return app


@pytest.mark.asyncio
class TestCharacterCreation:
    """Test character creation flow."""

    async def test_character_creation_screen_loads(self, app):
        """Character creation screen should load after clicking New Game."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            screen_name = type(app.screen).__name__
            assert "CharacterCreation" in screen_name

    async def test_character_has_title(self, app):
        """Character creation should have a title."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            title = app.screen.query_one("#cc_title")
            assert title is not None

    async def test_can_type_name(self, app):
        """Should be able to type characters for name."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Type some keys
            for char in "Hero":
                await pilot.press(char)
            await pilot.pause()
            # Should not crash

    async def test_enter_advances_from_name_to_class(self, app):
        """Pressing Enter should advance from name to class selection."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Type name
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()

            # Should be on step 1 (class selection)
            assert app.screen.step == 1

    async def test_enter_advances_from_class_to_race(self, app):
        """Pressing Enter on class should advance to race selection."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Enter name
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()

            # Select class
            await pilot.press("enter")
            await pilot.pause()

            # Should be on step 2 (race selection)
            assert app.screen.step == 2

    async def test_has_start_button(self, app):
        """Character creation should have a Start button when complete."""
        app = await navigate_to_character_creation(app)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Complete creation
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")  # Name
            await pilot.pause()
            await pilot.press("enter")  # Class
            await pilot.pause()
            await pilot.press("enter")  # Race
            await pilot.pause()

            # Should have start button
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

            # Go to character creation
            await pilot.click("#btn_new")
            await pilot.pause()

            # Enter name
            for char in "Adventure":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()

            # Select class
            await pilot.press("enter")
            await pilot.pause()

            # Select race
            await pilot.press("enter")
            await pilot.pause()

            # Click start
            await pilot.click("#btn_start")
            await pilot.pause()

            # Should be on game screen
            screen_name = type(app.screen).__name__
            assert "Game" in screen_name
