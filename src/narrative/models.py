"""Data models for the narrative system."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Consequence:
    """Represents a consequence of a choice."""

    type: str  # "stat", "item", "flag", "relationship", "gold"
    target: str  # What it affects
    value: Any  # How much/effect


@dataclass
class SkillCheck:
    """Represents an optional skill check."""

    ability: str  # "str", "dex", "con", "int", "wis", "cha"
    dc: int  # Difficulty Class
    success_next_scene: str  # Scene on success
    failure_next_scene: str  # Scene on failure


@dataclass
class Choice:
    """Represents a player choice in a scene."""

    id: str
    text: str
    shortcut: str  # Keyboard shortcut (A, B, C, D)
    next_scene: str
    consequences: List[Consequence] = field(default_factory=list)
    skill_check: Optional[SkillCheck] = None
    required_flags: Dict[str, bool] = field(default_factory=dict)
    set_flags: Dict[str, bool] = field(default_factory=dict)


@dataclass
class Scene:
    """Represents a story scene."""

    id: str
    act: int
    title: str
    description: str
    choices: List[Choice] = field(default_factory=list)
    next_scene: Optional[str] = None
    flags_required: Dict[str, bool] = field(default_factory=dict)
    flags_set: Dict[str, bool] = field(default_factory=dict)
    is_combat: bool = False
    is_ending: bool = False
    ending_type: Optional[str] = None
    ai_dialogue: bool = False
    npc_name: Optional[str] = None
    npc_mood: Optional[str] = None


@dataclass
class DiceRollResult:
    """Represents the result of a dice roll."""

    dice_type: str  # "d20", "d6", etc.
    rolls: List[int]
    modifier: int
    total: int
    natural: Optional[int] = None
    is_critical: bool = False
    is_fumble: bool = False


@dataclass
class GameState:
    """Represents the current game state."""

    character: Any  # Character object
    current_scene: str = "start"
    scene_history: List[str] = field(default_factory=list)
    choices_made: List[str] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)
    relationships: Dict[str, int] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    current_act: int = 1
    is_combat: bool = False
    ending_determined: Optional[str] = None
    turns_spent: int = 0


@dataclass
class Ending:
    """Represents a game ending."""

    id: str
    title: str
    description: str
    requirements: Dict[str, Any] = field(default_factory=dict)
