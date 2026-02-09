"""Item storage, weight limits, and stacking."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from src.entities.item import Item


class EncumbranceState(Enum):
    """Encumbrance states based on weight carried."""
    UNENCUMBERED = "unencumbered"
    ENCUMBERED = "encumbered"
    HEAVILY_ENCUMBERED = "heavily_encumbered"
    OVER_LIMIT = "over_limit"


@dataclass
class Inventory:
    """
    Character inventory with weight tracking and capacity.

    Attributes:
        items: List of items in inventory
        gold: Current gold amount
        max_weight: Maximum weight that can be carried
        strength: Strength score for encumbrance calculations
    """

    max_weight: float = 100.0
    strength: int = 10
    gold: int = 0
    items: List[Item] = field(default_factory=list)

    def add_item(self, item: Item) -> bool:
        """
        Add an item to the inventory.

        Args:
            item: Item to add

        Returns:
            True if item was added, False if over capacity
        """
        # Check if stackable item can be combined
        if item.stackable:
            for existing in self.items:
                if existing.can_stack_with(item):
                    existing.add(item.quantity)
                    return True

        # Check weight capacity
        new_weight = self.get_total_weight() + item.total_weight
        if new_weight > self.max_weight:
            return False

        self.items.append(item)
        return True

    def remove_item(self, item_id: str) -> Optional[Item]:
        """
        Remove an item from the inventory by ID.

        Args:
            item_id: ID of the item to remove

        Returns:
            The removed item, or None if not found
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                return self.items.pop(i)
        return None

    def find_item(self, item_id: str) -> Optional[Item]:
        """
        Find an item by ID.

        Args:
            item_id: ID of the item to find

        Returns:
            The item, or None if not found
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_total_weight(self) -> float:
        """
        Calculate total weight of all items.

        Returns:
            Total weight including item quantities
        """
        return sum(item.total_weight for item in self.items)

    def add_gold(self, amount: int) -> None:
        """
        Add gold to inventory.

        Args:
            amount: Amount of gold to add
        """
        self.gold = max(0, self.gold + amount)

    def remove_gold(self, amount: int) -> int:
        """
        Remove gold from inventory.

        Args:
            amount: Amount of gold to remove

        Returns:
            Actual amount removed
        """
        removed = min(amount, self.gold)
        self.gold -= removed
        return removed

    def get_encumbrance_threshold(self, threshold_type: str) -> float:
        """
        Get encumbrance threshold based on strength.

        Args:
            threshold_type: "unencumbered", "encumbered", or "heavily"

        Returns:
            Weight threshold in pounds
        """
        base = self.strength * 5

        if threshold_type == "unencumbered":
            return base
        elif threshold_type == "encumbered":
            return base * 2  # 10 * STR
        elif threshold_type == "heavily":
            return base * 3  # 15 * STR
        return float('inf')

    def get_encumbrance_state(self, strength: int) -> EncumbranceState:
        """
        Determine encumbrance state based on weight and strength.

        Args:
            strength: Character's strength score

        Returns:
            EncumbranceState
        """
        weight = self.get_total_weight()
        base = strength * 5

        unencumbered_limit = base  # 5 * STR
        encumbered_limit = base * 2  # 10 * STR
        heavily_limit = base * 3  # 15 * STR

        if weight >= heavily_limit:
            return EncumbranceState.OVER_LIMIT
        elif weight >= encumbered_limit:
            return EncumbranceState.HEAVILY_ENCUMBERED
        elif weight >= unencumbered_limit:
            return EncumbranceState.ENCUMBERED
        else:
            return EncumbranceState.UNENCUMBERED

    def get_speed_reduction(self, strength: int) -> int:
        """
        Calculate speed reduction from encumbrance.

        Args:
            strength: Character's strength score

        Returns:
            Speed reduction in feet
        """
        state = self.get_encumbrance_state(strength)
        if state == EncumbranceState.ENCUMBERED:
            return 10
        elif state == EncumbranceState.HEAVILY_ENCUMBERED:
            return 20
        elif state == EncumbranceState.OVER_LIMIT:
            return 100  # Can't move
        return 0

    def get_capacity(self) -> float:
        """
        Calculate inventory capacity.

        Base capacity: 75 + 15 * STR modifier (minimum 75)

        Returns:
            Maximum weight capacity
        """
        str_mod = (self.strength - 10) // 2
        capacity = 75 + (str_mod * 15)
        return max(75, capacity)

    def is_encumbered(self, strength: int) -> bool:
        """Check if character is encumbered."""
        state = self.get_encumbrance_state(strength)
        return state in (EncumbranceState.ENCUMBERED,
                        EncumbranceState.HEAVILY_ENCUMBERED,
                        EncumbranceState.OVER_LIMIT)

    def is_over_limit(self, strength: int) -> bool:
        """Check if character is over encumbrance limit."""
        return self.get_encumbrance_state(strength) == EncumbranceState.OVER_LIMIT

    def clear(self) -> None:
        """Remove all items from inventory."""
        self.items.clear()

    def get_items_by_type(self, item_type) -> List[Item]:
        """Get all items of a specific type."""
        return [item for item in self.items if item.item_type == item_type]

    def __len__(self) -> int:
        """Return number of items in inventory."""
        return len(self.items)

    def __contains__(self, item_id: str) -> bool:
        """Check if item exists in inventory."""
        return any(item.id == item_id for item in self.items)
