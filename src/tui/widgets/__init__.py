"""Widgets for displaying game data."""

from typing import Optional, Tuple
from textual.widget import Widget
from textual.widgets import Static


class MapWidget(Widget):
    """Widget for displaying the game map.

    Renders the dungeon map with tiles, entities, and FOV.
    """

    def __init__(self, map_data=None, **kwargs):
        super().__init__(**kwargs)
        self.map_data = map_data
        self.visible_tiles: set = set()
        self.explored_tiles: set = set()
        self.player_pos: Optional[Tuple[int, int]] = None
        self.enemy_positions: dict = {}
        self.item_positions: dict = {}

        self.tile_chars = {
            "FLOOR": ".",
            "WALL": "#",
            "STAIRS_UP": "<",
            "STAIRS_DOWN": ">",
            "DOOR_CLOSED": "+",
            "DOOR_OPEN": "/",
            "WATER": "~",
            "LAVA": "^",
            "VOID": " ",
        }

    def set_map(self, map_data) -> None:
        """Set the map data to display."""
        self.map_data = map_data
        self.refresh()

    def set_visible_tiles(self, tiles: set) -> None:
        """Set currently visible tiles (FOV)."""
        self.visible_tiles = tiles
        self.refresh()

    def set_explored_tiles(self, tiles: set) -> None:
        """Set explored but not currently visible tiles."""
        self.explored_tiles = tiles
        self.refresh()

    def set_player(self, pos: Tuple[int, int]) -> None:
        """Set player position."""
        self.player_pos = pos
        self.refresh()

    def set_enemies(self, positions: dict) -> None:
        """Set enemy positions {id: (x, y)}."""
        self.enemy_positions = positions
        self.refresh()

    def set_items(self, positions: dict) -> None:
        """Set item positions {id: (x, y)}."""
        self.item_positions = positions
        self.refresh()

    def render(self) -> str:
        """Render the map."""
        if not self.map_data:
            return "No map loaded"

        lines = []
        height = self.map_data.height
        width = self.map_data.width

        for y in range(height):
            line = ""
            for x in range(width):
                char = self._get_tile_char(x, y)
                line += char
            lines.append(line)

        return "\n".join(lines)

    def _get_tile_char(self, x: int, y: int) -> str:
        """Get the character to display for a tile."""
        pos = (x, y)

        if self.player_pos == pos:
            return "@"

        for enemy_id, enemy_pos in self.enemy_positions.items():
            if enemy_pos == pos:
                return "E"

        for item_id, item_pos in self.item_positions.items():
            if item_pos == pos:
                return "*"

        if pos not in self.visible_tiles:
            if pos in self.explored_tiles:
                tile = self.map_data.get_tile(x, y)
                if tile:
                    base_char = self.tile_chars.get(tile.tile_type.name, " ")
                    return base_char.lower()
                return " "
            else:
                return " "

        tile = self.map_data.get_tile(x, y)
        if tile:
            return self.tile_chars.get(tile.tile_type.name, "?")

        return " "


class StatusWidget(Widget):
    """Widget for displaying player status."""

    def __init__(self, player=None, **kwargs):
        super().__init__(**kwargs)
        self.player = player

    def set_player(self, player) -> None:
        """Set the player to display."""
        self.player = player
        self.refresh()

    def render(self) -> str:
        """Render the status display."""
        if not self.player:
            return "No player"

        p = self.player
        lines = [
            f"Name: {p.name}",
            f"Level {p.level} {p.race} {p.character_class}",
            f"HP: {p.current_hp}/{p.max_hp}",
            f"AC: {p.armor_class}",
            f"XP: {p.experience}",
            f"Floor: {p.current_floor}",
        ]
        return "\n".join(lines)


class CombatWidget(Widget):
    """Widget for displaying combat information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combat_log: list = []
        self.max_lines = 10

    def add_entry(self, text: str) -> None:
        """Add a combat log entry."""
        self.combat_log.append(text)
        if len(self.combat_log) > self.max_lines:
            self.combat_log.pop(0)
        self.refresh()

    def clear(self) -> None:
        """Clear the combat log."""
        self.combat_log.clear()
        self.refresh()

    def render(self) -> str:
        """Render the combat log."""
        if not self.combat_log:
            return "No recent combat"
        return "\n".join(self.combat_log)


class LogWidget(Widget):
    """Widget for displaying game log messages."""

    def __init__(self, max_lines: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.messages: list = []
        self.max_lines = max_lines

    def add_message(self, text: str, level: str = "info") -> None:
        """Add a log message."""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append({"timestamp": timestamp, "level": level, "text": text})
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
        self.refresh()

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.refresh()

    def render(self) -> str:
        """Render the log messages."""
        if not self.messages:
            return "No messages"

        lines = []
        for msg in self.messages[-self.max_lines :]:
            level_marker = {"debug": "D", "info": "I", "warning": "!", "error": "X"}.get(
                msg["level"], "?"
            )

            lines.append(f"[{msg['timestamp']}] {level_marker}: {msg['text']}")

        return "\n".join(lines)
