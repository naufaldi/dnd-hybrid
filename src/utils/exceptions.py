"""Custom exceptions for the game."""


class GameError(Exception):
    """Base exception for all game errors."""
    pass


class SaveError(GameError):
    """Save/load related errors."""
    pass


class SaveCorruptionError(SaveError):
    """Save file is corrupted."""

    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Save file '{filename}' is corrupted")


class SaveVersionError(SaveError):
    """Save file version is incompatible."""

    def __init__(self):
        super().__init__("Save file version is incompatible")


class SaveNotFoundError(SaveError):
    """Save file does not exist."""

    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Save file '{filename}' not found")


class CombatError(GameError):
    """Combat-related errors."""
    pass


class TargetNotFoundError(CombatError):
    """Target not found for attack."""

    def __init__(self):
        super().__init__("Target not found")


class InvalidActionError(CombatError):
    """Player attempted invalid action."""

    def __init__(self, action: str):
        self.action = action
        super().__init__(f"Invalid action: {action}")


class MovementError(GameError):
    """Movement-related errors."""
    pass


class BlockedPathError(MovementError):
    """Path is blocked by obstacle."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        super().__init__(f"Path blocked at ({x}, {y})")


class ValidationError(GameError):
    """Input validation error."""
    pass
