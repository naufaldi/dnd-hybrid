"""Tests for Scene Manager."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.narrative.scene_manager import SceneManager
from src.narrative.models import Scene, Choice, GameState, SkillCheck


class TestSceneManager:
    """Test scene management."""

    @pytest.fixture
    def mock_ai_client(self):
        client = MagicMock()
        client.enhance_description = MagicMock(return_value="Enhanced text")
        return client

    @pytest.fixture
    def scene_manager(self, mock_ai_client):
        with patch("pathlib.Path.glob", return_value=[]):
            manager = SceneManager(Path("src/story/scenes"), mock_ai_client)
            manager.scenes = {
                "start": Scene(
                    id="start",
                    act=1,
                    title="Start",
                    description="You begin your adventure.",
                    choices=[
                        Choice(id="go_left", text="Go left", shortcut="A", next_scene="left_room"),
                        Choice(
                            id="go_right", text="Go right", shortcut="B", next_scene="right_room"
                        ),
                    ],
                ),
                "left_room": Scene(
                    id="left_room",
                    act=1,
                    title="Left Room",
                    description="A dark room.",
                    choices=[],
                    is_ending=True,
                    ending_type="hero",
                ),
                "right_room": Scene(
                    id="right_room",
                    act=1,
                    title="Right Room",
                    description="A bright room.",
                    choices=[],
                ),
            }
            return manager

    def test_get_scene(self, scene_manager):
        scene = scene_manager.get_scene("start")
        assert scene is not None
        assert scene.id == "start"

    def test_get_scene_not_found(self, scene_manager):
        with pytest.raises(ValueError, match="Scene not found"):
            scene_manager.get_scene("nonexistent")

    def test_get_valid_choices(self, scene_manager):
        state = GameState(character=None, current_scene="start")

        scene = scene_manager.get_scene("start")
        choices = scene_manager.get_valid_choices(scene, state)

        assert len(choices) == 2

    def test_apply_flags(self, scene_manager):
        scene = Scene(
            id="test",
            act=1,
            title="Test",
            description="Test",
            flags_set={"test_flag": True, "another": False},
            choices=[],
        )

        state = GameState(character=None, current_scene="test")

        scene_manager.apply_flags(scene, state)
        assert state.flags["test_flag"] == True
        assert state.flags["another"] == False

    def test_get_next_scene_simple(self, scene_manager):
        choice = Choice(id="test", text="Test", shortcut="A", next_scene="left_room")

        next_scene_id = scene_manager.get_next_scene(choice)
        assert next_scene_id == "left_room"

    def test_apply_choice_consequences(self, scene_manager):
        choice = Choice(
            id="test",
            text="Test",
            shortcut="A",
            next_scene="next",
            consequences=[MagicMock(type="flag", target="has_key", value=True)],
        )

        state = GameState(character=None, current_scene="test")

        scene_manager.apply_choice_consequences(choice, state)

        assert "has_key" in state.flags

    def test_add_scene(self, scene_manager):
        new_scene = Scene(
            id="new_scene", act=1, title="New Scene", description="A new scene.", choices=[]
        )

        scene_manager.add_scene(new_scene)

        assert "new_scene" in scene_manager.scenes
        assert scene_manager.scenes["new_scene"].title == "New Scene"
