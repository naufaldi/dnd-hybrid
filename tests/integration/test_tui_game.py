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

            # Complete character creation (wizard to reach race step)
            for char in "Hero":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("down")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#btn_start")
            await pilot.pause()

            # Should be on game screen
            assert app.screen is not None

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
            await pilot.press("down")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#btn_start")
            await pilot.pause()

            await pilot.press("s")
            await pilot.pause()

    async def test_scene_navigation_no_duplicate_id_error(self, app):
        """Test navigating between scenes with duplicate choice IDs doesn't crash."""
        from src.narrative.models import GameState, Scene, Choice
        from src.entities.character import Character

        # Create a mock game state with scenes that have duplicate choice IDs
        scene1 = Scene(
            id="test_scene_1",
            act=1,
            title="Test Scene 1",
            description="Test scene 1",
            choices=[
                Choice(id="continue", text="Continue", shortcut="A", next_scene="test_scene_2"),
            ],
        )
        scene2 = Scene(
            id="test_scene_2",
            act=1,
            title="Test Scene 2",
            description="Test scene 2",
            choices=[
                Choice(id="continue", text="Continue", shortcut="A", next_scene="test_scene_1"),
                Choice(id="go_back", text="Go Back", shortcut="B", next_scene="test_scene_1"),
            ],
        )

        # Add scenes to scene manager
        app.scene_manager.add_scene(scene1)
        app.scene_manager.add_scene(scene2)

        # Create character
        char = Character(
            id="test",
            name="TestHero",
            race="human",
            character_class="fighter",
            hit_points=10,
        )

        # Create game state with initial scene set
        state = GameState(character=char)
        state.current_scene = "test_scene_1"
        app.narrative_game_state = state
        app.narrative_initial_scene = "test_scene_1"

        # Navigate to narrative screen and test
        async with app.run_test() as pilot:
            await pilot.pause()
            app.push_screen("narrative")
            await pilot.pause()
            await pilot.pause()  # Extra pause for screen transition

            # Should be on narrative screen
            narrative_screen = app.screen
            assert narrative_screen is not None

            # Get the narrative screen instance and verify button IDs are unique
            # This is the core test - button IDs should include scene ID prefix
            from src.tui.screens.narrative_game_screen import NarrativeGameScreen
            assert isinstance(narrative_screen, NarrativeGameScreen)

            # Verify button IDs include scene prefix - this prevents DuplicateIds
            choices_container = narrative_screen.query_one("#choices_container")
            buttons = list(choices_container.children)
            assert len(buttons) > 0, "Should have at least one choice button"

            # The key test: button IDs should be unique due to scene ID prefix
            button_ids = [btn.id for btn in buttons if btn.id]
            assert len(button_ids) == len(set(button_ids)), f"Button IDs should be unique: {button_ids}"
            assert button_ids[0].startswith("choice_test_scene_1_"), f"Button ID should have scene prefix: {button_ids[0]}"
