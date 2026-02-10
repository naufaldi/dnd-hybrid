"""Enemy entity."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum, auto
from .entity import Entity, EntityType


class AIType(Enum):
    """Enemy AI behavior types."""
    PASSIVE = auto()
    AGGRESSIVE = auto()
    DEFENSIVE = auto()
    PATROL = auto()


class EnemyType(Enum):
    """Enemy types."""
    BEAST = auto()
    UNDEAD = auto()
    ABERRATION = auto()
    CONSTRUCT = auto()
    DRAGON = auto()
    ELEMENTAL = auto()
    FEY = auto()
    FIEND = auto()
    GIANT = auto()
    HUMANOID = auto()
    MONSTROSITY = auto()
    OOZE = auto()
    PLANT = auto()


@dataclass
class Enemy(Entity):
    """Enemy entity."""

    entity_type: EntityType = field(default=EntityType.ENEMY, init=False)

    # Classification
    enemy_type: EnemyType = EnemyType.HUMANOID
    cr: float = 1.0  # Challenge rating

    # Stats
    armor_class: int = 10
    max_hp: int = 10
    current_hp: int = 10
    attack_bonus: int = 2
    damage_per_round: int = 5

    # Attributes
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Behavior
    ai_type: AIType = AIType.AGGRESSIVE
    aggro_range: int = 5
    patrol_route: Optional[List[Tuple[int, int]]] = None
    abilities: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    immunities: List[str] = field(default_factory=list)

    # State
    status_effects: List = field(default_factory=list)

    # Combat properties (for CombatEngine)
    magical_bonus: int = 0
    damage_die: str = "1d8"  # Default damage die

    @property
    def strength_mod(self) -> int:
        return (self.strength - 10) // 2

    @property
    def dexterity_mod(self) -> int:
        return (self.dexterity - 10) // 2

    @property
    def damage_modifier(self) -> int:
        """Damage modifier (strength modifier for melee)."""
        return self.strength_mod

    def take_damage(self, damage: int) -> int:
        """Take damage."""
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp == 0:
            self.alive = False
        return damage

    def heal(self, amount: int) -> int:
        """Heal."""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def can_see(self, target_pos: Tuple[int, int], map_fov: set) -> bool:
        """Check if enemy can see target position."""
        return target_pos in map_fov

    def is_in_aggro_range(self, target_pos: Tuple[int, int]) -> bool:
        """Check if target is within aggro range."""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        return (dx * dx + dy * dy) ** 0.5 <= self.aggro_range
