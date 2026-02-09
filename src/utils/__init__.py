"""Utils package for D&D Roguelike game."""

from .exceptions import (
    GameError,
    SaveError,
    SaveCorruptionError,
    SaveVersionError,
    SaveNotFoundError,
    CombatError,
    TargetNotFoundError,
    InvalidActionError,
    MovementError,
    BlockedPathError,
    ValidationError,
)

from .validators import (
    validate_coordinate,
    validate_character_name,
    validate_direction,
    validate_attribute_value,
)

from .logger import GameLogger, get_logger

__all__ = [
    # Exceptions
    "GameError",
    "SaveError",
    "SaveCorruptionError",
    "SaveVersionError",
    "SaveNotFoundError",
    "CombatError",
    "TargetNotFoundError",
    "InvalidActionError",
    "MovementError",
    "BlockedPathError",
    "ValidationError",
    # Validators
    "validate_coordinate",
    "validate_character_name",
    "validate_direction",
    "validate_attribute_value",
    # Logger
    "GameLogger",
    "get_logger",
]
