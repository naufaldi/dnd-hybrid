"""Tests for Character class."""

import pytest
from src.entities.character import (
    Character, attribute_modifier, proficiency_bonus, level_from_xp
)


class TestAttributeModifier:
    def test_modifier_table(self):
        assert attribute_modifier(1) == -5
        assert attribute_modifier(8) == -1
        assert attribute_modifier(10) == 0
        assert attribute_modifier(12) == 1
        assert attribute_modifier(16) == 3
        assert attribute_modifier(20) == 5


class TestProficiencyBonus:
    def test_levels_1_to_4(self):
        assert proficiency_bonus(1) == 2
        assert proficiency_bonus(4) == 2

    def test_levels_5_to_8(self):
        assert proficiency_bonus(5) == 3
        assert proficiency_bonus(8) == 3

    def test_levels_9_to_12(self):
        assert proficiency_bonus(9) == 4
        assert proficiency_bonus(12) == 4


class TestCharacter:
    def test_character_creation(self):
        char = Character(
            id="test", name="TestChar",
            character_class="fighter", race="human",
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=12, charisma=8
        )
        assert char.id == "test"
        assert char.alive is True

    def test_derived_stats(self):
        char = Character(
            id="test", name="Test", character_class="fighter", race="human",
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=12, charisma=8
        )
        assert char.strength_mod == 3
        assert char.dexterity_mod == 2
        assert char.armor_class == 12  # 10 + dex

    def test_take_damage(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         hit_points=20)
        damage = char.take_damage(5)
        assert char.current_hp == 15
        assert char.damage_taken == 5

    def test_take_damage_with_temp_hp(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         hit_points=20, temporary_hp=10)
        damage = char.take_damage(5)
        assert char.temporary_hp == 5
        assert char.current_hp == 20

    def test_level_up(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         constitution=14, hit_points=10)
        char.level_up()
        assert char.level == 2

    def test_xp_level_up(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         constitution=14, experience=0)
        char.add_experience(1000)  # 900 < 1000 < 2700, so level 3
        assert char.level == 3
