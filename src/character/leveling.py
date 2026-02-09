"""XP, level-up logic, and proficiency bonus."""

from dataclasses import dataclass, field
from typing import Callable, List


# XP thresholds for levels 1-20
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]


# Proficiency bonus by level range
PROFICIENCY_BY_LEVEL = [
    (1, 4, 2),
    (5, 8, 3),
    (9, 12, 4),
    (13, 16, 5),
    (17, 20, 6),
]


def _get_proficiency_for_level(level: int) -> int:
    """Get proficiency bonus for a given level."""
    for min_level, max_level, bonus in PROFICIENCY_BY_LEVEL:
        if min_level <= level <= max_level:
            return bonus
    return 6  # Cap at level 20


@dataclass
class LevelManager:
    """
    Character level management.

    Handles XP accumulation, level calculation, and proficiency bonus.
    """

    experience: int = 0
    level: int = 1
    _pending_level_ups: int = 0
    _level_up_callbacks: List[Callable[[int], None]] = field(default_factory=list)
    _starting_level: int = field(default=0, repr=False)

    def __post_init__(self):
        """Set experience to match starting level if needed."""
        # Handle starting_level parameter
        if self._starting_level > 0:
            self.level = min(self._starting_level, 20)
            self.experience = XP_THRESHOLDS[self.level - 1]
        elif self.level > 1 and self.experience == 0:
            self.experience = XP_THRESHOLDS[self.level - 1]

    def __init__(self, experience: int = 0, level: int = 1, starting_level: int = 0):
        """Initialize LevelManager.

        Args:
            experience: Starting XP amount
            level: Starting level
            starting_level: Convenience parameter to start at a specific level
                           (overrides level if provided)
        """
        self.experience = experience
        self._pending_level_ups = 0
        self._level_up_callbacks = []

        if starting_level > 0:
            self.level = min(starting_level, 20)
            self.experience = XP_THRESHOLDS[self.level - 1]
        else:
            self.level = level
            if level > 1 and experience == 0:
                self.experience = XP_THRESHOLDS[level - 1]

    def add_xp(self, amount: int) -> int:
        """
        Add XP and check for level ups.

        Args:
            amount: XP to add

        Returns:
            Number of levels gained
        """
        if amount <= 0:
            return 0

        old_level = self.level
        self.experience += amount
        self._recalculate_level()
        new_levels = self.level - old_level
        self._pending_level_ups = new_levels
        return new_levels

    def check_level_up(self) -> bool:
        """
        Check if there are pending level ups.

        Returns:
            True if character should level up
        """
        if self._pending_level_ups > 0:
            self._pending_level_ups -= 1
            self.level += 1
            self._trigger_level_up_callbacks()
            return True
        return False

    def get_level(self) -> int:
        """Get current level."""
        return self.level

    def get_xp(self) -> int:
        """Get current XP."""
        return self.experience

    def get_xp_to_next_level(self) -> int:
        """Get XP needed for next level."""
        if self.level >= 20:
            return 0
        next_threshold = XP_THRESHOLDS[self.level]
        return max(0, next_threshold - self.experience)

    def get_xp_progress(self) -> float:
        """
        Get progress to next level as percentage (0-100).

        Returns:
            Percentage of XP progress to next level
        """
        if self.level >= 20:
            return 100.0

        current_threshold = XP_THRESHOLDS[self.level - 1]
        next_threshold = XP_THRESHOLDS[self.level]
        progress = (self.experience - current_threshold) / (next_threshold - current_threshold)
        return progress * 100

    def get_proficiency_bonus(self) -> int:
        """
        Get proficiency bonus based on level.

        Returns:
            Proficiency bonus:
            - Levels 1-4: +2
            - Levels 5-8: +3
            - Levels 9-12: +4
            - Levels 13-16: +5
            - Levels 17-20: +6
        """
        return _get_proficiency_for_level(self.level)

    def _recalculate_level(self) -> None:
        """Recalculate level from XP."""
        new_level = self._calculate_level_from_xp(self.experience)
        self.level = min(new_level, 20)

    def _calculate_level_from_xp(self, experience: int) -> int:
        """Calculate level from XP."""
        for i, threshold in enumerate(XP_THRESHOLDS):
            if experience < threshold:
                return i
        return 20

    def _trigger_level_up_callbacks(self) -> None:
        """Trigger all registered level up callbacks."""
        for callback in self._level_up_callbacks:
            callback(self.level)

    def on_level_up(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for level up events.

        Args:
            callback: Function that takes the new level as parameter
        """
        self._level_up_callbacks.append(callback)

    def can_level_up(self) -> bool:
        """Check if character can level up (has pending level ups)."""
        return self._pending_level_ups > 0

    def get_level_range_for_bonus(bonus: int) -> tuple:
        """Get the level range for a proficiency bonus."""
        for min_level, max_level, b in PROFICIENCY_BY_LEVEL:
            if b == bonus:
                return (min_level, max_level)
        return (17, 20)  # Default to highest

    def __repr__(self) -> str:
        return f"LevelManager(level={self.level}, xp={self.experience})"


def level_from_xp(experience: int) -> int:
    """
    Calculate level from XP.

    Args:
        experience: Total XP

    Returns:
        Level (1-20)
    """
    for i, threshold in enumerate(XP_THRESHOLDS):
        if experience < threshold:
            return i
    return 20


def proficiency_bonus(level: int) -> int:
    """
    Calculate proficiency bonus from level.

    Args:
        level: Character level

    Returns:
        Proficiency bonus
    """
    return _get_proficiency_for_level(level)


def xp_for_level(level: int) -> int:
    """
    Get XP required for a given level.

    Args:
        level: Target level (1-20)

    Returns:
        XP required
    """
    if 1 <= level <= 20:
        return XP_THRESHOLDS[level - 1]
    return XP_THRESHOLDS[-1]
