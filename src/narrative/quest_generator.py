"""Procedural quest generation for AI-driven side quests."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .scene_manager import SceneManager
import yaml

from ..utils.logger import get_logger
from .models import Scene, Choice, GameState, SkillCheck
from .validators import validate_scene
from ..ai.openrouter_client import OpenRouterClient
from ..ai.prompts import build_story_summary, build_quest_scene_prompt

logger = get_logger(__name__)


@dataclass
class QuestTemplate:
    """Template for procedural quest generation."""

    quest_type: str  # fetch, defeat, deliver
    objective: str
    reward_type: str  # gold, item, reputation
    num_scenes: int = 4


@dataclass
class Quest:
    """Active procedural quest."""

    template: QuestTemplate
    scenes: List[Scene] = field(default_factory=list)
    current_step: int = 0


QUEST_TEMPLATES: Dict[str, QuestTemplate] = {
    "fetch_artifact": QuestTemplate(
        quest_type="fetch",
        objective="ancient artifact",
        reward_type="reputation",
        num_scenes=4,
    ),
    "fetch_item": QuestTemplate(
        quest_type="fetch",
        objective="rare item",
        reward_type="gold",
        num_scenes=3,
    ),
    "defeat_enemy": QuestTemplate(
        quest_type="defeat",
        objective="bandit leader",
        reward_type="gold",
        num_scenes=4,
    ),
    "deliver_message": QuestTemplate(
        quest_type="deliver",
        objective="urgent message",
        reward_type="reputation",
        num_scenes=3,
    ),
    "seal_quest": QuestTemplate(
        quest_type="fetch",
        objective="seal artifacts",
        reward_type="reputation",
        num_scenes=5,
    ),
}


class QuestGenerator:
    """Generates procedural quest scene chains via AI."""

    def __init__(
        self,
        ai_client: Optional[OpenRouterClient] = None,
    ):
        self.ai_client = ai_client

    async def generate_quest(
        self,
        template: QuestTemplate,
        game_state: Optional[GameState],
        scene_manager: "SceneManager",
    ) -> List[Scene]:
        """Generate a quest scene chain and register with scene manager."""
        if not self.ai_client:
            return []

        scenes: List[Scene] = []
        quest_id = template.objective.replace(" ", "_")[:20]

        ctx = {
            "char_info": "",
            "story_summary": "",
        }
        if game_state:
            if game_state.character:
                c = game_state.character
                ctx["char_info"] = (
                    f"Player: {c.name} the {c.race} {c.character_class}"
                )
            ctx["story_summary"] = build_story_summary(
                {
                    "flags": game_state.flags,
                    "choices_made": game_state.choices_made,
                    "scene_history": game_state.scene_history,
                    "inventory": game_state.inventory,
                    "relationships": game_state.relationships,
                }
            )

        for i in range(template.num_scenes):
            scene_id = f"quest_{quest_id}_{i}"
            prompt = build_quest_scene_prompt(
                template.objective,
                i,
                template.num_scenes,
                template.quest_type,
                ctx,
            )
            try:
                import asyncio

                response = await asyncio.wait_for(
                    self.ai_client.generate(
                        prompt=prompt, max_tokens=600, temperature=0.8
                    ),
                    timeout=10.0,
                )
                if response:
                    scene_data = yaml.safe_load(response)
                    if scene_data and isinstance(scene_data, dict):
                        scene = self._parse_quest_scene(
                            scene_data, scene_id, quest_id, i
                        )
                        if scene:
                            is_valid, errors = validate_scene(scene)
                            if is_valid:
                                scenes.append(scene)
                                scene_manager.add_ai_scene(scene)
                            else:
                                logger.warning(
                                    f"Quest scene {scene_id} invalid: {errors}"
                                )
            except Exception as e:
                logger.warning(f"Quest scene generation failed: {e}")

        return scenes

    def _parse_quest_scene(
        self, data: dict, scene_id: str, quest_id: str, step: int
    ) -> Optional[Scene]:
        """Parse AI response into Scene."""
        choices = []
        for i, c in enumerate(data.get("choices", [])):
            skill_check = None
            if "skill_check" in c:
                sk = c["skill_check"]
                skill_check = SkillCheck(
                    ability=sk.get("ability", "str"),
                    dc=sk.get("dc", 10),
                    success_next_scene=sk.get(
                        "success_next_scene", c.get("next_scene", "")
                    ),
                    failure_next_scene=sk.get(
                        "failure_next_scene", c.get("next_scene", "")
                    ),
                )
            next_scene = c.get("next_scene", "")
            if step == 0 and not next_scene:
                next_scene = f"quest_{quest_id}_1"
            elif step > 0 and not next_scene:
                next_scene = f"quest_complete_{quest_id}"
            choices.append(
                Choice(
                    id=c.get("id", f"choice_{i}"),
                    text=c.get("text", "Continue"),
                    shortcut=c.get("shortcut", "ABCD"[i % 4]),
                    next_scene=next_scene,
                    skill_check=skill_check,
                )
            )
        return Scene(
            id=data.get("id", scene_id),
            act=data.get("act", 2),
            title=data.get("title", "Quest"),
            description=data.get("description", ""),
            choices=choices,
            flags_set=data.get("flags_set", {}),
            is_ai_generated=True,
        )
