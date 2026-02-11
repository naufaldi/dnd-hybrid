"""Tests for Ending Manager."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.narrative.ending_manager import EndingManager
from src.narrative.models import Ending, GameState


class MockCharacter:
    def __init__(self, level=1, gold=0):
        self.level = level
        self.gold = gold


class TestEndingManager:
    """Test ending management."""

    @pytest.fixture
    def endings_file(self, tmp_path):
        file = tmp_path / "endings.yaml"
        file.write_text("""
endings:
  legendary:
    title: "The Legendary Hero"
    description: |
      Not only have you defeated the dungeon's master, but you've discovered
      ancient secrets and become a legend in your own time.
    requirements:
      flags_required:
        defeated_boss: true
        found_treasure: true
        saved_town: true
      min_gold: 500
      min_level: 5
      choices_made:
        - heroic_choice

  hero:
    title: "Hero Ending"
    description: "You are a hero."
    requirements:
      flags_required:
        defeated_boss: true
        saved_town: true
      min_gold: 100
      min_level: 3

  survivor:
    title: "Survivor Ending"
    description: "You survived."
    requirements:
      flags_required:
        escaped_dungeon: true
      min_gold: 0
      min_level: 1

  mystery:
    title: "Mystery"
    description: "Unknown fate."
    requirements:
      flags_required: {}
      min_gold: 0
      min_level: 1
""")
        return file

    @pytest.fixture
    def ending_manager(self, endings_file):
        return EndingManager(endings_file)

    def test_load_endings(self, ending_manager):
        assert len(ending_manager.endings) == 4
        assert "hero" in ending_manager.endings
        assert "survivor" in ending_manager.endings
        assert "legendary" in ending_manager.endings

    def test_get_ending(self, ending_manager):
        ending = ending_manager.get_ending("hero")
        assert ending is not None
        assert ending.title == "Hero Ending"

    def test_get_ending_not_found(self, ending_manager):
        ending = ending_manager.get_ending("nonexistent")
        assert ending is None

    def test_determine_ending_hero_requirements_met(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=5, gold=500),
            current_scene="test",
            flags={"defeated_boss": True, "saved_town": True},
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "hero"

    def test_determine_ending_survivor_requirements_met(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=1, gold=0),
            current_scene="test",
            flags={"escaped_dungeon": True},
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "survivor"

    def test_determine_ending_partial_flags(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=1, gold=0),
            current_scene="test",
            flags={"defeated_boss": True},
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "mystery"

    def test_determine_ending_min_gold_not_met(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=5, gold=50),
            current_scene="test",
            flags={"defeated_boss": True, "saved_town": True},
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "mystery"

    def test_determine_ending_min_level_not_met(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=2, gold=500),
            current_scene="test",
            flags={"defeated_boss": True, "saved_town": True},
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "mystery"

    def test_determine_ending_with_choices_made(self, ending_manager):
        state = GameState(
            character=MockCharacter(level=5, gold=500),
            current_scene="test",
            flags={"defeated_boss": True, "saved_town": True, "found_treasure": True},
            choices_made=["heroic_choice"],
        )
        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "legendary"

    def test_get_all_endings(self, ending_manager):
        all_endings = ending_manager.get_all_endings()
        assert len(all_endings) == 4
        assert "hero" in all_endings
        assert "survivor" in all_endings
        assert "legendary" in all_endings

    def test_get_ending_count(self, ending_manager):
        assert ending_manager.get_ending_count() == 4

    def test_nonexistent_file_warning(self, caplog):
        manager = EndingManager(Path("/nonexistent/endings.yaml"))
        assert len(manager.endings) == 0
        assert "not found" in caplog.text.lower()
