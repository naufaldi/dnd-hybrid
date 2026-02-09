"""Combat system for D&D Roguelike game.

Provides dice rolling, combat resolution, initiative tracking, and status effects.
"""

from .attack_result import AttackResult
from .combat_engine import CombatEngine
from .dice import DiceRoller
from .initiative import InitiativeTracker
from .status_effects import Condition, StatusEffect, StatusEffectManager

__all__ = [
    "AttackResult",
    "CombatEngine",
    "Condition",
    "DiceRoller",
    "InitiativeTracker",
    "StatusEffect",
    "StatusEffectManager",
]
