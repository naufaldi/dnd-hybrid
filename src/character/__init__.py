"""Character module for D&D Roguelike.

Provides attribute management, inventory, equipment, and leveling systems.
"""

from src.character.attributes import (
    AttributeSet,
    attribute_modifier,
    ability_score_increase_levels,
)
from src.character.inventory import (
    Inventory,
    EncumbranceState,
)
from src.character.equipment import (
    Equipment,
    EquipmentSlot,
)
from src.character.leveling import (
    LevelManager,
    level_from_xp,
    proficiency_bonus,
    xp_for_level,
    XP_THRESHOLDS,
)

__all__ = [
    # Attributes
    "AttributeSet",
    "attribute_modifier",
    "ability_score_increase_levels",
    # Inventory
    "Inventory",
    "EncumbranceState",
    # Equipment
    "Equipment",
    "EquipmentSlot",
    # Leveling
    "LevelManager",
    "level_from_xp",
    "proficiency_bonus",
    "xp_for_level",
    "XP_THRESHOLDS",
]
