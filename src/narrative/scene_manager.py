"""Scene manager for loading and managing story scenes."""

from pathlib import Path
from typing import Dict, Optional, List
import yaml
from ..utils.logger import get_logger
from .models import Scene, Choice, GameState, Consequence, SkillCheck
from .validators import validate_scene
from .fallbacks import get_fallback_scene
from ..ai.openrouter_client import OpenRouterClient

logger = get_logger(__name__)


class SceneManager:
    """Manages story scenes and flow."""

    def __init__(self, story_dir: Path, ai_client: Optional[OpenRouterClient] = None):
        self.story_dir = story_dir
        self.ai_client = ai_client
        self.scenes: Dict[str, Scene] = {}
        self.ai_scene_cache: Dict[str, Scene] = {}  # Cache for AI-generated scenes
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
                        scene = self._parse_scene(scene_data, str(yaml_file))
                        self.scenes[scene.id] = scene
                        logger.info(f"Loaded scene: {scene.id}")
            except Exception as e:
                logger.error(f"Error loading scene from {yaml_file}: {e}")

    def _parse_scene(self, data: dict, source_path: str = None) -> Scene:
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
                required_mechanics=choice_data.get("required_mechanics", []),
                combat_encounter=choice_data.get("combat_encounter"),
                victory_next_scene=choice_data.get("victory_next_scene"),
                defeat_scene=choice_data.get("defeat_scene"),
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
            required_mechanics=data.get("required_mechanics", []),
            is_ai_generated=False,  # YAML scenes are manual
            source_file=source_path,
        )

    def get_scene(self, scene_id: str) -> Scene:
        """
        Get scene by ID with fallback support (sync version).

        Tries in order:
        1. Manual scenes (YAML files)
        2. AI-generated scenes (cached)
        3. Fallback generic scenes

        Note: For AI generation with game state context, use get_scene_async()
        """
        # 1. Try manual scenes first
        if scene_id in self.scenes:
            return self.scenes[scene_id]

        # 2. Try AI-generated scenes cache
        if scene_id in self.ai_scene_cache:
            scene = self.ai_scene_cache[scene_id]
            # Validate before returning
            is_valid, errors = validate_scene(scene)
            if is_valid:
                return scene
            else:
                logger.warning(f"AI scene '{scene_id}' has invalid mechanics: {errors}")
                # Remove invalid scene from cache
                del self.ai_scene_cache[scene_id]

        # 3. Try to generate with AI (sync - no game state)
        if self.ai_client:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't await in sync context, will use fallback
                    pass
                else:
                    ai_scene = loop.run_until_complete(self._generate_ai_scene(scene_id))
                    if ai_scene:
                        is_valid, errors = validate_scene(ai_scene)
                        if is_valid:
                            self.ai_scene_cache[scene_id] = ai_scene
                            return ai_scene
            except Exception:
                pass

        # 4. Fallback to generic scene
        return self._get_fallback_for_scene(scene_id)

    async def get_scene_async(self, scene_id: str, game_state: Optional[GameState] = None) -> Scene:
        """
        Get scene by ID with AI generation (async version with game state).

        This method can generate scenes dynamically using AI when no static
        scene exists, using the game state for context-aware generation.

        Args:
            scene_id: The scene ID to retrieve
            game_state: Current game state for context

        Returns:
            The Scene object
        """
        # 1. Try manual scenes first
        if scene_id in self.scenes:
            return self.scenes[scene_id]

        # 2. Try AI-generated scenes cache
        if scene_id in self.ai_scene_cache:
            scene = self.ai_scene_cache[scene_id]
            is_valid, errors = validate_scene(scene)
            if is_valid:
                return scene
            else:
                del self.ai_scene_cache[scene_id]

        # 3. Try to generate with AI (async with game state)
        if self.ai_client:
            ai_scene = await self._generate_ai_scene(scene_id, game_state)
            if ai_scene:
                is_valid, errors = validate_scene(ai_scene)
                if is_valid:
                    self.ai_scene_cache[scene_id] = ai_scene
                    return ai_scene
                else:
                    logger.warning(f"Generated AI scene '{scene_id}' has invalid mechanics: {errors}")

        # 4. Fallback to generic scene
        return self._get_fallback_for_scene(scene_id)

    def _get_fallback_for_scene(self, scene_id: str) -> Scene:
        """Get a fallback scene based on scene_id naming."""
        # Try to infer scene type from ID
        scene_type = "exploration"  # Default

        if "combat" in scene_id.lower():
            scene_type = "combat"
        elif "puzzle" in scene_id.lower() or "door" in scene_id.lower():
            scene_type = "puzzle"
        elif "dialogue" in scene_id.lower() or "talk" in scene_id.lower():
            scene_type = "dialogue"
        elif "trap" in scene_id.lower():
            scene_type = "trap"
        elif "rest" in scene_id.lower():
            scene_type = "rest"

        logger.info(f"Using fallback scene for: {scene_id} (type: {scene_type})")
        return get_fallback_scene(scene_type)

    async def _generate_ai_scene(self, scene_id: str, game_state: Optional[GameState] = None) -> Optional[Scene]:
        """Generate a scene using AI when no static scene exists.

        This enables dynamic story generation - when a player reaches a
        dead end or takes an unexpected path, AI generates a new scene.

        Args:
            scene_id: The requested scene ID
            game_state: Current game state for context (optional)

        Returns:
            Generated Scene or None if generation fails
        """
        if not self.ai_client:
            return None

        logger.info(f"AI generating scene for: {scene_id}")

        # Build context for the AI
        char_info = ""
        flags_info = ""
        if game_state and game_state.character:
            char = game_state.character
            char_info = f"Player: {char.name} the {char.race} {char.character_class} (HP: {char.hit_points})"
        if game_state and game_state.flags:
            flags_info = f"Story progress: {', '.join([k for k, v in game_state.flags.items() if v])}"

        prompt = f"""Generate a D&D narrative game scene in YAML format.

Scene ID: {scene_id}
{char_info}
{flags_info}

Generate a complete scene with:
- id: {scene_id}
- act: 2 (this is Act 2)
- title: A fitting title
- description: 3-5 sentences of atmospheric narrative in second person ("You see...", "You hear...")
- choices: 3-4 choices with different approaches (combat, diplomatic, stealth, exploration)
- Each choice should have a unique next_scene ID that continues the story

The tone should be:
- Atmospheric and immersive
- Present tense, second person
- Mix of danger and opportunity
- Logical story progression

Format as clean YAML. Include flags_set if appropriate.

Example format:
```yaml
id: {scene_id}
act: 2
title: "Your Scene Title"
description: |
  Narrative description here. Present tense, second person.
choices:
  - id: choice_1
    text: "First choice description"
    shortcut: A
    next_scene: scene_id_for_choice_1
  - id: choice_2
    text: "Second choice"
    shortcut: B
    next_scene: another_scene_id
flags_set:
  visited_generated_scene: true
```

Generate ONLY the YAML, no other text:"""

        try:
            import asyncio
            response = await asyncio.wait_for(
                self.ai_client.generate(prompt=prompt, max_tokens=800, temperature=0.8),
                timeout=10.0
            )

            if response:
                # Parse YAML response into Scene object
                scene_data = yaml.safe_load(response)
                if scene_data and isinstance(scene_data, dict):
                    # Create Scene from parsed data
                    choices = []
                    for choice_data in scene_data.get("choices", []):
                        skill_check = None
                        if "skill_check" in choice_data:
                            sk = choice_data["skill_check"]
                            skill_check = SkillCheck(
                                ability=sk.get("ability", "str"),
                                dc=sk.get("dc", 10),
                                success_next_scene=sk.get("success_next_scene", choice_data.get("next_scene", "")),
                                failure_next_scene=sk.get("failure_next_scene", choice_data.get("next_scene", ""))
                            )

                        choice = Choice(
                            id=choice_data.get("id", ""),
                            text=choice_data.get("text", ""),
                            shortcut=choice_data.get("shortcut", "A"),
                            next_scene=choice_data.get("next_scene", ""),
                            skill_check=skill_check
                        )
                        choices.append(choice)

                    scene = Scene(
                        id=scene_data.get("id", scene_id),
                        act=scene_data.get("act", 2),
                        title=scene_data.get("title", "Untitled"),
                        description=scene_data.get("description", ""),
                        choices=choices,
                        flags_set=scene_data.get("flags_set", {})
                    )

                    logger.info(f"AI successfully generated scene: {scene_id}")
                    return scene

        except Exception as e:
            logger.warning(f"AI scene generation failed for {scene_id}: {e}")

        return None

    def add_ai_scene(self, scene: Scene) -> None:
        """Add an AI-generated scene to the cache."""
        is_valid, errors = validate_scene(scene)
        if is_valid:
            scene.is_ai_generated = True
            self.ai_scene_cache[scene.id] = scene
            logger.info(f"Added AI scene to cache: {scene.id}")
        else:
            logger.warning(f"Refused to add invalid AI scene: {errors}")

    def has_scene(self, scene_id: str) -> bool:
        """Check if scene exists (manual or AI cached)."""
        return scene_id in self.scenes or scene_id in self.ai_scene_cache

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
