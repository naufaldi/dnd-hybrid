"""Scene manager for loading and managing story scenes."""

from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import asdict
import yaml
from ..utils.logger import get_logger
from .models import Scene, Choice, GameState, Consequence, SkillCheck
from ..ai.openrouter_client import OpenRouterClient

logger = get_logger(__name__)


class SceneManager:
    """Manages story scenes and flow."""

    def __init__(self, story_dir: Path, ai_client: Optional[OpenRouterClient] = None):
        self.story_dir = story_dir
        self.ai_client = ai_client
        self.scenes: Dict[str, Scene] = {}
        self._load_scenes()

    def _load_scenes(self) -> None:
        """Load all scene files from the story directory."""
        if not self.story_dir.exists():
            logger.warning(f"Story directory not found: {self.story_dir}")
            return

        for yaml_file in self.story_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, "r") as f:
                    scene_data = yaml.safe_load(f)
                    if scene_data:
                        scene = self._parse_scene(scene_data)
                        self.scenes[scene.id] = scene
                        logger.info(f"Loaded scene: {scene.id}")
            except Exception as e:
                logger.error(f"Error loading scene from {yaml_file}: {e}")

    def _parse_scene(self, data: dict) -> Scene:
        """Parse scene data into Scene object."""
        choices = []
        for choice_data in data.get("choices", []):
            skill_check = None
            if "skill_check" in choice_data:
                sk = choice_data["skill_check"]
                skill_check = SkillCheck(
                    ability=sk["ability"],
                    dc=sk["dc"],
                    success_next_scene=sk.get("success_next_scene", sk.get("next_scene", "")),
                    failure_next_scene=sk.get("failure_next_scene", sk.get("next_scene", "")),
                )

            choice = Choice(
                id=choice_data["id"],
                text=choice_data["text"],
                shortcut=choice_data["shortcut"],
                next_scene=choice_data.get("next_scene", ""),
                skill_check=skill_check,
                consequences=[
                    Consequence(type=c["type"], target=c["target"], value=c.get("value"))
                    for c in choice_data.get("consequences", [])
                ],
                required_flags=choice_data.get("required_flags", {}),
                set_flags=choice_data.get("set_flags", {}),
            )
            choices.append(choice)

        return Scene(
            id=data["id"],
            act=data.get("act", 1),
            title=data.get("title", ""),
            description=data.get("description", ""),
            choices=choices,
            next_scene=data.get("next_scene"),
            flags_required=data.get("flags_required", {}),
            flags_set=data.get("flags_set", {}),
            is_combat=data.get("is_combat", False),
            is_ending=data.get("is_ending", False),
            ending_type=data.get("ending_type"),
            ai_dialogue=data.get("ai_dialogue", False),
            npc_name=data.get("npc_name"),
            npc_mood=data.get("npc_mood"),
        )

    def get_scene(self, scene_id: str) -> Scene:
        """Get scene by ID."""
        if scene_id not in self.scenes:
            raise ValueError(f"Scene not found: {scene_id}")
        return self.scenes[scene_id]

    def has_scene(self, scene_id: str) -> bool:
        """Check if scene exists."""
        return scene_id in self.scenes

    def add_scene(self, scene: Scene) -> None:
        """Add a scene to the manager."""
        self.scenes[scene.id] = scene

    def get_valid_choices(self, scene: Scene, state: GameState) -> List[Choice]:
        """Get choices that are valid given current game state."""
        valid = []
        for choice in scene.choices:
            if not all(state.flags.get(k, False) == v for k, v in choice.required_flags.items()):
                continue
            valid.append(choice)
        return valid

    def apply_flags(self, scene: Scene, state: GameState) -> None:
        """Apply flags set by entering a scene."""
        for flag, value in scene.flags_set.items():
            state.flags[flag] = value

    def get_next_scene(self, choice: Choice) -> str:
        """Get the next scene ID based on a choice."""
        return choice.next_scene

    def apply_choice_consequences(self, choice: Choice, state: GameState) -> None:
        """Apply consequences of a choice to game state."""
        state.choices_made.append(choice.id)

        for consequence in choice.consequences:
            if consequence.type == "flag":
                state.flags[consequence.target] = consequence.value
                logger.debug(f"  Set flag {consequence.target} = {consequence.value}")

            elif consequence.type == "gold":
                if hasattr(state.character, "gold"):
                    current_gold = getattr(state.character, "gold", 0)
                    new_gold = current_gold + consequence.value
                    state.character.gold = max(0, new_gold)
                    logger.debug(f"  Gold change: {current_gold} -> {new_gold}")

            elif consequence.type == "relationship":
                current = state.relationships.get(consequence.target, 0)
                new_value = max(-10, min(10, current + consequence.value))
                state.relationships[consequence.target] = new_value
                logger.debug(f"  Relationship {consequence.target}: {current} -> {new_value}")

            elif consequence.type == "item":
                if consequence.value not in state.inventory:
                    state.inventory.append(consequence.value)
                    logger.debug(f"  Added item: {consequence.value}")

            elif consequence.type == "stat":
                if hasattr(state.character, consequence.target):
                    current = getattr(state.character, consequence.target)
                    setattr(state.character, consequence.target, current + consequence.value)
                    logger.debug(
                        f"  Stat {consequence.target}: {current} -> {current + consequence.value}"
                    )

    async def render_scene(self, scene: Scene, state: GameState) -> str:
        """Render scene with optional AI enhancement."""
        description = scene.description

        if self.ai_client:
            try:
                enhanced = await self.ai_client.enhance_description(
                    description,
                    {
                        "player_class": getattr(state.character, "character_class", "unknown")
                        if state.character
                        else "unknown",
                        "act": state.current_act,
                    },
                )
                if enhanced:
                    description = enhanced
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")

        return description

    def get_scenes_by_act(self, act: int) -> List[Scene]:
        """Get all scenes for a specific act."""
        return [s for s in self.scenes.values() if s.act == act]

    def get_scene_count(self) -> int:
        """Get total number of scenes."""
        return len(self.scenes)
