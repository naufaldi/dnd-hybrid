"""Tests for Item class."""

import pytest
from src.entities.item import Item, ItemType, Rarity, WeaponType


class TestItem:
    def test_item_creation(self):
        item = Item(id="sword1", name="Longsword", item_type=ItemType.WEAPON)
        assert item.id == "sword1"
        assert item.alive is True

    def test_item_stackable(self):
        potion = Item(
            id="p1", name="Health Potion", item_type=ItemType.POTION,
            rarity=Rarity.COMMON, stackable=True, quantity=5, max_stack=99
        )
        assert potion.can_stack_with(potion)

    def test_stack_different_items(self):
        potion = Item(id="p1", name="Health Potion", item_type=ItemType.POTION, stackable=True)
        mana = Item(id="p2", name="Mana Potion", item_type=ItemType.POTION, stackable=True)
        assert not potion.can_stack_with(mana)

    def test_item_add_quantity(self):
        potion = Item(id="p1", name="Potion", stackable=True, quantity=5, max_stack=99)
        potion.add(3)
        assert potion.quantity == 8

    def test_item_remove_quantity(self):
        potion = Item(id="p1", name="Potion", stackable=True, quantity=5)
        removed = potion.remove(2)
        assert removed == 2
        assert potion.quantity == 3

    def test_non_stackable_cannot_add(self):
        sword = Item(id="s1", name="Sword", stackable=False, quantity=1)
        sword.add(5)  # Should not change
        assert sword.quantity == 1
