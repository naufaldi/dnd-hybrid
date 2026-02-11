"""Choice system for player decision making."""

from typing import List, Optional
from ..utils.logger import get_logger
from .models import Choice, GameState

logger = get_logger(__name__)


class ChoiceSystem:
    """Handles player choice presentation and resolution."""

    def __init__(self):
        self.selected_index = 0

    def select_by_index(self, choices: List[Choice], index: int) -> Optional[Choice]:
        """Select choice by index."""
        if 0 <= index < len(choices):
            return choices[index]
        return None

    def select_by_shortcut(self, choices: List[Choice], shortcut: str) -> Optional[Choice]:
        """Select choice by keyboard shortcut."""
        for choice in choices:
            if choice.shortcut.upper() == shortcut.upper():
                return choice
        return None

    def format_choices_display(self, choices: List[Choice], selected_index: int = -1) -> str:
        """Format choices for display."""
        lines = []
        for i, choice in enumerate(choices):
            marker = "▶" if i == selected_index else " "
            lines.append(f"  [{choice.shortcut}] {marker} {choice.text}")
        return "\n".join(lines)

    def get_available_choices(self, choices: List[Choice], state: GameState) -> List[Choice]:
        """Filter choices that are available given game state."""
        available = []
        for choice in choices:
            if not all(state.flags.get(k, False) == v for k, v in choice.required_flags.items()):
                continue
            available.append(choice)
        return available
