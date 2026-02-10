# tests/unit/test_persistence/test_save_manager.py
"""Tests for save manager."""

import pytest
import tempfile
from pathlib import Path
from src.persistence.save_manager import SaveManager, SAVE_FORMAT_VERSION
from src.utils.exceptions import SaveCorruptionError


@pytest.fixture
def temp_save_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def save_manager(temp_save_dir):
    return SaveManager(temp_save_dir)


class TestSaveManager:
    def test_save_game(self, save_manager, temp_save_dir):
        """Test saving a game."""
        game_state = {
            "character": {"id": "hero1", "name": "Hero", "level": 5},
            "world": {"current_floor": 3},
        }

        path = save_manager.save_game(game_state, "test.sav")
        assert path.exists()
        assert path.name == "test.sav"

    def test_load_game(self, save_manager, temp_save_dir):
        """Test loading a game."""
        game_state = {
            "character": {"id": "hero1", "name": "Hero", "level": 5},
            "world": {"current_floor": 3},
        }

        path = save_manager.save_game(game_state, "test.sav")
        loaded, timestamp = save_manager.load_game(path)

        assert loaded["character"]["name"] == "Hero"
        assert loaded["character"]["level"] == 5
        assert loaded["world"]["current_floor"] == 3

    def test_save_and_load_roundtrip(self, save_manager):
        """Test save/load preserves all data."""
        game_state = {
            "character": {
                "id": "hero1",
                "name": "TestHero",
                "level": 10,
                "experience": 25000,
                "character_class": "wizard",
                "race": "elf",
                "background": "",
                "strength": 8,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 18,
                "wisdom": 10,
                "charisma": 12,
                "hit_points": 60,
                "temporary_hp": 0,
                "exhaustion_level": 0,
                "alive": True,
                "death_save_successes": 0,
                "death_save_failures": 0,
                "current_floor": 5,
                "position_x": 0,
                "position_y": 0,
                "damage_dealt": 0,
                "damage_taken": 0,
                "turns_survived": 0,
            },
            "world": {"current_floor": 5},
            "inventory": ["sword", "potion", "scroll"],
        }

        path = save_manager.save_game(game_state)
        loaded, _ = save_manager.load_game(path)

        assert loaded["character"]["name"] == "TestHero"
        assert loaded["character"]["level"] == 10
        assert loaded["inventory"] == ["sword", "potion", "scroll"]

    def test_list_saves(self, save_manager):
        """Test listing save files."""
        for i in range(3):
            save_manager.save_game(
                {"character": {"id": f"c{i}", "name": f"H{i}", "level": i + 1}},
                f"save{i}.sav"
            )

        saves = save_manager.list_saves()
        assert len(saves) == 3

    def test_delete_save(self, save_manager):
        """Test deleting a save."""
        save_manager.save_game(
            {"character": {"id": "c1", "name": "H1", "level": 1}},
            "to_delete.sav"
        )
        assert (save_manager.save_dir / "to_delete.sav").exists()

        save_manager.delete_save("to_delete.sav")
        assert not (save_manager.save_dir / "to_delete.sav").exists()

    def test_corrupted_save_raises(self, save_manager, temp_save_dir):
        """Test that corrupted save raises error."""
        game_state = {"character": {"id": "c1", "name": "H1", "level": 1}}
        path = save_manager.save_game(game_state, "corrupt_test.sav")

        # Corrupt the file by overwriting the beginning with invalid data
        with open(path, "r+b") as f:
            f.seek(0)
            f.write(b"CORRUPTED")

        with pytest.raises(SaveCorruptionError):
            save_manager.load_game(path)

    def test_get_latest_save(self, save_manager):
        """Test getting the most recent save."""
        assert save_manager.get_latest_save() is None

        for i in range(3):
            save_manager.save_game(
                {"character": {"id": f"c{i}", "name": f"H{i}", "level": i}},
                f"save{i}.sav"
            )

        latest = save_manager.get_latest_save()
        assert latest is not None
        assert latest.name == "save2.sav"

    def test_save_contains_checksum(self, save_manager, temp_save_dir):
        """Test that saved files contain checksums."""
        game_state = {"character": {"id": "c1", "name": "Test", "level": 1}}
        path = save_manager.save_game(game_state, "checksum_test.sav")

        # Read the compressed file and decompress it to verify checksum exists
        import zlib
        with open(path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed)
        import json
        save_data = json.loads(decompressed)
        assert "checksum" in save_data

    def test_default_filename_includes_character_id(self, save_manager):
        """Test that default filename includes character ID."""
        game_state = {"character": {"id": "my_hero", "name": "Hero", "level": 1}}
        path = save_manager.save_game(game_state)

        assert "my_hero" in path.name
        assert path.suffix == ".sav"
