"""TUI screens for the game."""

from typing import Optional
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Button, ListView, ListItem
from textual.app import App
from textual import events

from ..widgets import MapWidget, StatusWidget, CombatWidget, LogWidget
from ...core.game_engine import GameState
from ...core.event_bus import GameEvents, Event
from ...world.dungeon_generator import DungeonGenerator, DungeonConfig


class MenuScreen(Screen):
    """Main menu screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.menu_items = [
            ("New Game", self.action_new_game),
            ("Continue", self.action_continue),
            ("Options", self.action_options),
            ("Quit", self.action_quit),
        ]

    def compose(self):
        """Compose the menu screen."""
        yield Container(
            Vertical(
                Static("D&D ROGUELIKE", id="title"),
                Static("A roguelike with D&D 5e mechanics", id="subtitle"),
                Static("\n" * 3),
                Static("> New Game", id="menu_0"),
                Static("  Continue", id="menu_1"),
                Static("  Options", id="menu_2"),
                Static("  Quit", id="menu_3"),
                id="menu_items",
            ),
            id="menu_container",
        )

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for menu navigation."""
        if event.key == "up":
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self._update_menu_display()
        elif event.key == "down":
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self._update_menu_display()
        elif event.key == "enter":
            self.menu_items[self.selected_index][1]()

    def _update_menu_display(self) -> None:
        """Update the menu item display."""
        for i, (_, _) in enumerate(self.menu_items):
            widget = self.query_one(f"#menu_{i}", Static)
            if i == self.selected_index:
                widget.update(f"> {self.menu_items[i][0]}")
            else:
                widget.update(f"  {self.menu_items[i][0]}")

    def action_new_game(self) -> None:
        """Start a new game."""
        self.app.push_screen("character_creation")

    def action_continue(self) -> None:
        """Continue a saved game."""
        self.notify("No saved games found")

    def action_options(self) -> None:
        """Open options menu."""
        self.notify("Options not yet implemented")

    def action_quit(self) -> None:
        """Quit the game."""
        self.app.exit()


class CharacterCreationScreen(Screen):
    """Character creation screen."""

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
                Static("\n[Enter] Next  [Escape] Back", id="cc_help"),
                id="cc_content",
            ),
            id="cc_container",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._update_display()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "enter":
            self._next_step()
        elif event.key == "escape":
            self.app.pop_screen()
        elif event.key == "up":
            self._navigate(-1)
        elif event.key == "down":
            self._navigate(1)

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

        if self.step == 0:
            value.update(f"[b]{self.character_data['name']}[/b]")
            opts.update("Type your name")
        else:
            current = [self.classes, self.races][self.step - 1]
            display = []
            for i, c in enumerate(current):
                if c == self.character_data[["character_class", "race"][self.step - 1]]:
                    display.append(f"> {c}")
                else:
                    display.append(f"  {c}")
            opts.update("\n".join(display))

    def _navigate(self, delta: int) -> None:
        """Navigate options."""
        if self.step == 0:
            return

        current_list = [self.classes, self.races][self.step - 1]
        current_val = self.character_data[["character_class", "race"][self.step - 1]]
        idx = current_list.index(current_val)
        idx = (idx + delta) % len(current_list)
        self.character_data[["character_class", "race"][self.step - 1]] = current_list[idx]
        self._update_display()

    def _next_step(self) -> None:
        """Move to the next step."""
        if self.step < 2:
            self.step += 1
            self._update_display()
        else:
            # Start the game
            self.dismiss()


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


# Export screens
__all__ = [
    "MenuScreen",
    "CharacterCreationScreen",
    "GameScreen",
    "CharacterScreen",
    "InventoryScreen",
    "LogScreen",
]
