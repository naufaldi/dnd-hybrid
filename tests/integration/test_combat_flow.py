"""Integration tests for combat system integration."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch


class TestCombatSceneIntegration:
    """Tests for combat integration with scene system."""

    def test_combat_scenes_have_valid_enemy_references(self):
        """Test that all combat scenes reference valid enemies."""
        from src.narrative.scene_manager import SceneManager
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        invalid_references = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.combat_encounter:
                    enemy_id = choice.combat_encounter
                    if enemy_id not in ENEMY_DEFINITIONS:
                        invalid_references.append(
                            f"{scene_id}: references invalid enemy '{enemy_id}'"
                        )

        assert len(invalid_references) == 0, f"Invalid enemy references found:\n" + "\n".join(
            invalid_references
        )

    def test_combat_scenes_have_victory_navigation(self):
        """Test that combat scenes have victory_next_scene defined."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        missing_victory = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.combat_encounter:
                    if not choice.victory_next_scene:
                        missing_victory.append(
                            f"{scene_id}: combat choice '{choice.id}' missing victory_next_scene"
                        )

        assert len(missing_victory) == 0, (
            f"Combat choices missing victory navigation:\n" + "\n".join(missing_victory)
        )

    def test_combat_scenes_have_defeat_navigation(self):
        """Test that combat scenes have defeat_scene defined."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        missing_defeat = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.combat_encounter:
                    if not choice.defeat_scene:
                        missing_defeat.append(
                            f"{scene_id}: combat choice '{choice.id}' missing defeat_scene"
                        )

        assert len(missing_defeat) == 0, f"Combat choices missing defeat navigation:\n" + "\n".join(
            missing_defeat
        )

    def test_victory_scenes_exist(self):
        """Test that all victory_next_scene references point to existing scenes."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        all_scene_ids = set(manager.scenes.keys())
        missing_scenes = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.victory_next_scene:
                    if choice.victory_next_scene not in all_scene_ids:
                        missing_scenes.append(
                            f"{scene_id}: victory_next_scene '{choice.victory_next_scene}' doesn't exist"
                        )

        assert len(missing_scenes) == 0, f"Missing victory scenes:\n" + "\n".join(missing_scenes)

    def test_defeat_scenes_exist(self):
        """Test that all defeat_scene references point to existing scenes."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        all_scene_ids = set(manager.scenes.keys())
        missing_scenes = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.defeat_scene:
                    if choice.defeat_scene not in all_scene_ids:
                        missing_scenes.append(
                            f"{scene_id}: defeat_scene '{choice.defeat_scene}' doesn't exist"
                        )

        assert len(missing_scenes) == 0, f"Missing defeat scenes:\n" + "\n".join(missing_scenes)


class TestEnemyDefinitions:
    """Tests for enemy definition loading and usage."""

    def test_enemy_definitions_load(self):
        """Test that enemy definitions are loaded."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        assert len(ENEMY_DEFINITIONS) > 0
        assert "goblin" in ENEMY_DEFINITIONS

    def test_enemy_has_required_fields(self):
        """Test that enemies have required fields."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        required_fields = ["name", "hp", "ac"]

        for enemy_id, enemy in ENEMY_DEFINITIONS.items():
            for field in required_fields:
                assert hasattr(enemy, field) or field in enemy, (
                    f"Enemy '{enemy_id}' missing required field: {field}"
                )

    def test_enemy_hp_is_positive(self):
        """Test that enemy HP is positive."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        for enemy_id, enemy in ENEMY_DEFINITIONS.items():
            hp = getattr(enemy, "hp", enemy.get("hp", 0))
            assert hp > 0, f"Enemy '{enemy_id}' has invalid HP: {hp}"

    def test_enemy_ac_is_valid(self):
        """Test that enemy AC is within valid range."""
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        for enemy_id, enemy in ENEMY_DEFINITIONS.items():
            ac = getattr(enemy, "ac", enemy.get("ac", 0))
            assert 5 <= ac <= 30, f"Enemy '{enemy_id}' has unusual AC: {ac}"


class TestCombatDiceIntegration:
    """Tests for dice system integration with combat."""

    def test_import_roll_dice_from_combat_dice(self):
        """Test that roll_dice can be imported from combat.dice."""
        from src.combat.dice import roll_dice

        assert callable(roll_dice)

    def test_import_ability_modifier_from_combat_dice(self):
        """Test that ability_modifier can be imported from combat.dice."""
        from src.combat.dice import ability_modifier

        assert callable(ability_modifier)

    def test_roll_dice_used_in_combat_context(self):
        """Test that roll_dice works in combat calculations."""
        from src.combat.dice import roll_dice

        # Simulate weapon damage roll
        damage = roll_dice("1d8")
        assert 1 <= damage <= 8

    def test_ability_modifier_used_in_attack_calculation(self):
        """Test that ability_modifier works in attack calculations."""
        from src.combat.dice import ability_modifier

        strength = 16
        modifier = ability_modifier(strength)

        # Simulate attack roll
        import random

        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + modifier + 2  # + proficiency

        assert total_attack >= attack_roll + 1  # modifier should add

    def test_combat_screen_imports_resolve(self):
        """Test that combat screen can import dice functions."""
        try:
            from src.tui.screens.combat_screen import CombatScreen

            # If this import works, the dice imports inside should also work
            assert True
        except ImportError as e:
            pytest.fail(f"Combat screen import failed: {e}")


class TestCombatStateManagement:
    """Tests for combat state in game state."""

    def test_game_state_has_combat_flags(self):
        """Test that game state tracks combat flags."""
        from src.narrative.game_state import GameState

        state = GameState()

        # Should have combat-related attributes
        assert hasattr(state, "is_combat")
        assert hasattr(state, "current_enemy")
        assert hasattr(state, "victory_scene")
        assert hasattr(state, "defeat_scene")

    def test_combat_flags_defaults(self):
        """Test default values for combat flags."""
        from src.narrative.game_state import GameState

        state = GameState()

        assert state.is_combat is False
        assert state.current_enemy is None

    def test_combat_flags_can_be_set(self):
        """Test that combat flags can be modified."""
        from src.narrative.game_state import GameState

        state = GameState()

        state.is_combat = True
        state.current_enemy = "goblin"
        state.victory_scene = "goblin_victory"
        state.defeat_scene = "death_in_dungeon"

        assert state.is_combat is True
        assert state.current_enemy == "goblin"
        assert state.victory_scene == "goblin_victory"
        assert state.defeat_scene == "death_in_dungeon"


class TestCombatCharacterIntegration:
    """Tests for character integration with combat."""

    def test_character_has_combat_stats(self):
        """Test that characters have combat-relevant stats."""
        from src.character.character import Character

        char = Character(
            name="Test",
            character_class="fighter",
            race="human",
            strength=14,
            dexterity=12,
            constitution=13,
            intelligence=10,
            wisdom=11,
            charisma=8,
        )

        # Should have combat stats
        assert hasattr(char, "hit_points")
        assert hasattr(char, "armor_class")
        assert hasattr(char, "strength_mod")
        assert hasattr(char, "dexterity_mod")

    def test_character_ability_modifiers_calculated(self):
        """Test that ability modifiers are calculated correctly."""
        from src.character.character import Character

        char = Character(
            name="Test",
            character_class="fighter",
            race="human",
            strength=16,  # Should be +3
            dexterity=14,  # Should be +2
            constitution=12,  # Should be +1
        )

        assert char.strength_mod == 3
        assert char.dexterity_mod == 2
        assert char.constitution_mod == 1

    def test_character_ac_calculation(self):
        """Test that AC is calculated correctly."""
        from src.character.character import Character

        char = Character(
            name="Test",
            character_class="fighter",
            race="human",
            dexterity=14,  # +2 DEX mod
        )

        # Base AC is 10 + DEX mod
        expected_ac = 10 + 2
        assert char.armor_class == expected_ac


class TestCombatTransitionIntegration:
    """Tests for combat-to-scene transitions."""

    def test_victory_scene_loading(self):
        """Test that victory scenes can be loaded."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Common victory scenes
        victory_scenes = ["goblin_victory", "hero_ending", "act1_conclusion"]

        for scene_id in victory_scenes:
            scene = manager.get_scene(scene_id)
            assert scene is not None, f"Victory scene '{scene_id}' not found"

    def test_defeat_scene_loading(self):
        """Test that defeat scenes can be loaded."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Common defeat scenes
        defeat_scenes = ["death_in_dungeon", "survivor_ending"]

        for scene_id in defeat_scenes:
            scene = manager.get_scene(scene_id)
            assert scene is not None, f"Defeat scene '{scene_id}' not found"

    def test_combat_scene_chain_integrity(self):
        """Test that combat scene chains are complete."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Test goblin encounter chain
        goblin_scene = manager.get_scene("goblin_encounter")
        assert goblin_scene is not None

        # Should have choices leading to combat
        combat_choices = [c for c in goblin_scene.choices if c.combat_encounter]
        assert len(combat_choices) > 0

        # Each combat choice should have victory/defeat navigation
        for choice in combat_choices:
            assert choice.victory_next_scene, f"Choice '{choice.id}' missing victory scene"
            assert choice.defeat_scene, f"Choice '{choice.id}' missing defeat scene"

            # Verify those scenes exist
            assert manager.get_scene(choice.victory_next_scene), (
                f"Victory scene '{choice.victory_next_scene}' not found"
            )
            assert manager.get_scene(choice.defeat_scene), (
                f"Defeat scene '{choice.defeat_scene}' not found"
            )
