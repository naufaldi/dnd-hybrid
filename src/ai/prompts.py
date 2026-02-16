"""AI prompt templates for narrative generation."""

from typing import Dict, Any


def build_story_summary(game_state: Dict[str, Any]) -> str:
    """Build a brief story summary from game state for narrative consistency."""
    flags = game_state.get("flags", {})
    choices_made = game_state.get("choices_made", [])[-10:]
    scene_history = game_state.get("scene_history", [])[-7:]
    inventory = game_state.get("inventory", [])
    relationships = game_state.get("relationships", {})

    parts = []
    if scene_history:
        path = " -> ".join(scene_history)
        parts.append(f"Path: {path}")
    if choices_made:
        parts.append(f"Key choices: {', '.join(choices_made)}")
    if flags:
        active = [k for k, v in flags.items() if v]
        if active:
            parts.append(f"Story flags: {', '.join(active)}")
    if inventory:
        parts.append(f"Inventory: {', '.join(inventory[:5])}")
    if relationships:
        notable = [f"{npc}:{val}" for npc, val in list(relationships.items())[:3]]
        parts.append(f"Relationships: {', '.join(notable)}")

    return " | ".join(parts) if parts else "Beginning of adventure"


def build_scene_generation_prompt(
    scene_id: str, context: Dict[str, Any]
) -> str:
    """Build prompt for AI scene generation with full context."""
    char_info = context.get("char_info", "")
    flags_info = context.get("flags_info", "")
    story_summary = context.get("story_summary", "")
    scene_history = context.get("scene_history", "")
    choices_made = context.get("choices_made", "")
    inventory_info = context.get("inventory_info", "")
    relationships_info = context.get("relationships_info", "")
    current_act = context.get("current_act", 2)

    consistency_note = ""
    if story_summary:
        consistency_note = f"""
CRITICAL - Narrative consistency:
Story so far: {story_summary}
Do NOT contradict established facts. Maintain tone and continuity."""

    return f"""Generate a D&D narrative game scene in YAML format.

Scene ID: {scene_id}
{char_info}
{flags_info}
{scene_history}
{choices_made}
{inventory_info}
{relationships_info}
Current act: {current_act}
{consistency_note}

Generate a complete scene with:
- id: {scene_id}
- act: {current_act}
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
act: {current_act}
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


def build_quest_scene_prompt(
    objective: str,
    step_index: int,
    total_steps: int,
    quest_type: str,
    context: Dict[str, Any],
) -> str:
    """Build prompt for procedural quest scene generation."""
    char_info = context.get("char_info", "")
    story_summary = context.get("story_summary", "")

    step_desc = {
        0: "introduction - the quest giver explains the task",
        total_steps - 1: "climax - the objective is achieved, reward given",
    }.get(step_index, f"middle step {step_index + 1} of {total_steps}")

    return f"""Generate a D&D narrative game scene for a procedural quest.

Quest type: {quest_type}
Objective: {objective}
This is step {step_index + 1} of {total_steps}: {step_desc}

{char_info}
{story_summary}

Generate a complete scene in YAML format with:
- id: quest_{objective}_{step_index}
- act: (from context, usually 2)
- title: A fitting title
- description: 3-5 sentences, second person, atmospheric
- choices: 3-4 choices with next_scene IDs

For the final step, one choice should lead to a completion scene (next_scene: quest_complete_{objective}).
For middle steps, choices lead to quest_{objective}_{step_index + 1} or similar.

Generate ONLY valid YAML, no other text:"""


def build_ending_enhancement_prompt(
    base_description: str, game_state: Dict[str, Any]
) -> str:
    """Build prompt for AI-enhanced ending with playthrough-specific details."""
    flags = game_state.get("flags", {})
    choices_made = game_state.get("choices_made", [])
    scene_count = len(game_state.get("scene_history", []))

    active_flags = [k for k, v in flags.items() if v]
    context = f"Flags: {', '.join(active_flags) or 'none'}. "
    context += f"Key choices: {', '.join(choices_made[-5:]) or 'none'}. "
    context += f"Scenes visited: {scene_count}."

    return f"""Enhance this game ending with 1-2 personalized sentences reflecting the player's unique journey.

Base ending:
{base_description}

Playthrough context: {context}

Add 1-2 sentences that reference specific choices or achievements. Keep the original tone. Output ONLY the enhanced ending text, no preamble:"""
