"""Tests for character module."""

import pytest

from src.character.attributes import AttributeSet
from src.character.inventory import Inventory, EncumbranceState
from src.character.equipment import Equipment
from src.character.leveling import LevelManager
from src.entities.item import Item, ItemType, ArmorType


class TestAttributeSet:
    """Tests for AttributeSet class."""

    def test_attribute_set_creation(self):
        """Test creating an AttributeSet with defaults."""
        attrs = AttributeSet()
        assert attrs.strength == 10
        assert attrs.dexterity == 10
        assert attrs.constitution == 10
        assert attrs.intelligence == 10
        assert attrs.wisdom == 10
        assert attrs.charisma == 10

    def test_attribute_set_custom_values(self):
        """Test creating an AttributeSet with custom values."""
        attrs = AttributeSet(
            strength=16, dexterity=14, constitution=15,
            intelligence=12, wisdom=10, charisma=8
        )
        assert attrs.strength == 16
        assert attrs.dexterity == 14

    def test_modifier_calculation(self):
        """Test modifier calculation."""
        attrs = AttributeSet(strength=16)
        assert attrs.str_mod == 3

        attrs = AttributeSet(strength=10)
        assert attrs.str_mod == 0

        attrs = AttributeSet(strength=8)
        assert attrs.str_mod == -1

        attrs = AttributeSet(strength=20)
        assert attrs.str_mod == 5

        attrs = AttributeSet(strength=1)
        assert attrs.str_mod == -5

    def test_all_modifier_properties(self):
        """Test all modifier properties."""
        attrs = AttributeSet(
            strength=16, dexterity=14, constitution=15,
            intelligence=12, wisdom=10, charisma=8
        )
        assert attrs.str_mod == 3
        assert attrs.dex_mod == 2
        assert attrs.con_mod == 2
        assert attrs.int_mod == 1
        assert attrs.wis_mod == 0
        assert attrs.cha_mod == -1

    def test_ability_check_without_proficiency(self):
        """Test ability check without proficiency."""
        attrs = AttributeSet(strength=16)
        result = attrs.ability_check("strength", proficient=False)
        # Should be d20 + modifier (3), so range 4-23
        assert 4 <= result <= 23

    def test_ability_check_with_proficiency(self):
        """Test ability check with proficiency."""
        attrs = AttributeSet(strength=16)
        result = attrs.ability_check("strength", proficient=True, proficiency_bonus=2)
        # Should be d20 + modifier (3) + proficiency (2), so range 6-25
        assert 6 <= result <= 25

    def test_increase_attribute(self):
        """Test increasing an attribute."""
        attrs = AttributeSet(strength=10)
        attrs.increase_attribute("strength", 2)
        assert attrs.strength == 12
        assert attrs.str_mod == 1

    def test_increase_attribute_cap_at_30(self):
        """Test that attributes cap at 30."""
        attrs = AttributeSet(strength=28)
        attrs.increase_attribute("strength", 5)
        assert attrs.strength == 30

    def test_invalid_attribute_name(self):
        """Test that invalid attribute names raise ValueError."""
        attrs = AttributeSet()
        with pytest.raises(ValueError):
            attrs.increase_attribute("invalid", 2)


class TestInventory:
    """Tests for Inventory class."""

    def test_inventory_creation(self):
        """Test creating an inventory."""
        inv = Inventory(max_weight=100)
        assert inv.max_weight == 100
        assert len(inv.items) == 0
        assert inv.gold == 0

    def test_add_item(self):
        """Test adding an item."""
        inv = Inventory(max_weight=50)
        item = Item(id="sword", name="Sword", weight=3.0)
        inv.add_item(item)
        assert len(inv.items) == 1
        assert inv.items[0] is item

    def test_remove_item(self):
        """Test removing an item."""
        inv = Inventory(max_weight=50)
        item = Item(id="sword", name="Sword", weight=3.0)
        inv.add_item(item)
        removed = inv.remove_item("sword")
        assert removed is item
        assert len(inv.items) == 0

    def test_find_item(self):
        """Test finding an item by id."""
        inv = Inventory(max_weight=50)
        item = Item(id="sword", name="Sword", weight=3.0)
        inv.add_item(item)
        found = inv.find_item("sword")
        assert found is item

    def test_find_item_not_found(self):
        """Test finding non-existent item."""
        inv = Inventory(max_weight=50)
        found = inv.find_item("nonexistent")
        assert found is None

    def test_weight_tracking(self):
        """Test weight tracking."""
        inv = Inventory(max_weight=50)
        item = Item(id="sword", name="Sword", weight=5.0)
        inv.add_item(item)
        assert inv.get_total_weight() == 5.0

    def test_weight_tracking_with_quantity(self):
        """Test weight tracking with stacked items."""
        inv = Inventory(max_weight=50)
        item = Item(id="arrow", name="Arrow", weight=0.05, quantity=20, stackable=True, max_stack=100)
        inv.add_item(item)
        assert inv.get_total_weight() == 1.0  # 0.05 * 20

    def test_stackable_items_combine(self):
        """Test that stackable items combine."""
        inv = Inventory(max_weight=50)
        item1 = Item(id="arrow", name="Arrow", weight=0.05, quantity=10, stackable=True, max_stack=100)
        item2 = Item(id="arrow", name="Arrow", weight=0.05, quantity=5, stackable=True, max_stack=100)
        inv.add_item(item1)
        inv.add_item(item2)
        assert len(inv.items) == 1
        assert inv.items[0].quantity == 15

    def test_gold_tracking(self):
        """Test gold tracking."""
        inv = Inventory(max_weight=100)
        inv.add_gold(100)
        assert inv.gold == 100
        inv.add_gold(50)
        assert inv.gold == 150
        inv.remove_gold(75)
        assert inv.gold == 75

    def test_encumbrance_unencumbered(self):
        """Test unencumbered state."""
        inv = Inventory(max_weight=100)
        inv.add_item(Item(id="sword", name="Sword", weight=5.0))
        # With STR 10, unencumbered threshold is 50
        assert inv.get_encumbrance_state(10) == EncumbranceState.UNENCUMBERED

    def test_encumbrance_encumbered(self):
        """Test encumbered state."""
        inv = Inventory(max_weight=100)
        inv.add_item(Item(id="sword", name="Sword", weight=55.0))
        # With STR 10, encumbered threshold is 50-100
        assert inv.get_encumbrance_state(10) == EncumbranceState.ENCUMBERED

    def test_encumbrance_heavily_encumbered(self):
        """Test heavily encumbered state."""
        inv = Inventory(max_weight=200)
        inv.add_item(Item(id="sword", name="Sword", weight=120.0))
        # With STR 10, heavily encumbered threshold is 100-150
        assert inv.get_encumbrance_state(10) == EncumbranceState.HEAVILY_ENCUMBERED

    def test_encumbrance_over_limit(self):
        """Test over limit state."""
        inv = Inventory(max_weight=200)
        inv.add_item(Item(id="sword", name="Sword", weight=160.0))
        # With STR 10, over 150 is unable to move
        assert inv.get_encumbrance_state(10) == EncumbranceState.OVER_LIMIT

    def test_capacity_calculation(self):
        """Test capacity calculation."""
        # Base 75 + 15 * STR modifier
        # STR 10 = 0 mod, so 75 capacity
        inv = Inventory(strength=10)
        assert inv.get_capacity() == 75

        # STR 16 = +3 mod, so 75 + 45 = 120
        inv = Inventory(strength=16)
        assert inv.get_capacity() == 120

        # STR 8 = -1 mod, minimum 75
        inv = Inventory(strength=8)
        assert inv.get_capacity() == 75


class TestEquipment:
    """Tests for Equipment class."""

    def test_equipment_creation(self):
        """Test creating equipment."""
        equip = Equipment()
        assert equip.is_equipped("chest") is False
        assert equip.is_equipped("main_hand") is False

    def test_equip_item(self):
        """Test equipping an item."""
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT,
            base_ac=11, weight=10.0
        )
        equip.equip_item(armor, "chest")
        assert equip.is_equipped("chest")

    def test_unequip_item(self):
        """Test unequipping an item."""
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT,
            base_ac=11, weight=10.0
        )
        equip.equip_item(armor, "chest")
        unequipped = equip.unequip_item("chest")
        assert unequipped is armor
        assert equip.is_equipped("chest") is False

    def test_get_bonus(self):
        """Test getting bonuses from equipment."""
        equip = Equipment()
        ring = Item(
            id="ring", name="Ring of Protection",
            weight=0.5, magical_bonus=2
        )
        equip.equip_item(ring, "ring1")
        assert equip.get_bonus("ac") == 2

    def test_ac_calculation_unarmored(self):
        """Test AC calculation with no armor."""
        equip = Equipment()
        # Unarmored AC = 10 + dex_mod (assume 10 = 0)
        ac = equip.get_ac(dex_mod=0)
        assert ac == 10

    def test_ac_calculation_light_armor(self):
        """Test AC calculation with light armor."""
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT,
            base_ac=11, weight=10.0
        )
        equip.equip_item(armor, "chest")
        # Light armor AC = base + dex_mod
        ac = equip.get_ac(dex_mod=2)
        assert ac == 13  # 11 + 2

    def test_ac_calculation_medium_armor(self):
        """Test AC calculation with medium armor."""
        equip = Equipment()
        armor = Item(
            id="scale", name="Scale Mail",
            item_type=ItemType.ARMOR, armor_type=ArmorType.MEDIUM,
            base_ac=14, weight=10.0
        )
        equip.equip_item(armor, "chest")
        # Medium armor AC = base + dex_mod (max +2)
        ac = equip.get_ac(dex_mod=3)
        assert ac == 16  # 14 + 2 (capped)

    def test_ac_calculation_heavy_armor(self):
        """Test AC calculation with heavy armor."""
        equip = Equipment()
        armor = Item(
            id="plate", name="Plate Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.HEAVY,
            base_ac=18, weight=10.0
        )
        equip.equip_item(armor, "chest")
        # Heavy armor AC = base (no dex bonus)
        ac = equip.get_ac(dex_mod=5)
        assert ac == 18  # No dex added

    def test_ac_calculation_with_shield(self):
        """Test AC calculation with shield."""
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT,
            base_ac=11, weight=10.0
        )
        shield = Item(
            id="shield", name="Shield",
            item_type=ItemType.ARMOR, armor_type=ArmorType.SHIELD,
            base_ac=2, weight=10.0
        )
        equip.equip_item(armor, "chest")
        equip.equip_item(shield, "off_hand")
        # AC = armor (11) + shield (2) + dex (0)
        ac = equip.get_ac(dex_mod=0)
        assert ac == 13

    def test_get_equipped_items(self):
        """Test getting all equipped items."""
        equip = Equipment()
        armor = Item(
            id="leather", name="Leather Armor",
            item_type=ItemType.ARMOR, armor_type=ArmorType.LIGHT,
            base_ac=11, weight=10.0
        )
        shield = Item(
            id="shield", name="Shield",
            item_type=ItemType.ARMOR, armor_type=ArmorType.SHIELD,
            base_ac=2, weight=10.0
        )
        equip.equip_item(armor, "chest")
        equip.equip_item(shield, "off_hand")
        items = equip.get_equipped_items()
        assert len(items) == 2


class TestLevelManager:
    """Tests for LevelManager class."""

    def test_level_manager_creation(self):
        """Test creating a LevelManager."""
        lm = LevelManager()
        assert lm.get_level() == 1
        assert lm.get_xp() == 0

    def test_level_from_xp(self):
        """Test calculating level from XP."""
        lm = LevelManager()
        assert lm.get_level() == 1

        lm.add_xp(300)  # Level 2 threshold
        assert lm.get_level() == 2

        lm.add_xp(600)  # Total 900, level 3
        assert lm.get_level() == 3

    def test_xp_accumulation(self):
        """Test XP accumulation."""
        lm = LevelManager()
        lm.add_xp(100)
        assert lm.get_xp() == 100
        lm.add_xp(200)
        assert lm.get_xp() == 300

    def test_proficiency_bonus_level_1_to_4(self):
        """Test proficiency bonus for levels 1-4."""
        lm = LevelManager()
        assert lm.get_proficiency_bonus() == 2

        lm.add_xp(299)  # Still level 1
        assert lm.get_proficiency_bonus() == 2

    def test_proficiency_bonus_level_5_to_8(self):
        """Test proficiency bonus for levels 5-8."""
        lm = LevelManager()
        lm.add_xp(900)  # Level 2
        assert lm.get_proficiency_bonus() == 2

        lm.add_xp(1800)  # Level 3
        assert lm.get_proficiency_bonus() == 2

        lm.add_xp(6300)  # Level 5
        assert lm.get_proficiency_bonus() == 3

    def test_proficiency_bonus_levels_9_plus(self):
        """Test proficiency bonus for higher levels."""
        lm = LevelManager()
        lm.add_xp(14000)  # Level 6
        assert lm.get_proficiency_bonus() == 3

        lm.add_xp(21000)  # Total 35000, still level 8
        assert lm.get_proficiency_bonus() == 3

        lm.add_xp(13000)  # Total 48000, now level 9
        assert lm.get_proficiency_bonus() == 4

    def test_check_level_up(self):
        """Test level up check."""
        lm = LevelManager()
        assert lm.check_level_up() is False

        lm.add_xp(10000)  # Jump to level 5
        assert lm.check_level_up() is True

    def test_level_cap_at_20(self):
        """Test that level caps at 20."""
        lm = LevelManager()
        lm.add_xp(1000000)  # Way past level 20
        assert lm.get_level() == 20

    def test_starting_level(self):
        """Test starting at a specific level."""
        lm = LevelManager(starting_level=5)
        assert lm.get_level() == 5
        assert lm.get_proficiency_bonus() == 3
