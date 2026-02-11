"""TUI Menu tests - TDD approach.

These tests define the expected behavior of the menu screen.
Run these tests to verify the TUI works correctly.
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
class TestMenuScreen:
    """Test menu screen functionality."""

    async def test_app_starts_successfully(self, app):
        """App should start without errors."""
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app is not None

    async def test_menu_screen_is_visible_on_start(self, app):
        """Menu screen should be visible when app starts."""
        async with app.run_test() as pilot:
            await pilot.pause()
            # App should be running
            assert app.is_running

    async def test_menu_has_new_game_button(self, app):
        """Menu should have a New Game button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            # Query from screen, not app
            btn = app.screen.query_one("#btn_new")
            assert btn is not None

    async def test_menu_has_continue_button(self, app):
        """Menu should have a Continue button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn_continue")
            assert btn is not None

    async def test_menu_has_load_game_button(self, app):
        """Menu should have a Load Game button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn_load")
            assert btn is not None

    async def test_menu_has_quit_button(self, app):
        """Menu should have a Quit button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn_quit")
            assert btn is not None

    async def test_clicking_new_game_navigates_to_character_creation(self, app):
        """Clicking New Game should go to character creation screen."""
        async with app.run_test() as pilot:
            await pilot.pause()
            # Click New Game button
            await pilot.click("#btn_new")
            await pilot.pause()

            # Should be on character creation screen
            screen_name = type(app.screen).__name__
            assert "CharacterCreation" in screen_name

    async def test_clicking_continue_opens_load_game(self, app):
        """Clicking Continue should open Load Game screen."""
        async with app.run_test() as pilot:
            await pilot.pause()

            await pilot.click("#btn_continue")
            await pilot.pause()

            screen_name = type(app.screen).__name__
            assert "LoadGame" in screen_name

    async def test_clicking_load_game_opens_load_screen(self, app):
        """Clicking Load Game should open Load Game screen."""
        async with app.run_test() as pilot:
            await pilot.pause()

            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("enter")
            await pilot.pause()

            screen_name = type(app.screen).__name__
            assert "LoadGame" in screen_name

    async def test_quit_exits_app(self, app):
        """Pressing Quit should exit the app."""
        async with app.run_test() as pilot:
            await pilot.pause()

            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("enter")
            await pilot.pause()

            assert not app.is_running
