"""Equipment slot management and AC calculation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from src.entities.item import Item, ItemType, ArmorType


class EquipmentSlot(Enum):
    """Equipment slots."""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    NECK = "neck"
    RING1 = "ring1"
    RING2 = "ring2"


# Slot mappings for quick lookup
SLOT_ALIASES = {
    "main_hand": EquipmentSlot.MAIN_HAND,
    "off_hand": EquipmentSlot.OFF_HAND,
    "head": EquipmentSlot.HEAD,
    "chest": EquipmentSlot.CHEST,
    "legs": EquipmentSlot.LEGS,
    "feet": EquipmentSlot.FEET,
    "hands": EquipmentSlot.HANDS,
    "neck": EquipmentSlot.NECK,
    "ring1": EquipmentSlot.RING1,
    "ring2": EquipmentSlot.RING2,
    "ring": EquipmentSlot.RING1,  # Default ring to first slot
}


@dataclass
class Equipment:
    """
    Character equipment management.

    Manages equipped items, slot assignment, and AC calculation.
    """

    _slots: Dict[EquipmentSlot, Optional[Item]] = field(default_factory=lambda: {
        slot: None for slot in EquipmentSlot
    })

    def equip_item(self, item: Item, slot: str) -> bool:
        """
        Equip an item to a slot.

        Args:
            item: Item to equip
            slot: Slot name (e.g., "chest", "main_hand")

        Returns:
            True if successfully equipped

        Raises:
            ValueError: If slot is invalid
        """
        slot_enum = self._resolve_slot(slot)

        # Validate item can go in slot
        if not self._can_equip_in_slot(item, slot_enum):
            return False

        self._slots[slot_enum] = item
        return True

    def unequip_item(self, slot: str) -> Optional[Item]:
        """
        Unequip an item from a slot.

        Args:
            slot: Slot name

        Returns:
            The unequipped item, or None if slot was empty
        """
        slot_enum = self._resolve_slot(slot)
        item = self._slots[slot_enum]
        self._slots[slot_enum] = None
        return item

    def is_equipped(self, slot: str) -> bool:
        """
        Check if a slot has an item equipped.

        Args:
            slot: Slot name

        Returns:
            True if slot has an item
        """
        slot_enum = self._resolve_slot(slot)
        return self._slots[slot_enum] is not None

    def get_item(self, slot: str) -> Optional[Item]:
        """
        Get the item in a slot.

        Args:
            slot: Slot name

        Returns:
            The item, or None if slot is empty
        """
        slot_enum = self._resolve_slot(slot)
        return self._slots[slot_enum]

    def get_bonus(self, stat: str) -> int:
        """
        Get total bonus from all equipped items.

        Args:
            stat: Stat name (e.g., "ac", "attack", "damage")

        Returns:
            Total bonus from equipment
        """
        total = 0
        for item in self._slots.values():
            if item is not None:
                if stat == "ac":
                    total += item.magical_bonus
                elif stat in ("attack", "damage"):
                    total += item.magical_bonus
        return total

    def get_ac(self, dex_mod: int = 0) -> int:
        """
        Calculate armor class based on equipped items.

        AC calculation rules:
        - Unarmored: 10 + dex_mod
        - Light armor: base AC + dex_mod
        - Medium armor: base AC + dex_mod (max +2)
        - Heavy armor: base AC (no dex)
        - Shields: +2

        Args:
            dex_mod: Dexterity modifier

        Returns:
            Total armor class
        """
        chest = self._slots.get(EquipmentSlot.CHEST)
        off_hand = self._slots.get(EquipmentSlot.OFF_HAND)

        base_ac = 10  # Unarmored default

        if chest and chest.item_type == ItemType.ARMOR:
            armor_type = chest.armor_type
            armor_bonus = chest.magical_bonus

            if armor_type == ArmorType.LIGHT:
                # Light: base + dex + magic
                base_ac = chest.base_ac + dex_mod + armor_bonus
            elif armor_type == ArmorType.MEDIUM:
                # Medium: base + dex (max +2) + magic
                dex_bonus = min(dex_mod, 2)
                base_ac = chest.base_ac + dex_bonus + armor_bonus
            elif armor_type == ArmorType.HEAVY:
                # Heavy: base only (no dex) + magic
                base_ac = chest.base_ac + armor_bonus

        # Shield bonus
        if off_hand and off_hand.item_type == ItemType.ARMOR:
            if off_hand.armor_type == ArmorType.SHIELD:
                base_ac += off_hand.base_ac + off_hand.magical_bonus

        return base_ac

    def get_equipped_items(self) -> List[Item]:
        """
        Get all equipped items.

        Returns:
            List of equipped items
        """
        return [item for item in self._slots.values() if item is not None]

    def get_total_weight(self) -> float:
        """Get total weight of equipped items."""
        return sum(item.weight for item in self._slots.values() if item is not None)

    def _resolve_slot(self, slot: str) -> EquipmentSlot:
        """Resolve slot name to EquipmentSlot enum."""
        slot_lower = slot.lower()
        if slot_lower not in SLOT_ALIASES:
            raise ValueError(f"Invalid slot: {slot}")
        return SLOT_ALIASES[slot_lower]

    def _can_equip_in_slot(self, item: Item, slot: EquipmentSlot) -> bool:
        """Check if item can be equipped in slot."""
        # Weapons can go in main_hand or off_hand
        if item.item_type == ItemType.WEAPON:
            return slot in (EquipmentSlot.MAIN_HAND, EquipmentSlot.OFF_HAND)

        # Armor goes in appropriate slots
        if item.item_type == ItemType.ARMOR:
            armor_type = item.armor_type
            if armor_type == ArmorType.SHIELD:
                return slot == EquipmentSlot.OFF_HAND
            elif armor_type in (ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.HEAVY):
                return slot == EquipmentSlot.CHEST

        # Rings go in ring slots
        if item.item_type == ItemType.RING:
            return slot in (EquipmentSlot.RING1, EquipmentSlot.RING2)

        # Other items - check slot name matches item properties
        # This is simplified; real implementation would check item.slot
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = {}
        for slot, item in self._slots.items():
            if item is not None:
                result[slot.value] = item.id
        return result
