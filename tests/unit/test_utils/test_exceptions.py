"""Tests for custom exceptions."""
from src.utils.exceptions import (
    GameError, SaveError, SaveCorruptionError, SaveVersionError,
    SaveNotFoundError, CombatError, TargetNotFoundError, InvalidActionError,
    MovementError, BlockedPathError, ValidationError
)


class TestExceptionHierarchy:
    def test_game_error_is_base(self):
        assert issubclass(SaveError, GameError)
        assert issubclass(CombatError, GameError)
        assert issubclass(MovementError, GameError)
        assert issubclass(ValidationError, GameError)

    def test_save_error_hierarchy(self):
        assert issubclass(SaveCorruptionError, SaveError)
        assert issubclass(SaveVersionError, SaveError)
        assert issubclass(SaveNotFoundError, SaveError)

    def test_combat_error_hierarchy(self):
        assert issubclass(TargetNotFoundError, CombatError)
        assert issubclass(InvalidActionError, CombatError)

    def test_movement_error_hierarchy(self):
        assert issubclass(BlockedPathError, MovementError)
        assert issubclass(MovementError, GameError)


class TestSaveCorruptionError:
    def test_error_message_includes_filename(self):
        err = SaveCorruptionError("test.sav")
        assert "test.sav" in str(err)
        assert "corrupted" in str(err).lower()

    def test_error_stores_filename(self):
        err = SaveCorruptionError("save.sav")
        assert err.filename == "save.sav"


class TestSaveVersionError:
    def test_error_message_contains_version_info(self):
        err = SaveVersionError()
        assert "version" in str(err).lower()


class TestSaveNotFoundError:
    def test_error_message_includes_filename(self):
        err = SaveNotFoundError("missing.sav")
        assert "missing.sav" in str(err)
        assert "not found" in str(err).lower()


class TestBlockedPathError:
    def test_error_message_includes_coordinates(self):
        err = BlockedPathError(5, 10)
        assert "5" in str(err)
        assert "10" in str(err)
        assert "blocked" in str(err).lower()

    def test_error_stores_coordinates(self):
        err = BlockedPathError(3, 7)
        assert err.x == 3
        assert err.y == 7


class TestValidationError:
    def test_validation_error_is_game_error(self):
        assert issubclass(ValidationError, GameError)


class TestTargetNotFoundError:
    def test_error_message_indicates_target_missing(self):
        err = TargetNotFoundError()
        assert "target" in str(err).lower()


class TestInvalidActionError:
    def test_error_message_includes_action(self):
        err = InvalidActionError("attack")
        assert "attack" in str(err)
