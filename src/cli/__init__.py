"""Command-line interface for the game."""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import re


class CommandType(Enum):
    """Types of commands."""

    MOVE = auto()
    WAIT = auto()
    ATTACK = auto()
    PICKUP = auto()
    DROP = auto()
    USE = auto()
    EQUIP = auto()
    UNEQUIP = auto()
    LOOK = auto()
    INVENTORY = auto()
    CHARACTER = auto()
    MAP = auto()
    SAVE = auto()
    LOAD = auto()
    QUIT = auto()
    HELP = auto()
    UNKNOWN = auto()


@dataclass
class Command:
    """Represents a parsed command."""

    command_type: CommandType
    arguments: List[str]
    raw_input: str


class CommandParser:
    """Parses user input into commands."""

    # Command patterns
    COMMAND_PATTERNS = {
        # Movement
        r"^(n|north)$": (CommandType.MOVE, ["north"]),
        r"^(s|south)$": (CommandType.MOVE, ["south"]),
        r"^(e|east)$": (CommandType.MOVE, ["east"]),
        r"^(w|west)$": (CommandType.MOVE, ["west"]),
        r"^(ne|northeast)$": (CommandType.MOVE, ["northeast"]),
        r"^(nw|northwest)$": (CommandType.MOVE, ["northwest"]),
        r"^(se|southeast)$": (CommandType.MOVE, ["southeast"]),
        r"^(sw|southwest)$": (CommandType.MOVE, ["southwest"]),
        r"^(\.|\s|wait)$": (CommandType.WAIT, []),
        r"^go\s+(north|south|east|west|northeast|northwest|southeast|southwest)$": (CommandType.MOVE, []),
        r"^go\s+(\w+)$": (CommandType.MOVE, []),

        # Combat
        r"^(?:a|attack)(?:\s+(.+))?$": (CommandType.ATTACK, []),
        r"^(?:k|kill)(?:\s+(.+))?$": (CommandType.ATTACK, []),

        # Inventory
        r"^(?:g|get|grab)(?:\s+(.+))?$": (CommandType.PICKUP, []),
        r"^(?:,|pickup)(?:\s+(.+))?$": (CommandType.PICKUP, []),
        r"^(?:d|drop)(?:\s+(.+))?$": (CommandType.DROP, []),
        r"^(?:u|use)(?:\s+(.+))?$": (CommandType.USE, []),
        r"^(?:e|equip)(?:\s+(.+))?$": (CommandType.EQUIP, []),
        r"^(?:t|take)(?:\s+(.+))?$": (CommandType.EQUIP, []),
        r"^unequip(?:\s+(.+))?$": (CommandType.UNEQUIP, []),

        # Info
        r"^(?:l|look)(?:\s+(.*))?$": (CommandType.LOOK, []),
        r"^(?:i|inventory)$": (CommandType.INVENTORY, []),
        r"^inv$": (CommandType.INVENTORY, []),
        r"^(?:c|character)$": (CommandType.CHARACTER, []),
        r"^(?:m|map)(?:\s+(.*))?$": (CommandType.MAP, []),

        # Game
        r"^(?:s|save)(?:\s+(.*))?$": (CommandType.SAVE, []),
        r"^load(?:\s+(.+))?$": (CommandType.LOAD, []),
        r"^restore(?:\s+(.+))?$": (CommandType.LOAD, []),
        r"^(?:q|quit)$": (CommandType.QUIT, []),
        r"^(?:h|help|\?)$": (CommandType.HELP, []),
    }

    def parse(self, input_str: str) -> Command:
        """Parse user input into a command.

        Args:
            input_str: Raw user input.

        Returns:
            Parsed Command object.
        """
        input_str = input_str.strip().lower()

        for pattern, (cmd_type, default_args) in self.COMMAND_PATTERNS.items():
            match = re.match(pattern, input_str)
            if match:
                # Extract arguments from capture groups
                args = []
                for group in match.groups():
                    if group:
                        args.append(group.strip())

                return Command(
                    command_type=cmd_type,
                    arguments=args if args else default_args,
                    raw_input=input_str
                )

        # No match found
        return Command(
            command_type=CommandType.UNKNOWN,
            arguments=[input_str],
            raw_input=input_str
        )

    def get_help_text(self) -> str:
        """Get help text for all commands."""
        help_sections = {
            "Movement": [
                ("n/s/e/w", "Move north/south/east/west"),
                ("ne/nw/se/sw", "Move diagonally"),
                (". or space", "Wait one turn"),
            ],
            "Combat": [
                ("a [target]", "Attack target"),
                ("k [target]", "Kill target"),
            ],
            "Inventory": [
                ("g [item]", "Pick up item"),
                ("d [item]", "Drop item"),
                ("u [item]", "Use item"),
                ("e [item]", "Equip item"),
                ("unequip [item]", "Unequip item"),
            ],
            "Information": [
                ("l [target]", "Look at target/area"),
                ("i", "Show inventory"),
                ("c", "Show character"),
                ("m", "Show map"),
            ],
            "Game": [
                ("s [name]", "Save game"),
                ("load [name]", "Load game"),
                ("h", "Show this help"),
                ("q", "Quit game"),
            ],
        }

        lines = ["Available commands:", ""]

        for section, commands in help_sections.items():
            lines.append(f"{section}:")
            for cmd, desc in commands:
                lines.append(f"  {cmd:20} - {desc}")
            lines.append("")

        return "\n".join(lines)


class CLI:
    """Command-line interface for the game."""

    def __init__(self):
        self.parser = CommandParser()
        self.game_engine = None

    def set_game_engine(self, engine):
        """Set the game engine to control."""
        self.game_engine = engine

    def run(self):
        """Run the CLI game loop."""
        print("D&D Roguelike - CLI Mode")
        print("Type 'h' for help")
        print()

        while True:
            try:
                prompt = self._get_prompt()
                command_str = input(prompt).strip()

                if not command_str:
                    continue

                command = self.parser.parse(command_str)
                self._execute_command(command)

            except KeyboardInterrupt:
                print("\nUse 'q' to quit")
            except EOFError:
                print("\nGoodbye!")
                break

    def _get_prompt(self) -> str:
        """Get the command prompt."""
        if self.game_engine and self.game_engine.player:
            return f"({self.game_engine.player.name})> "
        return "> "

    def _execute_command(self, command: Command) -> None:
        """Execute a parsed command."""
        if command.command_type == CommandType.UNKNOWN:
            print(f"Unknown command: {command.raw_input}")
            print("Type 'h' for help")
            return

        if command.command_type == CommandType.HELP:
            print(self.parser.get_help_text())
            return

        if command.command_type == CommandType.QUIT:
            print("Goodbye!")
            raise EOFError

        if not self.game_engine:
            print("No game in progress")
            return

        # Execute game commands
        action = {"action": command.command_type.name.lower()}

        if command.arguments:
            action["target"] = command.arguments[0]

        result = self.game_engine.player_turn(action)
        if result:
            self.game_engine.enemy_turns()
        else:
            print("Action failed")

    def handle_movement(self, direction: str) -> None:
        """Handle movement input."""
        if not self.game_engine:
            return

        self.game_engine.player_turn({"action": "move", "direction": direction})
        self.game_engine.enemy_turns()


# Module exports
__all__ = ["CommandParser", "Command", "CommandType", "CLI"]
