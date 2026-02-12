"""Fallback generic scenarios for common situations."""

from typing import Dict
from .models import Scene, Choice, SkillCheck


class FallbackScenes:
    """Generic fallback scenes for common game situations."""

    @staticmethod
    def get_combat_encounter(enemy_name: str = "Goblin") -> Scene:
        """Generic combat encounter scene."""
        return Scene(
            id="combat_encounter_generic",
            act=1,
            title="Combat Encounter",
            description=f"A {enemy_name} appears! It readies its weapon, eyes fixed on you.",
            choices=[
                Choice(
                    id="fight",
                    text="Engage in combat",
                    shortcut="A",
                    next_scene="combat_resolution",
                    skill_check=SkillCheck(
                        ability="dex",
                        dc=10,
                        success_next_scene="combat_victory",
                        failure_next_scene="combat_damage",
                    ),
                ),
                Choice(
                    id="flee",
                    text="Try to escape",
                    shortcut="B",
                    next_scene="escape_attempt",
                    skill_check=SkillCheck(
                        ability="dex",
                        dc=12,
                        success_next_scene="escaped",
                        failure_next_scene="combat_trapped",
                    ),
                ),
            ],
            is_combat=True,
            required_mechanics=[],  # No special mechanics required
        )

    @staticmethod
    def get_exploration_scene() -> Scene:
        """Generic exploration scene."""
        return Scene(
            id="exploration_generic",
            act=1,
            title="Exploration",
            description="You find yourself in a dimly lit area. Something glints in the shadows ahead.",
            choices=[
                Choice(
                    id="investigate",
                    text="Investigate the area",
                    shortcut="A",
                    next_scene="investigation_result",
                    skill_check=SkillCheck(
                        ability="wis",
                        dc=10,
                        success_next_scene="found_treasure",
                        failure_next_scene="nothing_found",
                    ),
                ),
                Choice(
                    id="continue_on",
                    text="Continue forward cautiously",
                    shortcut="B",
                    next_scene="next_area",
                ),
            ],
            required_mechanics=[],
        )

    @staticmethod
    def get_puzzle_scene(puzzle_type: str = "door") -> Scene:
        """Generic puzzle scene."""
        descriptions = {
            "door": "A heavy door blocks your path. It has a complex lock mechanism.",
            "trap": "You notice subtle signs of a mechanical trap nearby.",
            "riddle": "An ancient inscription on the wall presents a riddle.",
        }
        desc = descriptions.get(puzzle_type, descriptions["door"])

        return Scene(
            id="puzzle_generic",
            act=1,
            title="Puzzle Challenge",
            description=desc,
            choices=[
                Choice(
                    id="solve",
                    text="Attempt to solve it",
                    shortcut="A",
                    next_scene="puzzle_result",
                    skill_check=SkillCheck(
                        ability="int",
                        dc=12,
                        success_next_scene="puzzle_solved",
                        failure_next_scene="puzzle_failed",
                    ),
                ),
                Choice(
                    id="skip",
                    text="Look for another way",
                    shortcut="B",
                    next_scene="alternative_path",
                ),
            ],
            required_mechanics=[],
        )

    @staticmethod
    def get_dialogue_scene(npc_name: str = "Mysterious Figure") -> Scene:
        """Generic dialogue scene."""
        return Scene(
            id="dialogue_generic",
            act=1,
            title=f"Conversation with {npc_name}",
            description=f"{npc_name} regards you with keen interest. 'What brings you here?' they ask.",
            choices=[
                Choice(
                    id="honest",
                    text="Tell them the truth",
                    shortcut="A",
                    next_scene="dialogue_result",
                    skill_check=SkillCheck(
                        ability="cha",
                        dc=10,
                        success_next_scene="npc_friendly",
                        failure_next_scene="npc_suspicious",
                    ),
                ),
                Choice(
                    id="deceptive",
                    text="Lie to them",
                    shortcut="B",
                    next_scene="dialogue_result",
                    skill_check=SkillCheck(
                        ability="cha",
                        dc=14,
                        success_next_scene="npc_believed",
                        failure_next_scene="npc_angered",
                    ),
                ),
                Choice(
                    id="leave",
                    text="Leave the conversation",
                    shortcut="C",
                    next_scene="left_conversation",
                ),
            ],
            npc_name=npc_name,
            npc_mood="neutral",
            required_mechanics=[],
        )

    @staticmethod
    def get_trap_scene() -> Scene:
        """Generic trap scene."""
        return Scene(
            id="trap_generic",
            act=1,
            title="Trap Detected",
            description="You notice subtle signs of a mechanical trap - a tripwire, pressure plate, or suspicious floor tiles.",
            choices=[
                Choice(
                    id="disarm",
                    text="Attempt to disarm the trap",
                    shortcut="A",
                    next_scene="trap_result",
                    skill_check=SkillCheck(
                        ability="dex",
                        dc=12,
                        success_next_scene="trap_disarmed",
                        failure_next_scene="trap_triggered",
                    ),
                ),
                Choice(
                    id="avoid",
                    text="Carefully avoid it",
                    shortcut="B",
                    next_scene="trap_result",
                    skill_check=SkillCheck(
                        ability="dex",
                        dc=10,
                        success_next_scene="trap_avoided",
                        failure_next_scene="trap_triggered",
                    ),
                ),
                Choice(
                    id="ignore",
                    text="Walk through anyway",
                    shortcut="C",
                    next_scene="trap_triggered",
                ),
            ],
            required_mechanics=[],
        )

    @staticmethod
    def get_rest_scene() -> Scene:
        """Generic rest/encampment scene."""
        return Scene(
            id="rest_generic",
            act=1,
            title="Resting Spot",
            description="You find a relatively safe spot to rest. The journey has been exhausting.",
            choices=[
                Choice(
                    id="short_rest",
                    text="Take a short rest (1 hour)",
                    shortcut="A",
                    next_scene="rest_complete",
                ),
                Choice(
                    id="long_rest",
                    text="Take a long rest (8 hours)",
                    shortcut="B",
                    next_scene="long_rest_complete",
                ),
                Choice(
                    id="keep_watching",
                    text="Rest while keeping watch",
                    shortcut="C",
                    next_scene="watch_complete",
                ),
            ],
            required_mechanics=[],
        )

    @staticmethod
    def get_error_scene(error_message: str) -> Scene:
        """Generic error/scene not found scene."""
        return Scene(
            id="scene_not_found",
            act=1,
            title="Scene Not Available",
            description=f"The intended scene could not be loaded. {error_message}. Using a generic fallback.",
            choices=[
                Choice(
                    id="continue",
                    text="Continue forward",
                    shortcut="A",
                    next_scene="exploration_generic",
                ),
                Choice(
                    id="restart",
                    text="Return to known location",
                    shortcut="B",
                    next_scene="start",
                ),
            ],
            required_mechanics=[],
        )


# Registry of fallback scenes by type
FALLBACK_SCENES: Dict[str, callable] = {
    "combat": FallbackScenes.get_combat_encounter,
    "exploration": FallbackScenes.get_exploration_scene,
    "puzzle": FallbackScenes.get_puzzle_scene,
    "dialogue": FallbackScenes.get_dialogue_scene,
    "trap": FallbackScenes.get_trap_scene,
    "rest": FallbackScenes.get_rest_scene,
}


def get_fallback_scene(scene_type: str = "exploration", **kwargs) -> Scene:
    """
    Get a fallback scene for a given type.

    Args:
        scene_type: Type of scene (combat, exploration, puzzle, dialogue, trap, rest)
        **kwargs: Additional parameters for the scene (e.g., enemy_name, npc_name)

    Returns:
        A Scene object with generic content
    """
    factory = FALLBACK_SCENES.get(scene_type, FallbackScenes.get_exploration_scene)
    return factory(**kwargs)
