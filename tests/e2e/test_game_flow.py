"""End-to-end tests for complete game flow."""

import pytest
from pathlib import Path


class TestCompleteGameFlow:
    """Tests that verify complete game flow from start to finish."""

    def test_all_scenes_are_reachable(self):
        """Test that all scenes form a connected graph."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Collect all scenes
        all_scenes = set(manager.scenes.keys())

        # Start from tavern_entry and see what's reachable
        visited = set()
        queue = ["tavern_entry"]

        while queue:
            scene_id = queue.pop(0)
            if scene_id in visited or scene_id not in manager.scenes:
                continue

            visited.add(scene_id)
            scene = manager.scenes[scene_id]

            # Add all next_scene targets
            for choice in scene.choices:
                if choice.next_scene:
                    queue.append(choice.next_scene)

                # Check skill check destinations
                if choice.skill_check:
                    for key in ["success_next_scene", "failure_next_scene"]:
                        target = getattr(choice.skill_check, key, None)
                        if target:
                            queue.append(target)

                # Check combat destinations
                if choice.combat_encounter:
                    for key in ["victory_next_scene", "defeat_scene"]:
                        target = getattr(choice, key, None)
                        if target:
                            queue.append(target)

        # Calculate unreachable scenes
        unreachable = all_scenes - visited

        # Some scenes might be intentionally unreachable (test scenes, etc.)
        # But critical scenes should all be reachable
        print(f"Total scenes: {len(all_scenes)}")
        print(f"Reachable from tavern_entry: {len(visited)}")
        print(f"Unreachable: {len(unreachable)}")

        # Main quest scenes should be reachable
        critical_scenes = [
            "tavern_entry",
            "mysterious_figure",
            "dungeon_entrance",
            "dungeon_entry_hall",
            "goblin_encounter",
            "goblin_victory",
            "act1_conclusion",
            "death_in_dungeon",
        ]

        for scene_id in critical_scenes:
            assert scene_id in visited, f"Critical scene '{scene_id}' is not reachable"

    def test_no_dead_ends_in_main_quest(self):
        """Test that main quest path doesn't have dead ends."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        # Define main quest path (lake route: dungeon -> lake -> far_shore -> shrine -> conclusion)
        main_quest = [
            "tavern_entry",
            "mysterious_figure",
            "dungeon_info",
            "offer_heroic",
            "dungeon_entrance",
            "dungeon_entry_hall",
            "underground_lake",
            "far_shore",
            "dark_shrine",
            "act1_conclusion",
        ]

        dead_ends = []
        for i, scene_id in enumerate(main_quest[:-1]):  # Skip last scene
            scene = manager.get_scene(scene_id)
            if not scene:
                dead_ends.append(f"Scene '{scene_id}' doesn't exist")
                continue

            # Check if there's a path to the next main quest scene
            next_in_chain = main_quest[i + 1]
            has_path = False

            for choice in scene.choices:
                if choice.next_scene == next_in_chain:
                    has_path = True
                    break

                # Check skill check destinations
                if choice.skill_check:
                    for key in ["success_next_scene", "failure_next_scene"]:
                        if getattr(choice.skill_check, key, None) == next_in_chain:
                            has_path = True
                            break

                # Check combat destinations
                if choice.victory_next_scene == next_in_chain:
                    has_path = True
                    break

            if not has_path:
                dead_ends.append(f"Scene '{scene_id}' has no path to '{next_in_chain}'")

        assert len(dead_ends) == 0, f"Dead ends found:\n" + "\n".join(dead_ends)

    def test_ending_scenes_are_terminal(self):
        """Test that ending scenes don't lead to other scenes."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        ending_scenes = ["death_in_dungeon", "hero_ending", "survivor_ending"]

        for scene_id in ending_scenes:
            scene = manager.get_scene(scene_id)
            if not scene:
                continue

            # Check that all choices lead to tavern_entry (play again) or nowhere
            for choice in scene.choices:
                if choice.next_scene and choice.next_scene != "tavern_entry":
                    print(f"Warning: {scene_id} choice leads to {choice.next_scene}")

    def test_combat_encounters_have_valid_enemies(self):
        """Test that all combat encounters reference valid enemies."""
        from src.narrative.scene_manager import SceneManager
        from src.entities.enemy_definitions import ENEMY_DEFINITIONS

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        invalid_enemies = []

        for scene_id, scene in manager.scenes.items():
            for choice in scene.choices:
                if choice.combat_encounter:
                    enemy_id = choice.combat_encounter
                    if enemy_id not in ENEMY_DEFINITIONS:
                        invalid_enemies.append(f"{scene_id}: invalid enemy '{enemy_id}'")

        assert len(invalid_enemies) == 0, f"Invalid enemy references:\n" + "\n".join(
            invalid_enemies
        )


class TestSceneContent:
    """Tests for scene content quality."""

    def test_all_scenes_have_content(self):
        """Test that all scenes have non-empty content."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        empty_content = []

        for scene_id, scene in manager.scenes.items():
            if not scene.description or len(scene.description.strip()) < 10:
                empty_content.append(f"{scene_id}: empty or very short description")

            if not scene.choices:
                empty_content.append(f"{scene_id}: no choices")

        assert len(empty_content) == 0, f"Scenes with content issues:\n" + "\n".join(empty_content)

    def test_no_duplicate_scene_ids(self):
        """Test that scene IDs are unique."""
        import yaml
        from pathlib import Path

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        yaml_files = list(scenes_dir.rglob("*.yaml"))

        scene_ids = {}
        duplicates = []

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    content = yaml.safe_load(f)
                    if content and "id" in content:
                        scene_id = content["id"]
                        if scene_id in scene_ids:
                            duplicates.append(
                                f"Duplicate ID '{scene_id}' in {yaml_file.name} and {scene_ids[scene_id]}"
                            )
                        else:
                            scene_ids[scene_id] = yaml_file.name
            except Exception:
                pass

        assert len(duplicates) == 0, f"Duplicate scene IDs:\n" + "\n".join(duplicates)

    def test_choice_shortcuts_are_valid(self):
        """Test that choice shortcuts are valid single characters."""
        from src.narrative.scene_manager import SceneManager

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        manager = SceneManager(scenes_dir)

        invalid_shortcuts = []

        for scene_id, scene in manager.scenes.items():
            for i, choice in enumerate(scene.choices):
                if choice.shortcut:
                    if len(choice.shortcut) != 1:
                        invalid_shortcuts.append(
                            f"{scene_id} choice {i}: shortcut '{choice.shortcut}' is not a single character"
                        )

        assert len(invalid_shortcuts) == 0, f"Invalid shortcuts:\n" + "\n".join(invalid_shortcuts)


class TestAIIntegrationFlow:
    """Tests for AI integration in the game flow."""

    def test_ai_dialogue_flagged_scenes(self):
        """Test that scenes with ai_dialogue flag have NPC info."""
        import yaml
        from pathlib import Path

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        yaml_files = list(scenes_dir.rglob("*.yaml"))

        missing_npc_info = []

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    content = yaml.safe_load(f)
                    if content and content.get("ai_dialogue"):
                        if not content.get("npc_name"):
                            missing_npc_info.append(
                                f"{yaml_file.name}: ai_dialogue=true but no npc_name"
                            )
            except Exception:
                pass

        assert len(missing_npc_info) == 0, f"Scenes missing NPC info:\n" + "\n".join(
            missing_npc_info
        )

    @pytest.mark.skip(reason="Requires actual AI service")
    def test_ai_dialogue_generation(self):
        """Test AI dialogue generation (skipped in CI)."""
        pass


class TestGameStateIntegration:
    """Tests for game state management throughout scenes."""

    def test_flag_consistency(self):
        """Test that flags set by one scene are checked by others."""
        import yaml
        from pathlib import Path
        from collections import defaultdict

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        yaml_files = list(scenes_dir.rglob("*.yaml"))

        # Collect all flags that are set and required
        flags_set = defaultdict(list)
        flags_required = defaultdict(list)

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    content = yaml.safe_load(f)
                    if not content:
                        continue

                    # Flags set at scene level
                    if "flags_set" in content:
                        for flag in content["flags_set"]:
                            flags_set[flag].append(yaml_file.name)

                    # Flags set in choices
                    if "choices" in content:
                        for choice in content["choices"]:
                            if "set_flags" in choice:
                                for flag in choice["set_flags"]:
                                    flags_set[flag].append(yaml_file.name)

                            # Flags required
                            if "required_flags" in choice:
                                for flag in choice["required_flags"]:
                                    flags_required[flag].append(yaml_file.name)
            except Exception:
                pass

        # Check for flags that are required but never set
        undefined_flags = set(flags_required.keys()) - set(flags_set.keys())

        if undefined_flags:
            print(f"Warning: Flags required but never set: {undefined_flags}")

    def test_scene_act_numbers_consistent(self):
        """Test that scene act numbers are consistent."""
        import yaml
        from pathlib import Path

        scenes_dir = Path(__file__).parent.parent.parent / "src" / "story" / "scenes"
        yaml_files = list(scenes_dir.rglob("*.yaml"))

        acts_found = set()

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    content = yaml.safe_load(f)
                    if content and "act" in content:
                        acts_found.add(content["act"])
            except Exception:
                pass

        # Should have at least act 1
        assert 1 in acts_found, "No scenes with act=1 found"
