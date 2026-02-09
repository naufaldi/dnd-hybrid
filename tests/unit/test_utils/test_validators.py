"""Tests for validators."""
import pytest
from src.utils.validators import (
    validate_coordinate, validate_character_name,
    validate_direction, validate_attribute_value
)
from src.utils.exceptions import ValidationError


class TestValidateCoordinate:
    def test_valid_coordinate_returns_unchanged(self):
        assert validate_coordinate(5, 5, 100, 100) == (5, 5)
        assert validate_coordinate(0, 0, 100, 100) == (0, 0)
        assert validate_coordinate(99, 99, 100, 100) == (99, 99)

    def test_negative_coordinates_clamped(self):
        assert validate_coordinate(-1, 5, 100, 100) == (0, 5)
        assert validate_coordinate(5, -10, 100, 100) == (5, 0)

    def test_out_of_bounds_clamped(self):
        assert validate_coordinate(101, 50, 100, 100) == (99, 50)
        assert validate_coordinate(50, 200, 100, 100) == (50, 99)


class TestValidateCharacterName:
    def test_valid_name_passes(self):
        validate_character_name("TestChar")
        validate_character_name("Sir Lancelot")
        validate_character_name("Dark-Knight")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_character_name("")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError, match="50"):
            validate_character_name("a" * 51)

    def test_invalid_characters_raise(self):
        with pytest.raises(ValidationError, match="invalid"):
            validate_character_name("test@char")


class TestValidateDirection:
    def test_valid_directions_normalized(self):
        assert validate_direction("n") == "north"
        assert validate_direction("N") == "north"
        assert validate_direction("north") == "north"
        assert validate_direction("s") == "south"
        assert validate_direction("south") == "south"
        assert validate_direction("e") == "east"
        assert validate_direction("east") == "east"
        assert validate_direction("w") == "west"
        assert validate_direction("west") == "west"

    def test_invalid_direction_raises(self):
        with pytest.raises(ValidationError, match="Invalid direction"):
            validate_direction("up")


class TestValidateAttributeValue:
    def test_valid_attribute_passes(self):
        assert validate_attribute_value(10, "strength") == 10
        assert validate_attribute_value(6, "dexterity") == 6
        assert validate_attribute_value(20, "intelligence") == 20

    def test_below_minimum_raises(self):
        with pytest.raises(ValidationError, match="must be between 6 and 20"):
            validate_attribute_value(5, "constitution")

    def test_above_maximum_raises(self):
        with pytest.raises(ValidationError, match="must be between 6 and 20"):
            validate_attribute_value(21, "wisdom")
