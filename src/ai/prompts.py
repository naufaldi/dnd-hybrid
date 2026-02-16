"""AI prompt templates for narrative generation."""

from typing import Dict, Any


def build_scene_enhancement_prompt(template: str, context: Dict[str, Any]) -> str:
    """Build prompt for enhancing scene description."""
    player_class = context.get("player_class", "unknown")
    act = context.get("act", 1)
    return f"""Enhance this scene description for a D&D interactive fiction game.
Keep the core facts and tone. Add 2-3 sentences of atmospheric detail.

Base description:
{template}

Context:
- Player class: {player_class}
- Current act: {act}

Enhanced description:"""


def build_dialogue_prompt(
    npc_name: str,
    mood: str,
    context: str,
    dialogue_type: str = "greeting",
) -> str:
    """Build prompt for NPC dialogue generation."""
    return f"""Generate a brief, atmospheric dialogue response for a D&D NPC.

NPC: {npc_name}
Mood: {mood} (enigmatic/hostile/neutral/friendly/curious)
Type: {dialogue_type} (greeting/response/question/threat/promise)
Context: {context}

Requirements:
- 1-2 sentences maximum
- Match the mood exactly
- No action descriptions, just spoken words
- Use evocative, mysterious language

Dialogue:"""


def build_outcome_prompt(
    action: str,
    roll_result: int,
    dc: int,
    success: bool,
) -> str:
    """Build prompt for skill check outcome narration."""
    result_str = "SUCCESS" if success else "FAILURE"
    return f"""Generate a 1-2 sentence narrative description of what happens when:
Action: {action}
Roll: {roll_result}
Difficulty: {dc}
Result: {result_str}

Narrative:"""


def build_choices_prompt(
    scene_context: str,
    character_info: Dict[str, Any],
    story_flags: Dict[str, bool],
    num_choices: int = 2,
) -> str:
    """Build prompt for dynamic choice generation."""
    char_desc = (
        f"{character_info.get('name', 'Hero')} the "
        f"{character_info.get('race', '')} {character_info.get('class', '')}"
    )
    story_progress = (
        ", ".join(k for k, v in story_flags.items() if v) if story_flags else "Beginning"
    )
    char_class = character_info.get("class", "adventurer")

    return f"""Generate {num_choices} creative story choices for a D&D narrative game.

Current Scene: {scene_context}
Player: {char_desc}
Story Progress: {story_progress}

Generate choices that:
- Are in character for a {char_class}
- Have different approaches (combat, diplomatic, stealth, etc.)
- Are thematically appropriate for a D&D adventure
- Lead to interesting story developments

For each choice, provide:
1. A short descriptive text (10-20 words)
2. The approach type: combat, diplomatic, stealth, exploration, or clever

Format your response as a JSON list like:
[
  {{"text": "Choice description", "approach": "stealth"}},
  {{"text": "Another choice", "approach": "diplomatic"}}
]

Only output the JSON, no other text:"""
