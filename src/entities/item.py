"""Item entity."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto
from .entity import Entity, EntityType


class ItemType(Enum):
    """Item types."""
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    SCROLL = auto()
    RING = auto()
    AMMO = auto()
    TREASURE = auto()
    FOOD = auto()


class Rarity(Enum):
    """Item rarity tiers."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


class WeaponType(Enum):
    """Weapon types."""
    SIMPLE_MELEE = auto()
    MARTIAL_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_RANGED = auto()


class ArmorType(Enum):
    """Armor types."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()


@dataclass
class Item(Entity):
    """Item entity."""

    entity_type: EntityType = field(default=EntityType.ITEM, init=False)

    # Classification
    item_type: ItemType = ItemType.TREASURE
    rarity: Rarity = Rarity.COMMON

    # Physical
    weight: float = 0.0
    quantity: int = 1
    stackable: bool = False
    max_stack: int = 1

    # Magical
    attunement_required: bool = False
    attunement_slots: int = 0
    magical_bonus: int = 0
    charges: int = 0
    max_charges: int = 0

    # Description
    description: str = ""
    lore_text: Optional[str] = None

    # For weapons
    weapon_type: Optional[WeaponType] = None
    damage_die: str = "1d4"  # notation like "1d8"
    damage_type: Optional[str] = None
    properties: List[str] = field(default_factory=list)

    # For armor
    armor_type: Optional[ArmorType] = None
    base_ac: int = 10
    stealth_disadvantage: bool = False

    # For potions/scrolls
    spell_id: Optional[str] = None
    uses_remaining: int = 1

    def can_stack_with(self, other: "Item") -> bool:
        """Check if items can stack."""
        if not self.stackable or not other.stackable:
            return False
        if self.name != other.name:
            return False
        if self.item_type != other.item_type:
            return False
        return True

    def add(self, quantity: int) -> None:
        """Add to stack."""
        if not self.stackable:
            return
        self.quantity = min(self.quantity + quantity, self.max_stack)

    def remove(self, quantity: int) -> int:
        """Remove from stack, returns actual removed."""
        removed = min(quantity, self.quantity)
        self.quantity -= removed
        return removed

    @property
    def attack_bonus(self) -> int:
        """Attack bonus from magical item."""
        return self.magical_bonus

    @property
    def total_weight(self) -> float:
        """Total weight of stack."""
        return self.weight * self.quantity
