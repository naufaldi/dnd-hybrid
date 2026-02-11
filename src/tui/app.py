"""Main TUI application."""

import uuid
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.driver import Driver
from textual.widgets import Header, Footer

from .screens import (
    MenuScreen,
    CharacterCreationScreen,
    NarrativeGameScreen,
    LoadGameScreen,
    EndingScreen,
)
from .reactivity.state_store import StateStore
from ..core.config import config
from ..entities.character import Character
from ..narrative.models import GameState
from ..narrative.scene_manager import SceneManager
from ..narrative.ending_manager import EndingManager


class DNDRoguelikeApp(App):
    """Main Textual application for AI Dungeon Chronicles (narrative D&D)."""

    TITLE = "AI Dungeon Chronicles"
    SUB_TITLE = "A Narrative D&D Adventure"

    CSS_PATH = [
        "styles/main.css",
        "styles/themes.css",
    ]

    BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    SCREENS = {
        "menu": MenuScreen,
        "character_creation": CharacterCreationScreen,
        "narrative": NarrativeGameScreen,
        "load_game": LoadGameScreen,
        "ending": EndingScreen,
    }

    def __init__(self, driver_class: Optional[type[Driver]] = None, **kwargs):
        super().__init__(driver_class=driver_class, **kwargs)

        self.state = StateStore()

        story_dir = Path(__file__).parent.parent / "story" / "scenes"
        endings_file = Path(__file__).parent.parent / "story" / "endings.yaml"
        self.scene_manager = SceneManager(story_dir)
        self.ending_manager = EndingManager(endings_file)

        self.narrative_game_state: Optional[GameState] = None
        self.narrative_initial_scene: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        yield MenuScreen(id="menu")
        yield CharacterCreationScreen(id="character_creation")
        yield LoadGameScreen(id="load_game")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.push_screen("menu")

    def action_show_menu(self) -> None:
        """Show the menu screen."""
        self.pop_screen()
        self.push_screen("menu")

    def _on_load_game_dismissed(self, result) -> None:
        """Handle load game screen dismissal."""
        if result:
            self.load_narrative_game(result)

    def start_narrative_game(
        self, character_name: str, character_class: str, race: str
    ) -> None:
        """Start a new narrative game with the given character."""
        char_id = str(uuid.uuid4())
        character = Character(
            id=char_id,
            name=character_name,
            character_class=character_class,
            race=race,
        )
        character.hit_points = character.max_hp

        game_state = GameState(
            character=character,
            current_scene="tavern_entry",
            scene_history=[],
            choices_made=[],
            flags={},
            relationships={},
            inventory=[],
            current_act=1,
            is_combat=False,
            ending_determined=None,
            turns_spent=0,
        )

        self.narrative_game_state = game_state
        self.narrative_initial_scene = "tavern_entry"

        try:
            self.push_screen("narrative")
        except ValueError:
            self.notify("Failed to load initial scene: tavern_entry")

    def load_narrative_game(self, save_data: dict) -> None:
        """Load a narrative game from save data."""
        from ..narrative.serializers import SaveDataBuilder

        try:
            game_state = SaveDataBuilder.extract_narrative_state(save_data)
            scene_id = game_state.current_scene
            scene = self.scene_manager.get_scene(scene_id)

            self.narrative_game_state = game_state
            self.narrative_initial_scene = scene_id

            self.push_screen("narrative")
        except (ValueError, KeyError) as e:
            self.notify(f"Failed to load save: {e}")

    def save_narrative_game(self, save_data: dict) -> bool:
        """Save the current narrative game."""
        try:
            import json
            import zlib
            from datetime import datetime

            config.ensure_directories()
            json_str = json.dumps(save_data, indent=2, default=str)
            compressed = zlib.compress(json_str.encode("utf-8"), level=6)
            char_name = save_data.get("narrative_state", {}).get("character", {}).get("name", "game")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{char_name}_{timestamp}.sav"
            save_path = config.save_directory / filename
            with open(save_path, "wb") as f:
                f.write(compressed)
            return True
        except Exception as e:
            self.notify(f"Failed to save: {e}")
            return False
