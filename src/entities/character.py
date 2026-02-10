"""Character entity."""

from dataclasses import dataclass, field
from typing import List, Dict
from .entity import Entity, EntityType


# XP thresholds for levels 1-20
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]


def attribute_modifier(score: int) -> int:
    """Calculate attribute modifier from score."""
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus from level."""
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6


def level_from_xp(experience: int) -> int:
    """Calculate level from XP."""
    for i, threshold in enumerate(XP_THRESHOLDS):
        if experience < threshold:
            return i
    return 20


@dataclass
class Character(Entity):
    """Player character."""

    entity_type: EntityType = field(default=EntityType.PLAYER, init=False)

    # Core
    level: int = 1
    experience: int = 0
    character_class: str = "fighter"
    race: str = "human"
    background: str = "soldier"

    # Attributes (6-20)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Derived (use properties)
    hit_points: int = 10
    temporary_hp: int = 0
    exhaustion_level: int = 0
    class_resources: Dict[str, int] = field(default_factory=dict)

    # State
    conditions: List = field(default_factory=list)
    death_save_successes: int = 0
    death_save_failures: int = 0

    # History
    damage_dealt: int = 0
    damage_taken: int = 0
    turns_survived: int = 0
    kills: Dict[str, int] = field(default_factory=dict)

    # Position
    current_floor: int = 1

    # Combat properties (for CombatEngine)
    magical_bonus: int = 0

    # Weapon damage dice by class
    CLASS_DAMAGE_DIE = {
        "fighter": "1d10",
        "wizard": "1d6",
        "rogue": "1d8",
        "cleric": "1d8",
        "paladin": "1d10",
        "ranger": "1d8",
        "barbarian": "1d12",
        "monk": "1d8",
        "bard": "1d8",
        "druid": "1d8",
        "sorcerer": "1d6",
        "warlock": "1d10",
    }

    @property
    def strength_mod(self) -> int:
        return attribute_modifier(self.strength)

    @property
    def dexterity_mod(self) -> int:
        return attribute_modifier(self.dexterity)

    @property
    def constitution_mod(self) -> int:
        return attribute_modifier(self.constitution)

    @property
    def intelligence_mod(self) -> int:
        return attribute_modifier(self.intelligence)

    @property
    def wisdom_mod(self) -> int:
        return attribute_modifier(self.wisdom)

    @property
    def charisma_mod(self) -> int:
        return attribute_modifier(self.charisma)

    @property
    def armor_class(self) -> int:
        """AC = 10 + dex modifier."""
        return 10 + self.dexterity_mod

    @property
    def max_hp(self) -> int:
        """Max HP (simplified - real implementation uses class)."""
        return 10 + (self.level - 1) * (5 + self.constitution_mod)

    @property
    def proficiency_bonus(self) -> int:
        return proficiency_bonus(self.level)

    @property
    def current_hp(self) -> int:
        return self.hit_points

    @property
    def is_dying(self) -> bool:
        """Character is at 0 HP and alive."""
        return self.hit_points <= 0 and self.alive

    @property
    def attack_bonus(self) -> int:
        """Attack bonus = proficiency bonus + strength modifier."""
        return self.proficiency_bonus + self.strength_mod

    @property
    def damage_die(self) -> str:
        """Base damage die based on class."""
        return self.CLASS_DAMAGE_DIE.get(self.character_class, "1d8")

    @property
    def damage_modifier(self) -> int:
        """Damage modifier (strength modifier for melee)."""
        return self.strength_mod

    def take_damage(self, damage: int) -> int:
        """Take damage, returns actual damage taken."""
        if self.temporary_hp > 0:
            temp_used = min(self.temporary_hp, damage)
            self.temporary_hp -= temp_used
            damage -= temp_used
        self.hit_points = max(0, self.hit_points - damage)
        self.damage_taken += damage
        if self.hit_points == 0:
            self.alive = False
        return damage

    def heal(self, amount: int) -> int:
        """Heal, returns actual healing."""
        old_hp = self.hit_points
        self.hit_points = min(self.max_hp, self.hit_points + amount)
        return self.hit_points - old_hp

    def add_experience(self, xp: int) -> None:
        """Add XP and handle level ups."""
        self.experience += xp
        new_level = level_from_xp(self.experience)
        while self.level < new_level:
            self.level_up()

    def level_up(self) -> None:
        """Level up the character."""
        self.level += 1
        # HP increase
        hp_gain = 5 + self.constitution_mod  # Simplified
        self.hit_points = min(self.max_hp, self.hit_points + hp_gain)
