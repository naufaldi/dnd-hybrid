"""Main TUI application."""

import os
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
    CombatScreen,
)
from .reactivity.state_store import StateStore
from ..core.config import config
from ..entities.character import Character
from ..narrative.models import GameState
from ..narrative.scene_manager import SceneManager
from ..narrative.ending_manager import EndingManager
from ..narrative.ai_service import create_ai_service
from ..narrative.npc_memory import NPCMemoryManager


def _load_api_key() -> Optional[str]:
    """Load OpenRouter API key from common sources."""
    # 1. Environment variable (already set)
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ.get("OPENROUTER_API_KEY")

    # 2. Check for .env file in project root or home directory
    candidates = [
        Path.cwd() / ".env",
        Path.home() / ".dnd_roguelike" / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]

    for env_path in candidates:
        if env_path.exists():
            try:
                content = env_path.read_text()
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("OPENROUTER_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key:
                            return key
            except Exception:
                pass

    # 3. Check config file
    config_dir = Path.home() / ".dnd_roguelike"
    config_file = config_dir / "config"
    if config_file.exists():
        try:
            content = config_file.read_text()
            for line in content.splitlines():
                if line.startswith("openrouter_api_key="):
                    key = line.split("=", 1)[1].strip()
                    if key:
                        return key
        except Exception:
            pass

    return None


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
        "combat": CombatScreen,
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
        self.ai_service = create_ai_service(api_key=_load_api_key())
        self.npc_memory = NPCMemoryManager()

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
        # Only pop if there's more than the default screen
        if len(self._screen_stack) > 1:
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
