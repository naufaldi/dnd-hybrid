"""Attack result dataclass for combat outcomes."""
from dataclasses import dataclass


@dataclass
class AttackResult:
    """Result of an attack roll in combat.

    Attributes:
        hit: True if the attack successfully hit the defender
        critical: True if the attack was a critical hit (natural 20)
        damage: Total damage dealt (0 if the attack missed)
        rolled: The raw d20 roll value
        total: The total attack roll (d20 + bonuses)
    """

    hit: bool
    critical: bool
    damage: int
    rolled: int
    total: int
