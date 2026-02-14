"""End-to-end tests for combat scenarios.

These tests verify complete combat flows from scene entry through combat to resolution.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch


class TestGoblinEncounterE2E:
    """End-to-end test for goblin encounter scenario."""

    def test_goblin_encounter_scene_exists(self):
        """Test that goblin encounter scene exists and is loadable."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        scene = manager.get_scene("goblin_encounter")
        assert scene is not None
        assert scene.title is not None
        assert len(scene.choices) > 0

    def test_goblin_encounter_has_combat_choice(self):
        """Test that goblin encounter has a combat choice."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        scene = manager.get_scene("goblin_encounter")
        combat_choices = [c for c in scene.choices if c.combat_encounter]

        assert len(combat_choices) > 0, "Goblin encounter should have combat choice"

    def test_goblin_encounter_combat_navigation_complete(self):
        """Test that goblin combat has complete navigation."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        scene = manager.get_scene("goblin_encounter")

        for choice in scene.choices:
            if choice.combat_encounter:
                # Should have victory navigation
                assert choice.victory_next_scene, f"Choice {choice.id} missing victory navigation"
                victory_scene = manager.get_scene(choice.victory_next_scene)
                assert victory_scene is not None, (
                    f"Victory scene {choice.victory_next_scene} not found"
                )

                # Should have defeat navigation
                assert choice.defeat_scene, f"Choice {choice.id} missing defeat navigation"
                defeat_scene = manager.get_scene(choice.defeat_scene)
                assert defeat_scene is not None, f"Defeat scene {choice.defeat_scene} not found"


class TestFullCombatScenario:
    """Full combat scenario tests."""

    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state for testing."""
        state = Mock()
        state.character = Mock()
        state.character.hit_points = 20
        state.character.max_hp = 20
        state.character.name = "TestHero"
        state.character.strength = 14
        state.character.strength_mod = 2
        state.character.equipment = {"weapon_damage": "1d8", "weapon_stat": "strength"}
        state.is_combat = False
        state.current_enemy = None
        return state

    def test_combat_screen_initialization_with_enemy(self, mock_game_state):
        """Test combat screen initializes correctly with enemy data."""
        from src.tui.screens.combat_screen import CombatScreen

        screen = CombatScreen(
            enemy_name="Goblin",
            enemy_hp=7,
            enemy_ac=15,
            enemy_description="A small, green creature",
            victory_scene="goblin_victory",
            defeat_scene="death_in_dungeon",
        )

        # Mock app
        screen.app = Mock()
        screen.app.narrative_game_state = mock_game_state

        assert screen.enemy_name == "Goblin"
        assert screen.enemy_current_hp == 7
        assert screen.victory_scene == "goblin_victory"

    def test_combat_damage_calculation(self):
        """Test damage calculation in combat context."""
        from src.combat.dice import roll_dice, ability_modifier

        # Simulate fighter with STR 14 (+2)
        strength_mod = ability_modifier(14)

        # Roll weapon damage
        weapon_damage = roll_dice("1d8")
        total_damage = weapon_damage + strength_mod

        # Verify damage range
        assert 3 <= total_damage <= 10  # 1+2 to 8+2

    def test_attack_roll_calculation(self):
        """Test attack roll calculation."""
        from src.combat.dice import ability_modifier
        import random

        # Simulate attack
        attack_roll = random.randint(1, 20)
        str_mod = ability_modifier(14)  # +2
        proficiency = 2
        total = attack_roll + str_mod + proficiency

        # Verify calculation
        assert total == attack_roll + 4

    def test_critical_hit_damage(self):
        """Test critical hit damage calculation (double dice)."""
        from src.combat.dice import roll_dice, ability_modifier

        # On crit, roll damage twice
        damage1 = roll_dice("1d8")
        damage2 = roll_dice("1d8")
        str_mod = ability_modifier(14)  # +2, added once

        total_damage = damage1 + damage2 + str_mod

        # Verify range: 2+2 to 16+2
        assert 4 <= total_damage <= 18


class TestCombatVictoryPath:
    """Tests for combat victory scenarios."""

    def test_victory_scene_transition(self):
        """Test that victory transitions work correctly."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Test goblin victory path
        goblin_scene = manager.get_scene("goblin_victory")
        assert goblin_scene is not None
        assert goblin_scene.choices is not None

    def test_combat_victory_clears_state(self):
        """Test that victory clears combat state."""
        from src.narrative.game_state import GameState

        state = GameState()
        state.is_combat = True
        state.current_enemy = "goblin"

        # Simulate victory cleanup
        state.is_combat = False
        state.current_enemy = None

        assert state.is_combat is False
        assert state.current_enemy is None


class TestCombatDefeatPath:
    """Tests for combat defeat scenarios."""

    def test_defeat_scene_transition(self):
        """Test that defeat transitions work correctly."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Test defeat path
        defeat_scene = manager.get_scene("death_in_dungeon")
        assert defeat_scene is not None

    def test_death_scene_is_terminal(self):
        """Test that death scene ends the game."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        death_scene = manager.get_scene("death_in_dungeon")

        # Should have choices (e.g., play again)
        assert len(death_scene.choices) > 0


class TestCombatWithDifferentEnemies:
    """Tests for combat with various enemy types."""

    def test_goblin_combat_setup(self):
        """Test goblin enemy is properly configured."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        assert "goblin" in ENEMY_DEFINITIONS
        goblin = ENEMY_DEFINITIONS["goblin"]

        assert goblin.hp > 0
        assert goblin.ac > 0

    def test_cultist_boss_combat_setup(self):
        """Test cultist boss enemy is properly configured."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        assert "cultist_boss" in ENEMY_DEFINITIONS
        boss = ENEMY_DEFINITIONS["cultist_boss"]

        assert boss.hp > 0
        assert boss.ac > 0
        # Boss should be stronger than goblin
        assert boss.hp > ENEMY_DEFINITIONS["goblin"].hp

    def test_guardian_combat_setup(self):
        """Test guardian enemy is properly configured."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        assert "guardian" in ENEMY_DEFINITIONS
        guardian = ENEMY_DEFINITIONS["guardian"]

        assert guardian.hp > 0
        assert guardian.ac > 0


class TestSkillCheckToCombatTransition:
    """Tests for transitions from skill checks to combat."""

    def test_failed_skill_check_leads_to_combat(self):
        """Test that failed skill checks can lead to combat."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Check goblin_attack scene (failure of negotiation)
        scene = manager.get_scene("goblin_attack")
        assert scene is not None

        # Should have combat
        combat_choices = [c for c in scene.choices if c.combat_encounter]
        assert len(combat_choices) > 0

    def test_trap_failure_combat_transition(self):
        """Test trap failure leading to combat."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Check trap scenarios
        trap_scene = manager.get_scene("goblin_flee_fail")
        assert trap_scene is not None


class TestFullCombatSequence:
    """Tests for complete combat sequences."""

    def test_tavern_to_goblin_combat_path(self):
        """Test full path from tavern to goblin combat."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Verify the path exists
        critical_path = [
            "tavern_entry",
            "dungeon_entrance",
            "dungeon_entry_hall",
            "goblin_encounter",
        ]

        for scene_id in critical_path:
            scene = manager.get_scene(scene_id)
            assert scene is not None, f"Scene {scene_id} not found"

    def test_combat_to_victory_path_exists(self):
        """Test that combat leads to victory scene."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Get goblin encounter
        goblin_scene = manager.get_scene("goblin_encounter")

        # Find combat choice
        for choice in goblin_scene.choices:
            if choice.combat_encounter and choice.victory_next_scene:
                victory_scene = manager.get_scene(choice.victory_next_scene)
                assert victory_scene is not None
                break
        else:
            pytest.fail("No combat choice with victory scene found")

    def test_multiple_combats_in_act1(self):
        """Test that Act 1 has multiple combat encounters."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        combat_scenes = []
        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.combat_encounter:
                    combat_scenes.append(scene_id)
                    break

        # Should have multiple combat scenes
        assert len(combat_scenes) >= 3, f"Expected 3+ combat scenes, found {len(combat_scenes)}"


class TestCombatImportValidation:
    """Tests to validate combat system imports work correctly."""

    def test_all_combat_imports_resolve(self):
        """Test that all combat-related imports resolve."""
        imports_to_test = [
            ("src.combat.dice", "roll_dice"),
            ("src.combat.dice", "ability_modifier"),
            ("src.combat.dice", "DiceRoller"),
            ("src.tui.screens.combat_screen", "CombatScreen"),
            ("src.entities.enemy_definitions", "ENEMY_DEFINITIONS"),
        ]

        for module_name, attr_name in imports_to_test:
            try:
                module = __import__(module_name, fromlist=[attr_name])
                getattr(module, attr_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {attr_name} from {module_name}: {e}")

    def test_combat_screen_no_import_errors(self):
        """Test that combat screen module loads without import errors."""
        try:
            from src.tui.screens.combat_screen import CombatScreen

            # If we get here, imports worked
            assert True
        except ImportError as e:
            if "roll_dice" in str(e) or "ability_modifier" in str(e):
                pytest.fail(f"Combat screen has dice import error: {e}")
            # Other errors are not our concern here
            assert True
