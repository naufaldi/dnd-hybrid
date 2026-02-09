"""Combat system for D&D Roguelike game.

Provides dice rolling, combat resolution, and initiative tracking.
"""

from .attack_result import AttackResult
from .combat_engine import CombatEngine
from .dice import DiceRoller
from .initiative import InitiativeTracker

__all__ = [
    "AttackResult",
    "CombatEngine",
    "DiceRoller",
    "InitiativeTracker",
]
