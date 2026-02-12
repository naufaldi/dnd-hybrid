"""TUI screens for the game."""

from typing import Optional
from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, ListView, ListItem
from textual.app import App
from textual import events

from ..widgets import MapWidget, StatusWidget, CombatWidget, LogWidget
from ...core.game_engine import GameState
from ...core.event_bus import GameEvents, Event
from ...world.dungeon_generator import DungeonGenerator, DungeonConfig
from ...combat.dice_display import DiceDisplay
from ...narrative.models import Scene, Choice, GameState as NarrativeGameState


class MenuScreen(Screen):
    """Main menu screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.menu_options = ["New Game", "Continue", "Load Game", "Quit"]
        self.buttons = ["btn_new", "btn_continue", "btn_load", "btn_quit"]

    def compose(self):
        """Compose the menu screen."""
        yield Container(
            Vertical(
                Static("AI DUNGEON CHRONICLES", id="title"),
                Static("A Narrative D&D Adventure", id="subtitle"),
                Static("\n" * 5),
                Static("  Use UP/DOWN arrows to select", id="hint"),
                Static("\n"),
                Button("New Game", id="btn_new", variant="primary"),
                Static("\n"),
                Button("Continue", id="btn_continue"),
                Static("\n"),
                Button("Load Game", id="btn_load"),
                Static("\n"),
                Button("Quit", id="btn_quit"),
                id="menu_content",
            ),
            id="menu_container",
        )

    def on_mount(self):
        """Focus first button on mount."""
        self.query_one("#btn_new").focus()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for menu navigation."""
        if event.key == "up":
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
            self._update_focus()
        elif event.key == "down":
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
            self._update_focus()
        elif event.key == "enter":
            # Trigger the action for current selection
            if self.selected_index == 0:
                self.action_new_game()
            elif self.selected_index == 1:
                self.action_continue()
            elif self.selected_index == 2:
                self.action_load_game()
            elif self.selected_index == 3:
                self.action_quit()

    def _update_focus(self):
        """Update button focus based on selected_index."""
        btn_id = self.buttons[self.selected_index]
        self.query_one(f"#{btn_id}").focus()

    def action_new_game(self) -> None:
        """Start a new game."""

        def on_character_created(data: dict) -> None:
            if data:
                self.app.call_later(
                    self.app.start_narrative_game,
                    data["name"],
                    data["character_class"],
                    data["race"],
                )

        self.app.push_screen("character_creation", on_character_created)

    def on_screen_dismissed(self, screen: Screen) -> None:
        """Handle screen dismissal."""
        pass

    def action_continue(self) -> None:
        """Continue a saved game."""
        self.app.push_screen("load_game", self.app._on_load_game_dismissed)

    def action_load_game(self) -> None:
        """Show load game screen."""
        self.app.push_screen("load_game", self.app._on_load_game_dismissed)

    def action_quit(self) -> None:
        """Quit the game."""
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "btn_new":
            self.action_new_game()
        elif button_id == "btn_continue":
            self.action_continue()
        elif button_id == "btn_load":
            self.action_load_game()
        elif button_id == "btn_quit":
            self.action_quit()


class CharacterCreationScreen(Screen):
    """Character creation screen."""

    BINDINGS = [
        Binding("up", "navigate_up", "Up"),
        Binding("down", "navigate_down", "Down"),
        Binding("enter", "confirm", "Enter"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 0
        self.character_data = {
            "name": "",
            "character_class": "fighter",
            "race": "human",
        }
        self.classes = ["fighter", "wizard", "rogue", "cleric"]
        self.races = ["human", "elf", "dwarf", "halfling"]

    def compose(self):
        """Compose the character creation screen."""
        yield Container(
            Vertical(
                Static("Create Your Character", id="cc_title"),
                Static("", id="cc_prompt"),
                Static("", id="cc_value"),
                Static("", id="cc_options"),
                Input("", id="name_input", placeholder="Type your name..."),
                Button("Start Game", id="btn_start", variant="primary"),
                Static("\n[Enter] Next  [Escape] Back", id="cc_help"),
                id="cc_content",
            ),
            id="cc_container",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._update_display()
        self._focus_current_step()

    def _focus_current_step(self) -> None:
        """Focus the appropriate widget for the current step."""
        if self.step == 0:
            self.query_one("#name_input", Input).focus()
        else:
            self.query_one("#cc_options", Static).focus()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses when Input has focus (step 0); BINDINGS handle step 1+."""
        if self.step == 0:
            if event.key == "enter":
                self.action_confirm()
            elif event.key == "escape":
                self.action_back()
        # Note: up/down keys for steps > 0 are handled by BINDINGS

    def action_navigate_up(self) -> None:
        if self.step > 0:
            self._navigate(-1)

    def action_navigate_down(self) -> None:
        if self.step > 0:
            self._navigate(1)

    def action_confirm(self) -> None:
        self._next_step()

    def action_back(self) -> None:
        self.app.pop_screen()

    def _update_display(self) -> None:
        """Update the display based on current step."""
        prompts = [
            "Enter your name:",
            "Choose your class:",
            "Choose your race:",
        ]
        options = [
            "",
            ", ".join(self.classes),
            ", ".join(self.races),
        ]

        prompt = self.query_one("#cc_prompt", Static)
        prompt.update(prompts[self.step])

        value = self.query_one("#cc_value", Static)
        opts = self.query_one("#cc_options", Static)
        name_input = self.query_one("#name_input", Input)
        start_btn = self.query_one("#btn_start", Button)

        if self.step == 0:
            value.update(f"[b]{self.character_data['name']}[/b]")
            name_input.display = True
            name_input.can_focus = True
            start_btn.display = False
            opts.update("Type your name and press Enter")
        elif self.step == 1:
            name_input.display = False
            name_input.can_focus = False
            start_btn.display = False
            current = self.classes
            display = []
            for c in current:
                if c == self.character_data["character_class"]:
                    display.append(f"> {c}")
                else:
                    display.append(f"  {c}")
            opts.update("\n".join(display))
        else:
            name_input.display = False
            name_input.can_focus = False
            start_btn.display = True
            current = self.races
            display = []
            for c in current:
                if c == self.character_data["race"]:
                    display.append(f"> {c}")
                else:
                    display.append(f"  {c}")
            opts.update("\n".join(display))

    def _navigate(self, delta: int) -> None:
        """Navigate options."""
        if self.step == 0:
            self._focus_current_step()
            return

        current_list = [self.classes, self.races][self.step - 1]
        current_list = list(current_list) if not isinstance(current_list, list) else current_list
        current_val = self.character_data[["character_class", "race"][self.step - 1]]
        idx = current_list.index(current_val)
        idx = (idx + delta) % len(current_list)
        self.character_data[["character_class", "race"][self.step - 1]] = current_list[idx]
        self._update_display()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for name entry."""
        if self.step == 0:
            self.character_data["name"] = event.value
            self._update_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_start":
            self.dismiss(self.character_data)

    def _next_step(self) -> None:
        """Move to the next step."""
        if self.step == 0:
            if not self.character_data["name"].strip():
                self.notify("Please enter a name")
                return
        if self.step == 1 and self.character_data["character_class"] == "fighter":
            self.dismiss(self.character_data)
            return
        if self.step < 2:
            self.step += 1
            self._update_display()
            self._focus_current_step()
        else:
            self.dismiss(self.character_data)


class GameScreen(Screen):
    """Main game screen with map and status."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fov_cache: set = set()
        self.explored_cache: set = set()

    def compose(self):
        """Compose the game screen."""
        yield Horizontal(
            Vertical(MapWidget(id="map"), id="map_container"),
            Vertical(StatusWidget(id="status"), CombatWidget(id="combat"), id="sidebar"),
            id="game_layout",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Generate initial dungeon
        self._generate_dungeon()

    def _generate_dungeon(self) -> None:
        """Generate a new dungeon."""
        config = DungeonConfig(
            width=80,
            height=24,
            min_room_size=6,
            max_room_size=12,
            min_rooms=6,
            max_rooms=10,
        )
        dungeon = DungeonGenerator(config).generate()

        # Set map on widget
        map_widget = self.query_one("#map", MapWidget)
        map_widget.set_map(dungeon)

    def update_view(self) -> None:
        """Update the map view."""
        map_widget = self.query_one("#map", MapWidget)
        status_widget = self.query_one("#status", StatusWidget)

        engine = self.app.game_engine
        if not engine.player:
            return

        # Update player position
        map_widget.set_player(engine.player.position)

        # Update FOV
        visible = engine.visible_tiles
        map_widget.set_visible_tiles(visible)

        # Update enemies
        enemy_positions = {e.id: e.position for e in engine.enemies}
        map_widget.set_enemies(enemy_positions)

        # Update items
        item_positions = {i.id: i.position for i in engine.items}
        map_widget.set_items(item_positions)

        # Update status
        status_widget.set_player(engine.player)

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for movement and actions."""
        engine = self.app.game_engine

        if engine.state not in (GameState.PLAYING, GameState.COMBAT):
            return

        direction_map = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "y": "northwest",
            "u": "northeast",
            "b": "southwest",
            "j": "southeast",
        }

        if event.key in direction_map:
            engine.player_turn({"action": "move", "direction": direction_map[event.key]})
            engine.enemy_turns()
            self.update_view()
        elif event.key == "." or event.key == "space":
            engine.player_turn({"action": "wait"})
            engine.enemy_turns()
            self.update_view()
        elif event.key == "," or event.key == "g":
            # Pick up item (simplified)
            pass
        elif event.key == "i":
            self.app.action_show_inventory()
        elif event.key == "c":
            self.app.action_show_character()
        elif event.key == "l":
            self.app.action_show_log()
        elif event.key == "s":
            # Save game
            self.app.save_game()
        elif event.key == "escape":
            self.app.action_show_menu()


class CharacterScreen(Screen):
    """Character sheet screen."""

    def compose(self):
        """Compose the character screen."""
        yield Container(
            Vertical(
                Static("Character Sheet", id="char_title"),
                Static("", id="char_details"),
                id="char_content",
            ),
            id="char_container",
        )

    def on_mount(self) -> None:
        """Update character display."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the character details display."""
        engine = self.app.game_engine
        if not engine.player:
            return

        p = engine.player
        details = [
            f"[b]{p.name}[/b]",
            f"Level {p.level} {p.race} {p.character_class}",
            "",
            "Attributes:",
            f"  STR {p.strength} ({p.strength_mod:+d})",
            f"  DEX {p.dexterity} ({p.dexterity_mod:+d})",
            f"  CON {p.constitution} ({p.constitution_mod:+d})",
            f"  INT {p.intelligence} ({p.intelligence_mod:+d})",
            f"  WIS {p.wisdom} ({p.wisdom_mod:+d})",
            f"  CHA {p.charisma} ({p.charisma_mod:+d})",
            "",
            "Combat:",
            f"  HP: {p.current_hp}/{p.max_hp}",
            f"  AC: {p.armor_class}",
            f"  Proficiency: +{p.proficiency_bonus}",
            "",
            f"Experience: {p.experience}",
        ]

        widget = self.query_one("#char_details", Static)
        widget.update("\n".join(details))


class InventoryScreen(Screen):
    """Inventory management screen."""

    def compose(self):
        """Compose the inventory screen."""
        yield Container(
            Vertical(
                Static("Inventory", id="inv_title"),
                ListView(id="inv_list"),
                Static("", id="inv_details"),
                id="inv_content",
            ),
            id="inv_container",
        )

    def on_mount(self) -> None:
        """Update inventory display."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the inventory list."""
        engine = self.app.game_engine
        if not engine.player:
            return

        # For now, show floor items
        items = [i.name for i in engine.items]

        list_view = self.query_one("#inv_list", ListView)
        list_view.clear()

        for item_name in items:
            list_view.append(ListItem(Static(item_name)))


class LogScreen(Screen):
    """Game log screen."""

    def compose(self):
        """Compose the log screen."""
        yield Container(
            Vertical(
                Static("Game Log", id="log_title"),
                Static("", id="log_content"),
                id="log_content_container",
            ),
            id="log_container",
        )

    def on_mount(self) -> None:
        """Update log display."""
        # For now, show placeholder
        widget = self.query_one("#log_content", Static)
        widget.update("Game events will appear here.")


from .narrative_game_screen import NarrativeGameScreen
from .load_game_screen import LoadGameScreen
from .ending_screen import EndingScreen


# Export screens
__all__ = [
    "MenuScreen",
    "CharacterCreationScreen",
    "GameScreen",
    "CharacterScreen",
    "InventoryScreen",
    "LogScreen",
    "NarrativeGameScreen",
    "LoadGameScreen",
    "EndingScreen",
]
