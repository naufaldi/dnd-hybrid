"""Tests for equipment module."""

import pytest
from src.character.equipment import Equipment, EquipmentSlot
from src.entities.item import Item, ItemType, ArmorType


class TestEquipment:
    """Tests for Equipment class."""

    def test_default_equipment(self):
        equip = Equipment()
        assert equip.get_item("main_hand") is None
        assert equip.get_item("chest") is None

    def test_equip_item(self):
        equip = Equipment()
        sword = Item(
            id="sword1", name="Longsword",
            item_type=ItemType.WEAPON
        )
        result = equip.equip_item(sword, "main_hand")
        assert result is True
        assert equip.get_item("main_hand") is not None
        assert equip.get_item("main_hand").id == "sword1"

    def test_unequip_item(self):
        equip = Equipment()
        sword = Item(id="sword1", name="Longsword", item_type=ItemType.WEAPON)
        equip.equip_item(sword, "main_hand")
        unequipped = equip.unequip_item("main_hand")
        assert unequipped is not None
        assert equip.get_item("main_hand") is None

    def test_is_equipped(self):
        equip = Equipment()
        armor = Item(id="leather", name="Leather Armor", item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT, base_ac=11)
        equip.equip_item(armor, "chest")
        assert equip.is_equipped("chest") is True
        assert equip.is_equipped("main_hand") is False

    def test_ac_calculation_unarmored(self):
        equip = Equipment()
        # No armor equipped, AC = 10 + dex_mod (0)
        assert equip.get_ac(0) == 10

    def test_ac_calculation_light_armor(self):
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR,
            armor_type=ArmorType.LIGHT,
            base_ac=11
        )
        equip.equip_item(armor, "chest")
        # Light armor: 11 + dex_mod
        assert equip.get_ac(0) == 11  # dex_mod = 0
        assert equip.get_ac(5) == 16  # dex_mod = 5

    def test_ac_calculation_medium_armor(self):
        equip = Equipment()
        armor = Item(
            id="chain", name="Chainmail",
            item_type=ItemType.ARMOR,
            armor_type=ArmorType.MEDIUM,
            base_ac=16
        )
        equip.equip_item(armor, "chest")
        # Medium armor: base + dex_mod (max +2)
        assert equip.get_ac(5) == 18  # 16 + 2 (capped)
        assert equip.get_ac(0) == 16  # 16 + 0

    def test_ac_calculation_heavy_armor(self):
        equip = Equipment()
        armor = Item(
            id="plate", name="Plate Armor",
            item_type=ItemType.ARMOR,
            armor_type=ArmorType.HEAVY,
            base_ac=18
        )
        equip.equip_item(armor, "chest")
        # Heavy armor: base only (no dex)
        assert equip.get_ac(10) == 18  # dex ignored

    def test_shield_bonus(self):
        equip = Equipment()
        shield = Item(
            id="shield", name="Shield",
            item_type=ItemType.ARMOR,
            armor_type=ArmorType.SHIELD,
            base_ac=2
        )
        equip.equip_item(shield, "off_hand")
        # Shield adds +2 to AC
        assert equip.get_ac(0) == 12  # 10 + 2 shield


class TestEquipmentSlot:
    """Tests for EquipmentSlot enum."""

    def test_valid_slots(self):
        slots = [s.value for s in EquipmentSlot]
        assert "main_hand" in slots
        assert "chest" in slots
        assert "ring1" in slots
