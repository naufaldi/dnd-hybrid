"""Tests for leveling module."""

import pytest
from src.character.leveling import LevelManager, XP_THRESHOLDS


class TestLevelManager:
    """Tests for LevelManager class."""

    def test_starting_level(self):
        lm = LevelManager()
        assert lm.get_level() == 1
        assert lm.get_proficiency_bonus() == 2

    def test_level_from_xp(self):
        lm = LevelManager()
        # Level 1: 0-299 XP
        assert lm.get_level() == 1
        # Level 2: 300-899 XP
        lm.add_xp(300)
        assert lm.get_level() == 2
        # Level 3: 900-2699 XP
        lm.add_xp(600)
        assert lm.get_level() == 3

    def test_proficiency_bonus_levels(self):
        lm = LevelManager()
        # Levels 1-4: +2
        assert lm.get_proficiency_bonus() == 2
        # Level 5-8: +3
        lm.add_xp(14000)  # Level 5
        assert lm.get_proficiency_bonus() == 3
        # Level 9-12: +4
        lm.add_xp(34000)  # Level 9
        assert lm.get_proficiency_bonus() == 4

    def test_max_level(self):
        lm = LevelManager()
        lm.add_xp(1000000)  # Way past level 20
        assert lm.get_level() == 20

    def test_add_xp(self):
        lm = LevelManager()
        lm.add_xp(500)
        assert lm.get_xp() == 500

    def test_xp_to_next_level(self):
        lm = LevelManager()
        lm.add_xp(100)
        # Should need 200 more for level 2 (300 - 100)
        needed = lm.get_xp_to_next_level()
        assert needed == 200

    def test_level_up_callback(self):
        callback_called = []

        def on_level_up(level):
            callback_called.append(level)

        lm = LevelManager()
        lm.on_level_up(on_level_up)
        lm.add_xp(300)  # Level goes to 2, pending = 1
        lm.check_level_up()  # Process pending level up, triggers callback
        assert len(callback_called) >= 1

    def test_threshold_values(self):
        assert XP_THRESHOLDS[0] == 0      # Level 1
        assert XP_THRESHOLDS[1] == 300    # Level 2
        assert XP_THRESHOLDS[4] == 6500   # Level 5 (not 14000)
        assert XP_THRESHOLDS[9] == 64000   # Level 10


class TestXPThresholds:
    """Tests for XP threshold values."""

    def test_thresholds_increase(self):
        for i in range(len(XP_THRESHOLDS) - 1):
            assert XP_THRESHOLDS[i] < XP_THRESHOLDS[i + 1]

    def test_exact_thresholds(self):
        assert XP_THRESHOLDS[0] == 0
        assert XP_THRESHOLDS[19] == 355000  # Level 20
