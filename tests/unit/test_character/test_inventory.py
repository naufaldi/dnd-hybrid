"""Tests for inventory module."""

import pytest
from src.character.inventory import Inventory, EncumbranceState
from src.entities.item import Item, ItemType


class TestInventory:
    """Tests for Inventory class."""

    def test_default_inventory(self):
        inv = Inventory()
        assert len(inv.items) == 0
        assert inv.get_total_weight() == 0.0
        assert inv.gold == 0

    def test_add_item(self):
        inv = Inventory()
        item = Item(id="sword1", name="Sword", weight=3.0)
        inv.add_item(item)
        assert len(inv.items) == 1

    def test_remove_item(self):
        inv = Inventory()
        item = Item(id="sword1", name="Sword", weight=3.0)
        inv.add_item(item)
        removed = inv.remove_item("sword1")
        assert removed is not None
        assert removed.id == "sword1"
        assert len(inv.items) == 0

    def test_find_item(self):
        inv = Inventory()
        item = Item(id="potion1", name="Health Potion", weight=0.5)
        inv.add_item(item)
        found = inv.find_item("potion1")
        assert found is not None
        assert found.name == "Health Potion"

    def test_weight_tracking(self):
        inv = Inventory()
        item = Item(id="sword1", name="Sword", weight=5.0)
        inv.add_item(item)
        assert inv.get_total_weight() == 5.0

    def test_add_multiple_items(self):
        inv = Inventory()
        inv.add_item(Item(id="s1", name="Sword", weight=3.0))
        inv.add_item(Item(id="s2", name="Shield", weight=6.0))
        assert inv.get_total_weight() == 9.0

    def test_gold_tracking(self):
        inv = Inventory()
        inv.add_gold(100)
        assert inv.gold == 100
        inv.add_gold(50)
        assert inv.gold == 150
        inv.remove_gold(75)
        assert inv.gold == 75


class TestEncumbrance:
    """Tests for encumbrance levels."""

    def test_unencumbered(self):
        inv = Inventory(max_weight=100)
        item = Item(id="light", name="Light Item", weight=10.0)
        inv.add_item(item)
        # STR 10, unencumbered limit = 10 * 5 = 50
        assert inv.get_encumbrance_state(10) == EncumbranceState.UNENCUMBERED

    def test_capacity_calculation(self):
        inv = Inventory(strength=10)
        # STR 10, str_mod = 0, capacity = 75 + 0 = 75
        assert inv.get_capacity() == 75


class TestInventoryMethods:
    """Additional inventory method tests."""

    def test_clear_inventory(self):
        inv = Inventory()
        inv.add_item(Item(id="s1", name="Sword", weight=3.0))
        inv.clear()
        assert len(inv.items) == 0

    def test_len_inventory(self):
        inv = Inventory()
        inv.add_item(Item(id="s1", name="Sword", weight=3.0))
        inv.add_item(Item(id="s2", name="Shield", weight=6.0))
        assert len(inv) == 2

    def test_contains_item(self):
        inv = Inventory()
        item = Item(id="sword1", name="Sword", weight=3.0)
        inv.add_item(item)
        assert "sword1" in inv
        assert "nonexistent" not in inv
