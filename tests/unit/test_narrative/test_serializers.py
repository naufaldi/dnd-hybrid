"""Tests for narrative serializers."""

import pytest
from unittest.mock import MagicMock
from src.narrative.serializers import NarrativeSerializer, SaveDataBuilder
from src.narrative.models import GameState, Scene, Choice, SkillCheck
from src.entities.character import Character


def create_test_character(name="TestHero", char_class="fighter", race="human"):
    """Helper to create a test character."""
    char = Character(
        id="test_char_123",
        name=name,
        character_class=char_class,
        race=race,
        strength=16,
        dexterity=14,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=10,
    )
    char.level = 3
    char.experience = 500
    char.hit_points = 25
    return char


class TestNarrativeSerializer:
    """Test narrative state serialization."""

    @pytest.fixture
    def mock_character(self):
        """Create a mock character."""
        return create_test_character()

    @pytest.fixture
    def game_state(self, mock_character):
        """Create a test game state."""
        return GameState(
            character=mock_character,
            current_scene="dungeon_entrance",
            scene_history=["start", "tavern", "dungeon_entrance"],
            choices_made=["leave_tavern", "enter_dungeon"],
            flags={"visited_tavern": True, "met_stranger": True},
            relationships={"goblin_king": 5},
            inventory=["sword", "potion"],
            current_act=1,
            is_combat=False,
            ending_determined=None,
            turns_spent=42,
        )

    def test_serialize_game_state(self, game_state):
        """Test serializing game state."""
        data = NarrativeSerializer.serialize_game_state(game_state)

        assert data["current_scene"] == "dungeon_entrance"
        assert data["scene_history"] == ["start", "tavern", "dungeon_entrance"]
        assert data["choices_made"] == ["leave_tavern", "enter_dungeon"]
        assert data["flags"]["visited_tavern"] == True
        assert data["turns_spent"] == 42
        assert "character" in data

    def test_deserialize_game_state(self, game_state):
        """Test deserializing game state."""
        data = NarrativeSerializer.serialize_game_state(game_state)
        restored = NarrativeSerializer.deserialize_game_state(data)

        assert restored.current_scene == "dungeon_entrance"
        assert restored.scene_history == ["start", "tavern", "dungeon_entrance"]
        assert restored.flags["visited_tavern"] == True
        assert restored.turns_spent == 42
        assert restored.character is not None
        assert restored.character.name == "TestHero"

    def test_serialize_character(self, mock_character):
        """Test serializing character."""
        data = NarrativeSerializer.serialize_character(mock_character)

        assert data["name"] == "TestHero"
        assert data["character_class"] == "fighter"
        assert data["race"] == "human"
        assert data["level"] == 3
        assert data["strength"] == 16

    def test_roundtrip_character(self, mock_character):
        """Test character survives serialization roundtrip."""
        data = NarrativeSerializer.serialize_character(mock_character)
        restored = NarrativeSerializer.deserialize_character(data)

        assert restored.name == mock_character.name
        assert restored.character_class == mock_character.character_class
        assert restored.race == mock_character.race
        assert restored.level == mock_character.level
        assert restored.strength == mock_character.strength

    def test_serialize_scene(self):
        """Test serializing scene."""
        scene = Scene(
            id="test_scene",
            act=1,
            title="Test Scene",
            description="A test scene description.",
            choices=[
                Choice(
                    id="choice1",
                    text="Make a choice",
                    shortcut="A",
                    next_scene="next_scene",
                    set_flags={"test_flag": True},
                )
            ],
            flags_set={"scene_visited": True},
            is_combat=False,
            is_ending=False,
        )

        data = NarrativeSerializer.serialize_scene(scene)

        assert data["id"] == "test_scene"
        assert data["title"] == "Test Scene"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["id"] == "choice1"
        assert data["flags_set"]["scene_visited"] == True

    def test_deserialize_scene(self):
        """Test deserializing scene."""
        scene_data = {
            "id": "test_scene",
            "act": 1,
            "title": "Test Scene",
            "description": "A test scene description.",
            "choices": [
                {
                    "id": "choice1",
                    "text": "Make a choice",
                    "shortcut": "A",
                    "next_scene": "next_scene",
                    "skill_check": {
                        "ability": "dex",
                        "dc": 12,
                        "success_next_scene": "success_scene",
                        "failure_next_scene": "failure_scene",
                    },
                    "set_flags": {"test_flag": True},
                    "consequences": [],
                    "required_flags": {},
                }
            ],
            "flags_set": {"scene_visited": True},
            "flags_required": {},
            "is_combat": False,
            "is_ending": False,
            "ending_type": None,
        }

        scene = NarrativeSerializer.deserialize_scene(scene_data)

        assert scene.id == "test_scene"
        assert len(scene.choices) == 1
        assert scene.choices[0].skill_check is not None
        assert scene.choices[0].skill_check.ability == "dex"
        assert scene.choices[0].skill_check.dc == 12


class TestSaveDataBuilder:
    """Test save data building."""

    @pytest.fixture
    def mock_character(self):
        """Create a mock character."""
        return create_test_character("TestWizard", "wizard", "elf")

    @pytest.fixture
    def game_state(self, mock_character):
        """Create a test game state."""
        return GameState(
            character=mock_character,
            current_scene="boss_fight",
            choices_made=["choice1", "choice2", "choice3"],
            flags={"saved_village": True},
        )

    def test_build_full_save(self, game_state):
        """Test building full save data."""
        metadata = {"playtime_seconds": 1800, "difficulty": "normal"}
        save_data = SaveDataBuilder.build_full_save(game_state, metadata)

        assert save_data["version"] == 2
        assert save_data["game_type"] == "narrative"
        assert save_data["metadata"]["playtime_seconds"] == 1800
        assert "narrative_state" in save_data
        assert save_data["narrative_state"]["current_scene"] == "boss_fight"

    def test_extract_narrative_state(self, game_state):
        """Test extracting narrative state from save."""
        save_data = SaveDataBuilder.build_full_save(game_state)
        extracted = SaveDataBuilder.extract_narrative_state(save_data)

        assert extracted.current_scene == "boss_fight"
        assert len(extracted.choices_made) == 3
        assert extracted.flags["saved_village"] == True
        assert extracted.character is not None

    def test_save_without_metadata(self, game_state):
        """Test building save without metadata."""
        save_data = SaveDataBuilder.build_full_save(game_state)

        assert save_data["metadata"] == {}
        assert save_data["version"] == 2

    def test_empty_game_state(self):
        """Test serializing empty game state."""
        state = GameState(character=None, current_scene="start")
        data = NarrativeSerializer.serialize_game_state(state)

        assert data["current_scene"] == "start"
        assert "character" in data
        assert data["character"] is None
