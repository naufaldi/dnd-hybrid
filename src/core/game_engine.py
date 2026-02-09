"""Main game engine (stub implementation)."""

from dataclasses import dataclass, field
from enum import Enum, auto
from .event_bus import EventBus, event_bus, GameEvents


class GameState(Enum):
    """Game state."""
    MENU = auto()
    PLAYING = auto()
    COMBAT = auto()
    PAUSED = auto()
    GAMEOVER = auto()


@dataclass
class GameEngine:
    """Main game engine."""

    state: GameState = GameState.MENU
    event_bus: EventBus = field(default_factory=lambda: event_bus)
    current_floor: int = 1
    turn_count: int = 0

    def start(self) -> None:
        """Start the game."""
        self.state = GameState.PLAYING
        self.event_bus.publish(GameEvents.GAME_STATE_CHANGE, {"state": self.state})

    def stop(self) -> None:
        """Stop the game."""
        self.state = GameState.GAMEOVER
        self.event_bus.publish(GameEvents.GAME_STATE_CHANGE, {"state": self.state})

    def pause(self) -> None:
        """Pause the game."""
        self.state = GameState.PAUSED

    def resume(self) -> None:
        """Resume the game."""
        self.state = GameState.PLAYING

    def get_state(self) -> dict:
        """Get current game state for serialization."""
        return {
            "state": self.state.name,
            "current_floor": self.current_floor,
            "turn_count": self.turn_count,
        }
