"""Integration tests for narrative game flow."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.narrative.scene_manager import SceneManager
from src.narrative.ending_manager import EndingManager
from src.narrative.models import Scene, Choice, GameState, SkillCheck


class MockCharacter:
    def __init__(self, level=1, gold=0):
        self.level = level
        self.gold = 0
        self.strength_mod = 1
        self.dexterity_mod = 1
        self.constitution_mod = 1
        self.intelligence_mod = 1
        self.wisdom_mod = 1
        self.charisma_mod = 1


class TestNarrativeFlow:
    """Test the complete narrative flow."""

    @pytest.fixture
    def scene_manager(self):
        with patch("pathlib.Path.glob", return_value=[]):
            manager = SceneManager(Path("src/story/scenes"), None)
            manager.scenes = self._create_test_scenes()
            return manager

    @pytest.fixture
    def ending_manager(self, tmp_path):
        endings_file = tmp_path / "endings.yaml"
        endings_file.write_text("""
endings:
  hero:
    title: "Hero"
    description: "You won."
    requirements:
      flags_required:
        saved_town: true
      min_gold: 0
      min_level: 1
  mystery:
    title: "Mystery"
    description: "Unknown."
    requirements:
      flags_required: {}
      min_gold: 0
      min_level: 1
""")
        return EndingManager(endings_file)

    def _create_test_scenes(self):
        start_scene = Scene(
            id="start",
            act=1,
            title="The Beginning",
            description="You begin your journey in a tavern.",
            choices=[
                Choice(
                    id="leave_tavern",
                    text="Leave the tavern",
                    shortcut="A",
                    next_scene="dungeon_entrance",
                ),
                Choice(
                    id="stay",
                    text="Stay and drink more",
                    shortcut="B",
                    next_scene="start",
                    set_flags={"stayed_at_tavern": True},
                ),
            ],
        )

        dungeon_scene = Scene(
            id="dungeon_entrance",
            act=1,
            title="Dungeon Entrance",
            description="A dark dungeon awaits.",
            choices=[
                Choice(
                    id="enter_boldly",
                    text="Enter boldly",
                    shortcut="A",
                    next_scene="dungeon_hall",
                ),
            ],
            flags_set={"visited_dungeon": True},
        )

        hall_scene = Scene(
            id="dungeon_hall",
            act=1,
            title="Dungeon Hall",
            description="A long hallway with torches.",
            choices=[
                Choice(
                    id="fight_goblin",
                    text="Fight the goblin",
                    shortcut="A",
                    next_scene="goblin_victory",
                ),
                Choice(
                    id="run_away",
                    text="Run back",
                    shortcut="B",
                    next_scene="dungeon_entrance",
                    set_flags={"ran_away": True},
                ),
            ],
            flags_set={"entered_hall": True},
        )

        victory_scene = Scene(
            id="goblin_victory",
            act=1,
            title="Victory!",
            description="You defeated the goblin!",
            choices=[
                Choice(
                    id="continue_on",
                    text="Continue your adventure",
                    shortcut="A",
                    next_scene="boss_door",
                ),
            ],
            flags_set={"defeated_goblin": True},
        )

        boss_scene = Scene(
            id="boss_door",
            act=1,
            title="The Boss Door",
            description="A massive door blocks your path.",
            choices=[
                Choice(
                    id="save_town",
                    text="Open the door to save the town",
                    shortcut="A",
                    next_scene="ending",
                    set_flags={"saved_town": True},
                ),
                Choice(
                    id="leave",
                    text="Turn back",
                    shortcut="B",
                    next_scene="dungeon_entrance",
                ),
            ],
        )

        ending_scene = Scene(
            id="ending",
            act=1,
            title="The End",
            description="Your journey ends here.",
            choices=[],
            is_ending=True,
        )

        return {
            "start": start_scene,
            "dungeon_entrance": dungeon_scene,
            "dungeon_hall": hall_scene,
            "goblin_victory": victory_scene,
            "boss_door": boss_scene,
            "ending": ending_scene,
        }

    def test_scene_transition_simple(self, scene_manager):
        """Test basic scene-to-scene transitions."""
        scene = scene_manager.get_scene("start")
        assert scene.id == "start"

        choice = scene.choices[0]
        assert choice.next_scene == "dungeon_entrance"

        next_scene = scene_manager.get_scene("dungeon_entrance")
        assert next_scene.id == "dungeon_entrance"
        assert next_scene.flags_set["visited_dungeon"] == True

    def test_choice_sets_flags(self, scene_manager):
        """Test that choices can set flags."""
        scene = scene_manager.get_scene("start")
        choice = scene.choices[1]
        assert choice.set_flags["stayed_at_tavern"] == True

    def test_full_game_path(self, scene_manager, ending_manager):
        """Test completing a full game path."""
        character = MockCharacter(level=1, gold=0)
        state = GameState(character=character, current_scene="start")

        state.current_scene = "start"
        scene_manager.apply_flags(scene_manager.get_scene("start"), state)
        assert state.flags.get("visited_dungeon") == None

        state.current_scene = "dungeon_entrance"
        scene_manager.apply_flags(scene_manager.get_scene("dungeon_entrance"), state)
        assert state.flags["visited_dungeon"] == True

        state.current_scene = "dungeon_hall"
        scene_manager.apply_flags(scene_manager.get_scene("dungeon_hall"), state)
        assert state.flags["entered_hall"] == True

        state.current_scene = "goblin_victory"
        scene_manager.apply_flags(scene_manager.get_scene("goblin_victory"), state)
        assert state.flags["defeated_goblin"] == True

        state.current_scene = "boss_door"
        scene_manager.apply_flags(scene_manager.get_scene("boss_door"), state)
        state.flags["saved_town"] = True

        ending = ending_manager.determine_ending(state)
        assert ending is not None
        assert ending.id == "hero"

    def test_run_away_path(self, scene_manager, ending_manager):
        """Test the run-away path."""
        character = MockCharacter(level=1, gold=0)
        state = GameState(character=character, current_scene="start")

        state.current_scene = "dungeon_hall"
        state = self._make_choice(scene_manager, state, "run_away")
        assert state.flags["ran_away"] == True
        assert state.current_scene == "dungeon_entrance"

    def _make_choice(self, scene_manager, state, choice_id):
        """Helper to make a choice and update state."""
        scene = scene_manager.get_scene(state.current_scene)
        choice = next((c for c in scene.choices if c.id == choice_id), None)
        if not choice:
            return state

        for flag, value in choice.set_flags.items():
            state.flags[flag] = value

        if choice.next_scene:
            state.current_scene = choice.next_scene
            next_scene = scene_manager.get_scene(choice.next_scene)
            for flag, value in next_scene.flags_set.items():
                state.flags[flag] = value

        return state

    def test_ending_determination(self, scene_manager, ending_manager):
        """Test ending determination logic."""
        character = MockCharacter(level=3, gold=100)

        state_hero = GameState(character=character, current_scene="end")
        state_hero.flags["saved_town"] = True
        ending_hero = ending_manager.determine_ending(state_hero)
        assert ending_hero.id == "hero"

        state_mystery = GameState(character=character, current_scene="end")
        ending_mystery = ending_manager.determine_ending(state_mystery)
        assert ending_mystery.id == "mystery"

    def test_scene_history_tracking(self, scene_manager):
        """Test that scene history is tracked."""
        character = MockCharacter(level=1, gold=0)
        state = GameState(character=character, current_scene="start")
        state.scene_history = []

        state.scene_history.append(state.current_scene)
        state.current_scene = "dungeon_entrance"
        state.scene_history.append(state.current_scene)

        assert len(state.scene_history) == 2
        assert state.scene_history[0] == "start"
        assert state.scene_history[1] == "dungeon_entrance"
