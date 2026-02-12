"""Registry of available game mechanics for validation and AI generation."""

from typing import Dict
from dataclasses import dataclass


@dataclass
class MechanicInfo:
    """Information about a game mechanic."""

    skill_check: str  # Primary ability used
    description: str
    available_actions: list[str] = None

    def __post_init__(self):
        if self.available_actions is None:
            self.available_actions = []


AVAILABLE_MECHANICS: Dict[str, MechanicInfo] = {
    "trap_mechanic": MechanicInfo(
        skill_check="dex",
        description="Detect and disarm traps",
        available_actions=["disarm_trap", "detect_trap", "avoid_trap"],
    ),
    "lockpick_mechanic": MechanicInfo(
        skill_check="dex",
        description="Pick locks",
        available_actions=["pick_lock", "break_lock", "find_key"],
    ),
    "persuasion_mechanic": MechanicInfo(
        skill_check="cha",
        description="Persuade NPCs",
        available_actions=["convince", "intimidate", "bribe", "barter"],
    ),
    "perception_mechanic": MechanicInfo(
        skill_check="wis",
        description="Notice hidden things",
        available_actions=["search", "spot_hidden", "listen"],
    ),
    "stealth_mechanic": MechanicInfo(
        skill_check="dex",
        description="Move silently",
        available_actions=["hide", "sneak", "ambush"],
    ),
    " Athletics_mechanic": MechanicInfo(
        skill_check="str",
        description="Physical challenges",
        available_actions=["climb", "swim", "jump", "break_door"],
    ),
    "survival_mechanic": MechanicInfo(
        skill_check="wis",
        description="Track and forage",
        available_actions=["track", "forage", "navigate"],
    ),
    "arcana_mechanic": MechanicInfo(
        skill_check="int",
        description="Magic knowledge",
        available_actions=["identify_magic", "dispel_magic", "recall_lore"],
    ),
    "medicine_mechanic": MechanicInfo(
        skill_check="wis",
        description="Heal and diagnose",
        available_actions=["heal", "diagnose", "stabilize"],
    ),
    "investigation_mechanic": MechanicInfo(
        skill_check="int",
        description="Find clues",
        available_actions=["search", "analyze", "deduce"],
    ),
}


def get_available_mechanic_names() -> list[str]:
    """Get list of all available mechanic names."""
    return list(AVAILABLE_MECHANICS.keys())


def get_mechanic_info(mechanic_name: str) -> MechanicInfo | None:
    """Get info about a specific mechanic."""
    return AVAILABLE_MECHANICS.get(mechanic_name)


def is_valid_mechanic(mechanic_name: str) -> bool:
    """Check if a mechanic name is valid."""
    return mechanic_name in AVAILABLE_MECHANICS
