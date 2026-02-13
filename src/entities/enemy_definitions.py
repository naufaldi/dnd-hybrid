"""Enemy definitions for narrative combat encounters.

This module provides enemy stats that can be used in scene YAML combat_encounter fields.
To add a new enemy: add definition here, then use combat_encounter: <name> in YAML.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Attack:
    """Enemy attack definition."""
    name: str
    damage: str  # e.g., "1d6+3"
    damage_type: str  # slashing, piercing, etc.
    attack_bonus: int = 0
    reach: Optional[str] = None  # for melee
    range_short: Optional[int] = None  # for ranged
    range_long: Optional[int] = None


@dataclass
class EnemyDefinition:
    """Enemy definition for narrative combat."""
    name: str
    hp: int
    ac: int
    challenge: str
    speed: int = 30
    abilities: List[str] = None
    attacks: List[Attack] = None
    description: str = ""

    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []
        if self.attacks is None:
            self.attacks = []


# Enemy definitions keyed by enemy type ID
ENEMY_DEFINITIONS: Dict[str, EnemyDefinition] = {
    "goblin": EnemyDefinition(
        name="Goblin",
        hp=7,
        ac=15,
        challenge="1/4",
        speed=30,
        abilities=["Nimble Escape"],
        attacks=[
            Attack(name="Scimitar", damage="1d6+3", damage_type="slashing", attack_bonus=4, reach="5 ft"),
            Attack(name="Shortbow", damage="1d6+3", damage_type="piercing", attack_bonus=4, range_short=80, range_long=320),
        ],
        description="A small, malicious humanoid with green skin and pointed ears.",
    ),
    "goblins": EnemyDefinition(  # Support plural form
        name="Goblin",
        hp=7,
        ac=15,
        challenge="1/4",
        speed=30,
        abilities=["Nimble Escape"],
        attacks=[
            Attack(name="Scimitar", damage="1d6+3", damage_type="slashing", attack_bonus=4, reach="5 ft"),
        ],
        description="A small, malicious humanoid with green skin and pointed ears.",
    ),
    "cultist": EnemyDefinition(
        name="Cultist",
        hp=9,
        ac=12,
        challenge="1/8",
        speed=30,
        abilities=["Dark Devotion"],
        attacks=[
            Attack(name="Scimitar", damage="1d6+2", damage_type="slashing", attack_bonus=4, reach="5 ft"),
        ],
        description="A hooded figure wearing dark robes, chanting obscure prayers.",
    ),
    "cultist_boss": EnemyDefinition(
        name="Cultist Leader",
        hp=22,
        ac=13,
        challenge="2",
        speed=30,
        abilities=["Dark Devotion", "Spellcasting"],
        attacks=[
            Attack(name="Dagger", damage="1d4+2", damage_type="piercing", attack_bonus=4, reach="5 ft"),
            Attack(name="Light Crossbow", damage="1d8+2", damage_type="piercing", attack_bonus=4, range_short=80, range_long=320),
        ],
        description="A powerful cultist leader wielding dark magic.",
    ),
    "guardian": EnemyDefinition(
        name="Stone Guardian",
        hp=33,
        ac=17,
        challenge="4",
        speed=30,
        abilities=["Immutable Form", "Magic Resistance"],
        attacks=[
            Attack(name="Slam", damage="2d10+5", damage_type="bludgeoning", attack_bonus=7, reach="10 ft"),
        ],
        description="A massive construct of animated stone, its eyes glowing with ethereal light.",
    ),
    "hobgoblin": EnemyDefinition(
        name="Hobgoblin",
        hp=11,
        ac=18,
        challenge="1/2",
        speed=30,
        abilities=["Martial Advantage"],
        attacks=[
            Attack(name="Longsword", damage="1d10+3", damage_type="slashing", attack_bonus=5, reach="5 ft"),
            Attack(name="Longbow", damage="1d8+3", damage_type="piercing", attack_bonus=5, range_short=150, range_long=600),
        ],
        description="A larger, more disciplined cousin of the goblin with orange-brown skin.",
    ),
    "bandit": EnemyDefinition(
        name="Bandit",
        hp=11,
        ac=12,
        challenge="1/8",
        speed=30,
        attacks=[
            Attack(name="Scimitar", damage="1d6+2", damage_type="slashing", attack_bonus=4, reach="5 ft"),
        ],
        description="A ragged outlaw looking for easy prey.",
    ),
    "bandit_captain": EnemyDefinition(
        name="Bandit Captain",
        hp=65,
        ac=15,
        challenge="2",
        speed=30,
        abilities=["Multiattack", "Pack Tactics"],
        attacks=[
            Attack(name="Flail", damage="1d8+3", damage_type="bludgeoning", attack_bonus=5, reach="5 ft"),
        ],
        description="A tough veteran leader of the bandit gang.",
    ),
    "ghost": EnemyDefinition(
        name="Specter",
        hp=22,
        ac=13,
        challenge="1",
        speed=0,  # Flying
        abilities=["Incorporeal Movement", "Undead Resilience", "Water Walk"],
        attacks=[
            Attack(name="Life Drain", damage="3d6+2", damage_type="necrotic", attack_bonus=5, reach="5 ft"),
        ],
        description="A translucent, ghostly apparition that floats silently.",
    ),
    "skeleton": EnemyDefinition(
        name="Skeleton",
        hp=13,
        ac=13,
        challenge="1/4",
        speed=30,
        abilities=["Undead Resilience"],
        attacks=[
            Attack(name="Shortsword", damage="1d6+2", damage_type="piercing", attack_bonus=4, reach="5 ft"),
            Attack(name="Shortbow", damage="1d6+2", damage_type="piercing", attack_bonus=4, range_short=80, range_long=320),
        ],
        description="Animated bones of a dead creature, rattling as it moves.",
    ),
    "zombie": EnemyDefinition(
        name="Zombie",
        hp=22,
        ac=8,
        challenge="1/4",
        speed=20,
        abilities=["Undead Resilience", "Toughness"],
        attacks=[
            Attack(name="Slam", damage="1d6+2", damage_type="bludgeoning", attack_bonus=3, reach="5 ft"),
        ],
        description="A shambling corpse with dead, vacant eyes.",
    ),
}


def get_enemy(enemy_type: str) -> Optional[EnemyDefinition]:
    """Get enemy definition by type.

    Args:
        enemy_type: The enemy type ID (e.g., "goblin", "cultist")

    Returns:
        EnemyDefinition or None if not found
    """
    return ENEMY_DEFINITIONS.get(enemy_type.lower())


def list_enemies() -> List[str]:
    """Get list of available enemy types."""
    return list(ENEMY_DEFINITIONS.keys())
