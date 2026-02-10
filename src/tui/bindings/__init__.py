"""Input bindings for the game."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from enum import Enum, auto


class KeyCategory(Enum):
    """Categories of key bindings."""

    MOVEMENT = auto()
    COMBAT = auto()
    INTERACTION = auto()
    UI = auto()
    DEBUG = auto()


@dataclass
class KeyBinding:
    """Represents a key binding."""

    key: str
    action: str
    description: str
    category: KeyCategory
    handler: Optional[Callable] = None


# Movement bindings
MOVEMENT_BINDINGS = [
    KeyBinding("n", "move_north", "Move north", KeyCategory.MOVEMENT),
    KeyBinding("s", "move_south", "Move south", KeyCategory.MOVEMENT),
    KeyBinding("e", "move_east", "Move east", KeyCategory.MOVEMENT),
    KeyBinding("w", "move_west", "Move west", KeyCategory.MOVEMENT),
    KeyBinding("y", "move_northwest", "Move northwest", KeyCategory.MOVEMENT),
    KeyBinding("u", "move_northeast", "Move northeast", KeyCategory.MOVEMENT),
    KeyBinding("b", "move_southwest", "Move southwest", KeyCategory.MOVEMENT),
    KeyBinding("j", "move_southeast", "Move southeast", KeyCategory.MOVEMENT),
    KeyBinding(".", "wait", "Wait a turn", KeyCategory.MOVEMENT),
    KeyBinding("space", "wait", "Wait a turn", KeyCategory.MOVEMENT),
]

# Combat bindings
COMBAT_BINDINGS = [
    KeyBinding("a", "attack", "Attack adjacent enemy", KeyCategory.COMBAT),
    KeyBinding("f", "fire", "Fire ranged weapon", KeyCategory.COMBAT),
    KeyBinding("h", "cast_spell", "Cast a spell", KeyCategory.COMBAT),
]

# Interaction bindings
INTERACTION_BINDINGS = [
    KeyBinding("g", "pickup", "Pick up item", KeyCategory.INTERACTION),
    KeyBinding(",", "pickup", "Pick up item", KeyCategory.INTERACTION),
    KeyBinding("i", "show_inventory", "Show inventory", KeyCategory.INTERACTION),
    KeyBinding("e", "equip", "Equip item", KeyCategory.INTERACTION),
    KeyBinding("d", "drop", "Drop item", KeyCategory.INTERACTION),
    KeyBinding("u", "use", "Use item", KeyCategory.INTERACTION),
    KeyBinding("r", "read", "Read scroll", KeyCategory.INTERACTION),
]

# UI bindings
UI_BINDINGS = [
    KeyBinding("c", "show_character", "Show character sheet", KeyCategory.UI),
    KeyBinding("m", "show_map", "Show map (fullscreen)", KeyCategory.UI),
    KeyBinding("l", "show_log", "Show message log", KeyCategory.UI),
    KeyBinding("?", "show_help", "Show help", KeyCategory.UI),
    KeyBinding("escape", "show_menu", "Show menu", KeyCategory.UI),
    KeyBinding("s", "save", "Save game", KeyCategory.UI),
]

# Debug bindings (only in debug mode)
DEBUG_BINDINGS = [
    KeyBinding("ctrl+d", "toggle_debug", "Toggle debug mode", KeyCategory.DEBUG),
    KeyBinding("ctrl+g", "goto_floor", "Go to floor (debug)", KeyCategory.DEBUG),
    KeyBinding("ctrl+x", "kill_enemies", "Kill all enemies (debug)", KeyCategory.DEBUG),
]


def get_all_bindings() -> List[KeyBinding]:
    """Get all key bindings."""
    bindings = []
    bindings.extend(MOVEMENT_BINDINGS)
    bindings.extend(COMBAT_BINDINGS)
    bindings.extend(INTERACTION_BINDINGS)
    bindings.extend(UI_BINDINGS)
    return bindings


def get_bindings_by_category(category: KeyCategory) -> List[KeyBinding]:
    """Get bindings filtered by category."""
    all_bindings = get_all_bindings()
    return [b for b in all_bindings if b.category == category]


def get_binding_for_key(key: str) -> Optional[KeyBinding]:
    """Find a binding for a key."""
    all_bindings = get_all_bindings()
    for binding in all_bindings:
        if binding.key == key.lower():
            return binding
    return None


# Binding groups for UI display
BINDING_GROUPS = {
    "Movement": MOVEMENT_BINDINGS,
    "Combat": COMBAT_BINDINGS,
    "Interaction": INTERACTION_BINDINGS,
    "UI": UI_BINDINGS,
}
