"""Input validation utilities."""

from typing import Tuple
from .exceptions import ValidationError


def validate_coordinate(x: int, y: int, width: int, height: int) -> Tuple[int, int]:
    """Validate and clamp coordinates to bounds."""
    return (
        max(0, min(x, width - 1)),
        max(0, min(y, height - 1))
    )


def validate_character_name(name: str) -> None:
    """Validate character name."""
    if not name:
        raise ValidationError("Character name cannot be empty")
    if len(name) > 50:
        raise ValidationError("Character name cannot exceed 50 characters")
    if not name.replace(" ", "").replace("-", "").replace("'", "").isalnum():
        raise ValidationError("Character name contains invalid characters")


def validate_direction(direction: str) -> str:
    """Validate and normalize direction input."""
    direction_map = {
        "n": "north",
        "north": "north",
        "s": "south",
        "south": "south",
        "e": "east",
        "east": "east",
        "w": "west",
        "west": "west",
    }
    normalized = direction.lower()
    if normalized not in direction_map:
        raise ValidationError(f"Invalid direction: {direction}")
    return direction_map[normalized]


def validate_attribute_value(value: int, attr_name: str) -> int:
    """Validate attribute value (6-20)."""
    if not 6 <= value <= 20:
        raise ValidationError(f"{attr_name} must be between 6 and 20, got {value}")
    return value
