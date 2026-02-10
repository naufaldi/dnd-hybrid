"""TUI Game Screen tests - TDD approach.

These tests define the expected behavior of the game screen.
"""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig

config.ensure_directories()


@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    return DNDRoguelikeApp()


@pytest.fixture
async def game_app(app):
    """Set up a game ready for testing."""
    async with app.run_test() as pilot:
        await pilot.pause()

        # Navigate to character creation
        await pilot.click("#btn_new")
        await pilot.pause()

        # Complete character creation
        for char in "TestHero":
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

        yield app


class TestGameScreen:
    """Test game screen functionality."""

    async def test_game_screen_is_visible(self, app):
        """Game screen should be visible after starting game."""
        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to character creation
            await pilot.click("#btn_new")
            await pilot.pause()

            # Complete creation
            for char in "Hero":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            # Start game
            await pilot.click("#btn_start")
            await pilot.pause()

            # Should be on game screen
            screen_name = type(app.screen).__name__
            assert "Game" in screen_name

    async def test_movement_north(self, app):
        """Pressing n should move player north."""
        async with app.run_test() as pilot:
            await pilot.pause()

            # Setup game
            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            player = engine.player
            initial_y = player.position[1]

            await pilot.press("n")
            await pilot.pause()

            # Player should have moved north (y decreased)
            assert player.position[1] < initial_y

    async def test_movement_south(self, app):
        """Pressing s should move player south."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            player = engine.player
            initial_y = player.position[1]

            await pilot.press("s")
            await pilot.pause()

            assert player.position[1] > initial_y

    async def test_movement_east(self, app):
        """Pressing e should move player east."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            player = engine.player
            initial_x = player.position[0]

            await pilot.press("e")
            await pilot.pause()

            assert player.position[0] > initial_x

    async def test_movement_west(self, app):
        """Pressing w should move player west."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            player = engine.player
            initial_x = player.position[0]

            await pilot.press("w")
            await pilot.pause()

            assert player.position[0] < initial_x


class TestGameScreenNavigation:
    """Test screen navigation from game screen."""

    async def test_press_c_opens_character_screen(self, app):
        """Pressing c should open character screen."""
        async with app.run_test() as pilot:
            await pilot.pause()

            # Setup game
            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            # Press c for character screen
            await pilot.press("c")
            await pilot.pause()

            # Should be on character screen
            screen_name = type(app.screen).__name__
            assert "Character" in screen_name

    async def test_press_i_opens_inventory_screen(self, app):
        """Pressing i should open inventory screen."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            await pilot.press("i")
            await pilot.pause()

            screen_name = type(app.screen).__name__
            assert "Inventory" in screen_name

    async def test_press_l_opens_log_screen(self, app):
        """Pressing l should open log screen."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            await pilot.press("l")
            await pilot.pause()

            screen_name = type(app.screen).__name__
            assert "Log" in screen_name

    async def test_press_s_saves_game(self, app):
        """Pressing s should save the game."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            # Clear any existing saves
            for f in config.save_directory.glob("*.json"):
                f.unlink()
            for f in config.save_directory.glob("*.sav"):
                f.unlink()

            await pilot.press("s")
            await pilot.pause()

            # Should have saved
            saves = list(config.save_directory.glob("*.json")) + list(
                config.save_directory.glob("*.sav")
            )
            assert len(saves) > 0


class TestGameScreenMap:
    """Test map display on game screen."""

    async def test_game_has_map_widget(self, app):
        """Game screen should have a map widget."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            map_widget = app.query_one("#map")
            assert map_widget is not None

    async def test_map_shows_player_position(self, app):
        """Map should show player position."""
        async with app.run_test() as pilot:
            await pilot.pause()

            engine = app.game_engine
            dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
            engine.current_map = dungeon
            engine.create_player("Test", "fighter", "human")
            engine.start()
            app.action_show_game()
            await pilot.pause()

            map_widget = app.query_one("#map")
            assert map_widget.player_pos == engine.player.position
