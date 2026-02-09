"""Tests for attributes module."""

import pytest
from src.character.attributes import (
    AttributeSet, attribute_modifier, ability_score_increase_levels
)


class TestAttributeModifier:
    """Tests for attribute_modifier function."""

    def test_modifier_table(self):
        assert attribute_modifier(1) == -5
        assert attribute_modifier(8) == -1
        assert attribute_modifier(10) == 0
        assert attribute_modifier(12) == 1
        assert attribute_modifier(16) == 3
        assert attribute_modifier(20) == 5
        assert attribute_modifier(30) == 10


class TestAttributeSet:
    """Tests for AttributeSet dataclass."""

    def test_default_values(self):
        attrs = AttributeSet()
        assert attrs.strength == 10
        assert attrs.dexterity == 10
        assert attrs.constitution == 10
        assert attrs.intelligence == 10
        assert attrs.wisdom == 10
        assert attrs.charisma == 10

    def test_custom_values(self):
        attrs = AttributeSet(strength=16, dexterity=14, constitution=15)
        assert attrs.strength == 16
        assert attrs.dexterity == 14
        assert attrs.constitution == 15

    def test_modifier_properties(self):
        attrs = AttributeSet(strength=16)  # +3 modifier
        assert attrs.str_mod == 3

    def test_modifier_properties_dex(self):
        attrs = AttributeSet(dexterity=20)  # +5 modifier
        assert attrs.dex_mod == 5

    def test_get_modifier(self):
        attrs = AttributeSet(strength=16)
        assert attrs.get_modifier("strength") == 3

    def test_get_score(self):
        attrs = AttributeSet(intelligence=14)
        assert attrs.get_score("intelligence") == 14

    def test_increase_attribute(self):
        attrs = AttributeSet(strength=10)
        attrs.increase_attribute("strength")
        assert attrs.strength == 12

    def test_increase_attribute_caps_at_30(self):
        attrs = AttributeSet(strength=29)
        attrs.increase_attribute("strength", 5)
        assert attrs.strength == 30

    def test_ability_score_increase_levels(self):
        levels = ability_score_increase_levels()
        assert 4 in levels
        assert 8 in levels
        assert 12 in levels
        assert 16 in levels
        assert 19 in levels
        assert 20 not in levels

    def test_to_dict(self):
        attrs = AttributeSet(strength=16, dexterity=14)
        d = attrs.to_dict()
        assert d["strength"] == 16
        assert d["dexterity"] == 14

    def test_from_dict(self):
        d = {"strength": 16, "dexterity": 14, "constitution": 15,
             "intelligence": 10, "wisdom": 10, "charisma": 10}
        attrs = AttributeSet.from_dict(d)
        assert attrs.strength == 16
        assert attrs.dexterity == 14
