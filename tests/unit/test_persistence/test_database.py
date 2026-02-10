# tests/unit/test_persistence/test_database.py
"""Tests for database module."""

import pytest
import tempfile
from pathlib import Path
from src.persistence.database import Database


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        db.initialize()
        yield db
        db.close()


class TestDatabase:
    def test_initialize_creates_tables(self, temp_db):
        """Test that initialize creates all tables."""
        cursor = temp_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "characters" in tables
        assert "world_states" in tables
        assert "inventory_items" in tables

    def test_save_and_load_character(self, temp_db):
        """Test saving and loading a character."""
        character = {
            "id": "test_char",
            "name": "TestHero",
            "level": 5,
            "experience": 5000,
            "character_class": "fighter",
            "race": "human",
            "background": "",
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8,
            "hit_points": 50,
            "temporary_hp": 0,
            "exhaustion_level": 0,
            "alive": True,
            "death_save_successes": 0,
            "death_save_failures": 0,
            "current_floor": 1,
            "position_x": 0,
            "position_y": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "turns_survived": 0,
        }

        temp_db.save_character(character)
        loaded = temp_db.load_character("test_char")

        assert loaded is not None
        assert loaded["name"] == "TestHero"
        assert loaded["level"] == 5

    def test_load_nonexistent_character(self, temp_db):
        """Test loading a character that doesn't exist."""
        result = temp_db.load_character("does_not_exist")
        assert result is None

    def test_delete_character(self, temp_db):
        """Test deleting a character."""
        character = {
            "id": "to_delete",
            "name": "DeleteMe",
            "level": 1,
            "experience": 0,
            "character_class": "rogue",
            "race": "elf",
            "background": "",
            "strength": 10,
            "dexterity": 16,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "hit_points": 10,
            "temporary_hp": 0,
            "exhaustion_level": 0,
            "alive": True,
            "death_save_successes": 0,
            "death_save_failures": 0,
            "current_floor": 1,
            "position_x": 0,
            "position_y": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "turns_survived": 0,
        }
        temp_db.save_character(character)
        temp_db.delete_character("to_delete")
        assert temp_db.load_character("to_delete") is None

    def test_list_characters(self, temp_db):
        """Test listing all characters."""
        for i in range(3):
            character = {
                "id": f"char_{i}",
                "name": f"Hero{i}",
                "level": i + 1,
                "experience": 0,
                "character_class": "fighter",
                "race": "human",
                "background": "",
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
                "hit_points": 10,
                "temporary_hp": 0,
                "exhaustion_level": 0,
                "alive": True,
                "death_save_successes": 0,
                "death_save_failures": 0,
                "current_floor": 1,
                "position_x": 0,
                "position_y": 0,
                "damage_dealt": 0,
                "damage_taken": 0,
                "turns_survived": 0,
            }
            temp_db.save_character(character)

        characters = temp_db.list_characters()
        assert len(characters) == 3

    def test_schema_version(self, temp_db):
        """Test schema version tracking."""
        version = temp_db.get_schema_version()
        assert version > 0

    def test_save_and_load_world_state(self, temp_db):
        """Test saving and loading world state."""
        character_id = "world_test_char"
        floor = 3
        seed = 12345
        explored = '{"0,0": true, "1,0": true}'
        rooms = '{"rooms": [{"x": 0, "y": 0}]}'

        temp_db.save_world_state(character_id, floor, seed, explored, rooms)
        loaded = temp_db.load_world_state(character_id, floor)

        assert loaded is not None
        assert loaded["floor_number"] == floor
        assert loaded["dungeon_seed"] == seed
        assert loaded["explored_tiles"] == explored
        assert loaded["room_data"] == rooms

    def test_load_nonexistent_world_state(self, temp_db):
        """Test loading world state that doesn't exist."""
        result = temp_db.load_world_state("nonexistent", 1)
        assert result is None

    def test_save_and_get_kills(self, temp_db):
        """Test saving and retrieving kill counts."""
        character_id = "killer_test"

        temp_db.save_kill(character_id, "goblin")
        temp_db.save_kill(character_id, "goblin")
        temp_db.save_kill(character_id, "orc")

        kills = temp_db.get_kills(character_id)
        assert len(kills) == 2

        kill_dict = {k["enemy_type"]: k["kill_count"] for k in kills}
        assert kill_dict["goblin"] == 2
        assert kill_dict["orc"] == 1
