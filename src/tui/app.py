"""Main TUI application."""

import asyncio
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.driver import Driver
from textual.widgets import Header, Footer

from .screens import (
    GameScreen,
    MenuScreen,
    CharacterScreen,
    InventoryScreen,
    LogScreen,
    CharacterCreationScreen,
)
from .reactivity.state_store import StateStore
from ..core.game_engine import GameEngine, GameState
from ..core.event_bus import event_bus, GameEvents, Event


class DNDRoguelikeApp(App):
    """Main Textual application for D&D Roguelike."""

    TITLE = "D&D Roguelike"
    SUB_TITLE = "A roguelike with D&D 5e mechanics"

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
        "game": GameScreen,
        "character": CharacterScreen,
        "character_creation": CharacterCreationScreen,
        "inventory": InventoryScreen,
        "log": LogScreen,
    }

    def __init__(self, driver_class: Optional[type[Driver]] = None, **kwargs):
        super().__init__(driver_class=driver_class, **kwargs)

        # Game engine instance
        self.game_engine = GameEngine()

        # State store for reactive UI updates
        self.state = StateStore()

        # Subscribe to game events
        event_bus.subscribe(GameEvents.GAME_STATE_CHANGE, self._on_game_state_change)
        event_bus.subscribe(GameEvents.COMBAT, self._on_combat_event)
        event_bus.subscribe(GameEvents.MOVEMENT, self._on_movement_event)
        event_bus.subscribe(GameEvents.PLAYER_ACTION, self._on_player_action)

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        yield MenuScreen(id="menu")
        yield CharacterCreationScreen(id="character_creation")
        yield GameScreen(id="game")
        yield CharacterScreen(id="character")
        yield InventoryScreen(id="inventory")
        yield LogScreen(id="log")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Start at menu screen
        self.push_screen("menu")

    # =========================================================================
    # Screen Navigation
    # =========================================================================

    def action_show_game(self) -> None:
        """Show the game screen."""
        self.push_screen("game")

    def action_show_menu(self) -> None:
        """Show the menu screen."""
        # Pop all screens and return to menu
        self.pop_screen()
        self.push_screen("menu")

    def action_show_character(self) -> None:
        """Show the character screen."""
        self.push_screen("character")

    def action_show_inventory(self) -> None:
        """Show the inventory screen."""
        self.push_screen("inventory")

    def action_show_log(self) -> None:
        """Show the log screen."""
        self.push_screen("log")

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def _on_game_state_change(self, event: Event) -> None:
        """Handle game state changes."""
        state = event.data.get("state")
        self.state.game_state = state.name if state else "MENU"

        if state == GameState.GAMEOVER:
            self.notify("Game Over! Press Enter to return to menu.")

    def _on_combat_event(self, event: Event) -> None:
        """Handle combat events."""
        action = event.data.get("action")
        if action == "hit":
            target = event.data.get("target")
            damage = event.data.get("damage")
            critical = event.data.get("critical", False)
            msg = f"Hit {target.name} for {damage} damage!"
            if critical:
                msg = "CRITICAL HIT! " + msg
            self.notify(msg)
        elif action == "miss":
            self.notify("Attack missed!")

    def _on_movement_event(self, event: Event) -> None:
        """Handle movement events."""
        try:
            game_screen = self.query_one("#game", GameScreen)
            if hasattr(game_screen, "update_view"):
                game_screen.update_view()
        except Exception:
            pass

    def _on_player_action(self, event: Event) -> None:
        """Handle player actions."""
        action = event.data.get("action")
        if action == "pickup":
            item = event.data.get("item")
            self.notify(f"Picked up {item.name}")
        elif action == "level_up":
            player = event.data.get("player")
            self.notify(f"Level Up! You are now level {player.level}")

    # =========================================================================
    # Game Control
    # =========================================================================

    async def start_game(self, character_name: str, character_class: str, race: str) -> None:
        """Start a new game with the given character."""
        # Create player
        self.game_engine.create_player(character_name, character_class, race)

        # Start the game
        self.game_engine.start()

        # Show game screen
        self.action_show_game()

    def save_game(self, filename: Optional[str] = None) -> bool:
        """Save the current game."""
        from ..persistence.save_manager import create_save_manager

        if not self.game_engine.player:
            return False

        state = self.game_engine.get_state()
        state["character"] = {
            "id": self.game_engine.player.id,
            "name": self.game_engine.player.name,
            "level": self.game_engine.player.level,
        }

        save_manager = create_save_manager()
        try:
            save_manager.save_game(state, filename)
            self.notify("Game saved!")
            return True
        except Exception as e:
            self.notify(f"Failed to save: {e}")
            return False
