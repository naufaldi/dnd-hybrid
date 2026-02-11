# Request for Comments (RFC)

## AI Dungeon Chronicles - Technical Design

**RFC Number:** 002  
**Status:** Draft  
**Created:** 2026-02-10  
**Updated:** 2026-02-11

---

## 1. Overview

This RFC describes the technical architecture for a Narrative D&D Interactive Fiction game with AI integration. The implementation transforms the original roguelike into a text-based adventure where players make meaningful choices that shape the story, experience explicit dice rolling with ASCII visuals, and encounter AI-generated narratives.

**Design Approach:** BG3-style feel in terminal—dice drama (animated rolls), choice weight (NPC relationships, flags), narrative flow (rich prose, scene transitions). See [docs/PRD.md](docs/PRD.md) User Stories and Appendix B for screen layouts.

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      TUI Layer (Simplified)                 │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Text Display   │  │  Choice Input   │                  │
│  │  (Narrative)     │  │  (A/B/C/D)      │                  │
│  └─────────────────┘  └─────────────────┘                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Narrative Engine                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Scene Manager  │  │  Choice System  │  │ Ending Mgr │  │
│  │  (Flow control)  │  │ (Selection/Diff)│  │(Tracking)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Integration                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ OpenRouter Client│  │  Prompt Manager │                  │
│  │  (API calls)    │  │  (Templates)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└────────────────────────────┬────────────────────────────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    D&D Core     │  │   Character     │  │   Persistence   │
│  (Dice/Combat)  │  │   Manager      │  │    (Saves)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 3. Module Structure

```
src/
├── main.py                      # Entry point
│
├── narrative/                   # NEW: Story engine
│   ├── __init__.py
│   ├── scene_manager.py         # Load/render scenes, handle flow
│   ├── choice_system.py         # Present choices, track consequences
│   ├── ending_manager.py        # Track flags, determine endings
│   └── scene_loader.py         # Load scene data from YAML/JSON
│
├── ai/                         # NEW: AI integration
│   ├── __init__.py
│   ├── openrouter_client.py     # OpenRouter API wrapper
│   ├── prompts.py              # System/user prompts
│   ├── narrative_generator.py   # Generate dynamic content
│   └── fallback.py             # Template fallbacks
│
├── combat/                     # KEEP: Combat mechanics
│   ├── __init__.py
│   ├── dice.py                 # Dice rolling mechanics
│   ├── dice_display.py         # ASCII visualization
│   ├── combat_resolver.py      # Combat outcomes
│   └── narrator.py             # Narrative combat descriptions
│
├── character/                  # KEEP: Character system
│   ├── __init__.py
│   ├── attributes.py           # 6 attributes, modifiers
│   ├── character.py            # Character class
│   ├── classes.py              # Class definitions
│   ├── races.py                # Race definitions
│   └── creation.py             # Character creation flow
│
├── story/                      # NEW: Story content
│   ├── __init__.py
│   ├── scenes/                # Scene YAML/JSON files
│   │   ├── act_1/
│   │   │   ├── tavern_entry.yaml
│   │   │   └── dungeon_entrance.yaml
│   │   ├── act_2/
│   │   └── act_3/
│   ├── choices.yaml           # Choice definitions
│   └── endings.yaml           # Ending conditions
│
├── tui/                       # REFACTOR: Simplified UI
│   ├── __init__.py
│   ├── app.py                 # Main Textual app
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── title_screen.py   # Main menu
│   │   ├── character_creation.py  # Character creation
│   │   ├── game_screen.py   # Main narrative display
│   │   ├── combat_screen.py  # Combat resolution
│   │   └── ending_screen.py  # Endings display
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── narrative_box.py  # Text display
│   │   ├── choice_menu.py    # Choice selection
│   │   ├── dice_view.py     # ASCII dice
│   │   └── stat_bar.py     # Character stats
│   └── styles/
│       └── theme.py          # Terminal styling
│
├── persistence/               # KEEP: Storage
│   ├── __init__.py
│   ├── database.py           # SQLite wrapper
│   └── save_manager.py      # Save/load
│
├── core/                      # KEEP: Utilities
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── event_bus.py         # Event system
│   └── exceptions.py        # Custom exceptions
│
└── utils/                    # KEEP: Utilities
    ├── __init__.py
    ├── logger.py            # Logging
    └── validators.py        # Input validation
```

## 4. Data Models

### 4.1 Scene

```python
@dataclass
class Scene:
    id: str                          # Unique scene ID (e.g., "tavern_entry")
    act: int                         # Act number (1-3)
    title: str                       # Scene title
    description: str                 # Main narrative text
    description_ai: Optional[str]   # AI enhancement prompt
    choices: List[Choice]            # Available choices
    dice_check: Optional[DiceCheck]  # Optional skill check
    next_scene: Optional[str]        # Default next scene ID
    flags_required: Dict[str, bool]  # Flags needed to enter
    flags_set: Dict[str, bool]       # Flags set on entry
    is_combat: bool                  # Combat scene flag
    is_ending: bool                  # Ending scene flag
    ending_type: Optional[str]        # Ending ID if is_ending
```

### 4.2 Choice

```python
@dataclass
class Choice:
    id: str                          # Unique choice ID
    text: str                         # Choice text shown to player
    shortcut: str                     # Keyboard shortcut (A, B, C, D)
    difficulty_modifier: int          # DC modifier based on choice
    consequences: List[Consequence]    # What happens
    next_scene: str                  # Scene to go to
    skill_check: Optional[SkillCheck] # Required roll
    failed_next_scene: Optional[str]  # Scene if check fails
    required_flags: Dict[str, bool]   # Flags needed
    set_flags: Dict[str, bool]        # Flags this choice sets
    # BG3-style: optional relationship gates
    relationship_required: Optional[Dict[str, int]]  # npc_id -> min_score
    relationship_change: Optional[Dict[str, int]]   # npc_id -> delta
```

### 4.3 Consequence

```python
@dataclass
class Consequence:
    type: str                        # "stat", "item", "flag", "relationship", "gold"
    target: str                      # What it affects
    value: Any                       # How much/effect
```

### 4.4 Skill Check

```python
@dataclass
class SkillCheck:
    ability: str                     # "str", "dex", "con", "int", "wis", "cha"
    dc: int                         # Difficulty Class
    success_next_scene: str         # Scene on success
    failure_next_scene: str         # Scene on failure
```

### 4.5 Game State

```python
@dataclass
class GameState:
    character: Character              # Player character
    current_scene: str               # Current scene ID
    scene_history: List[str]         # Scenes visited in order
    choices_made: List[str]          # Choice IDs selected
    flags: Dict[str, bool]           # Story flags (e.g., met_goblin: true)
    relationships: Dict[str, int]     # NPC relationship scores (-10 to +10)
    inventory: List[str]             # Item IDs collected
    current_act: int                # Current act (1-3)
    is_combat: bool                 # In combat flag
    combat_state: Optional[CombatState]
    ending_determined: Optional[str] # Ending ID if determined
    turns_spent: int                # Time spent in game
```

### 4.6 Dice Roll Result

```python
@dataclass
class DiceRollResult:
    dice_type: str                  # "d20", "d6", etc.
    rolls: List[int]                # Individual die results
    modifier: int                   # Added to total
    total: int                      # Sum of rolls + modifier
    natural: Optional[int]          # Natural roll (before modifier)
    is_critical: bool               # Natural 20
    is_fumble: bool                 # Natural 1
```

## 5. Core Components

### 5.1 OpenRouter Client

```python
class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = "meta-llama/llama-3.1-8b-instruct"
    
    async def generate(
        self, 
        prompt: str, 
        model: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate text using OpenRouter API."""
        ...
    
    async def enhance_description(
        self, 
        template: str, 
        context: dict
    ) -> str:
        """Enhance a scene description with AI."""
        ...
    
    async def generate_dialogue(
        self, 
        npc_name: str, 
        mood: str, 
        context: str
    ) -> str:
        """Generate NPC dialogue."""
        ...
```

### 5.2 Scene Manager

```python
class SceneManager:
    def __init__(self, story_dir: Path, ai_client: OpenRouterClient = None):
        self.story_dir = story_dir
        self.ai_client = ai_client
        self.scenes: Dict[str, Scene] = {}
        self._load_scenes()
    
    def get_scene(self, scene_id: str) -> Scene:
        """Get scene by ID."""
        ...
    
    def get_next_scene(
        self, 
        current_scene: Scene, 
        choice: Choice,
        game_state: GameState
    ) -> Scene:
        """Determine next scene based on choice."""
        ...
    
    async def render_scene(
        self, 
        scene: Scene, 
        game_state: GameState
    ) -> str:
        """Render scene with AI enhancement."""
        ...
```

### 5.3 Choice System

```python
class ChoiceSystem:
    def __init__(self):
        self.selected_index = 0
    
    def present_choices(
        self, 
        choices: List[Choice], 
        game_state: GameState
    ) -> List[Choice]:
        """Filter and present valid choices."""
        ...
    
    def select_choice(self, index: int) -> Choice:
        """Select choice by index."""
        ...
    
    def apply_consequences(
        self, 
        choice: Choice, 
        game_state: GameState
    ) -> GameState:
        """Apply choice consequences to game state."""
        ...
```

### 5.4 ASCII Dice Display (BG3-Style)

**Animated Roll Sequence:**
1. `display_rolling(ability: str, dc: int, modifier: int)` - Pre-roll + "Rolling..." + "?"
2. After delay (~0.5–1s): `display_skill_check(ability, result, dc, success)`
3. Nat 20: `★ CRITICAL ★` frame; optional `sys.stdout.write('\a')`
4. Nat 1: Distinct fumble frame

```python
class DiceDisplay:
    @staticmethod
    def display_rolling(ability: str, dc: int, modifier: int) -> str:
        """Pre-roll context + rolling placeholder."""
        return f"DC {dc} · {ability.upper()} (+{modifier})\n\nRolling...\n  [?]"

    @staticmethod
    def display_d20(result: DiceRollResult) -> str:
        """Generate ASCII art for d20 roll."""
        ...

    @staticmethod
    def display_skill_check(
        ability: str, result: DiceRollResult, dc: int, success: bool
    ) -> str:
        """Generate ASCII art for skill check. Nat 20/1 get special frames."""
        ...
```

### 5.5 Ending Manager

```python
class EndingManager:
    def __init__(self, endings_config: Path):
        self.endings = self._load_endings(endings_config)
    
    def determine_ending(self, game_state: GameState) -> str:
        """Determine which ending based on flags and choices."""
        ...
    
    def get_ending(self, ending_id: str) -> Ending:
        """Get ending by ID."""
        ...
```

## 6. Scene YAML Format

```yaml
# story/scenes/act_1/tavern_entry.yaml
id: tavern_entry
act: 1
title: "The Prancing Pony"

description: |
  The warm glow of hearth fire spills onto the cobblestones as you push 
  open the heavy oak door. The smell of roasting meat and ale fills your 
  nostrils. {patrons_ai}
  
  A group of rough-looking adventurers argue in one corner. Near the bar, 
  a hooded figure sits alone, nursing a drink.

description_ai: "Describe the busy tavern atmosphere with 2-3 sensory details"

choices:
  - id: talk_stranger
    text: "Approach the mysterious hooded figure"
    shortcut: A
    next_scene: mysterious_figure
    consequences:
      - type: flag
        target: met_stranger
        value: true
  
  - id: talk_adventurers
    text: "Join the adventurers' conversation"
    shortcut: B
    next_scene: adventurers
    skill_check:
      ability: cha
      dc: 12
      success_next_scene: adventurers
      failure_next_scene: adventurers_rejected
  
  - id: barkeep_rumors
    text: "Ask the barkeep about local rumors"
    shortcut: C
    consequences:
      - type: gold
        target: player
        value: -2
    next_scene: barkeep_rumors
  
  - id: leave_tavern
    text: "Leave and head to the dungeon"
    shortcut: D
    next_scene: dungeon_entrance

flags_set:
  visited_tavern: true
```

## 7. Endings YAML Format

```yaml
# story/endings.yaml
endings:
  hero:
    title: "The Hero's Triumph"
    description: |
      With the dark lord defeated and the realm saved, you stand victorious.
      Songs will be sung of your bravery for generations to come...
    requirements:
      flags_required:
        boss_defeated: true
        saved_kingdom: true
      choices_made:
        - heroic_choice_1
        - heroic_choice_2
  
  tragic:
    title: "The Final Sacrifice"
    description: |
      As the portal closes behind you, you know you will never return.
      But your sacrifice has saved them all...
    requirements:
      flags_required:
        sacrifice_made: true
  
  merchant:
    title: "The Wealthy Trader"
    description: |
      Who needs glory when you have gold? You've made quite a fortune
      on your adventures and retired comfortably...
    requirements:
      flags_required:
        completed_trade: true
      min_gold: 500
  
  corrupted:
    title: "Shadows Embrace"
    description: |
      The power was too sweet, the darkness too welcoming.
      You have become what you once sought to destroy...
    requirements:
      flags_required:
        darkness_accepted: true
  
  mystery:
    title: "Beyond the Veil"
    description: |
      The ancient secret was real, and now you understand.
      Reality bends as you step through the threshold...
    requirements:
      flags_required:
        discovered_secret: true
```

## 8. AI Prompt Templates

### Scene Enhancement Prompt
```
Enhance this scene description for a D&D interactive fiction game.
Keep the core facts and tone. Add 2-3 sentences of atmospheric detail.

Base description:
{base_description}

Context:
- Player class: {player_class}
- Current act: {act}
- Recent events: {recent_flags}

Enhanced description:
```

### Dialogue Generation Prompt
```
Generate 1-2 sentences of dialogue for a D&D NPC.

NPC: {npc_name}
Mood: {mood} (hostile/neutral/friendly/helpful)
Context: {situation}

Dialogue:
```

### Outcome Narration Prompt
```
The player just rolled {roll_result} on a {check_type} check (DC {dc}).
The roll was {success/failure}.

Provide a 1-2 sentence narrative description of what happens:

Narration:
```

## 9. TUI Screen Specifications

### 9.1 Screen Layout Architecture

Target: 80x24 terminal. All screens use Textual Widgets with Header/Footer.

| Screen | Layout | Widgets |
|--------|--------|---------|
| Title | Centered Vertical | Static(title), Static(subtitle), Button(New/Continue/Load/Quit) |
| Character Creation | Vertical | Static(prompt), Input/Static(options), Button(Start) |
| Narrative Game | Horizontal | Left: ScrollableContainer(scene_title, scene_description); Right: Vertical(choices, dice_display, status_info) |
| Load Game | Vertical | ListView(saves) |

### 9.2 Narrative Game Screen (Two-Column)

```python
# Layout: Horizontal
# Left panel (70%): ScrollableContainer
#   - scene_title (Static)
#   - scene_description (Static, markup=True)
# Right panel (30%): Vertical
#   - choices_header (Static)
#   - choices_container (Vertical of Buttons)
#   - dice_display (Static)  # "Rolling...", result, or empty
#   - status_info (Static)   # Character stats
#   - action_buttons (Static) # [S] Save
```

### 9.3 Dice Roll Animation (BG3-Style)

**Sequence:**
1. Pre-roll: Show "DC {dc} · {ability} (+{mod})" in dice_display
2. Rolling: Show "Rolling..." with cycling "?" for ~0.5–1s (`set_interval`)
3. Reveal: Roll d20, display result via DiceDisplay
4. Nat 20: Special frame `★ CRITICAL ★`; optional terminal bell `\a`
5. Nat 1: Distinct fumble frame

```python
# In narrative_game_screen._handle_skill_check():
# 1. dice_widget.update("DC 12 · Persuasion (+3)\n\n[Press to roll]")
# 2. await asyncio.sleep(0.1); dice_widget.update("Rolling...\n  [?]")
# 3. set_interval(0.15, cycle_question_mark) for 3-5 ticks
# 4. result = DiceDisplay.roll_d20(modifier)
# 5. dice_widget.update(DiceDisplay.display_skill_check(...))
```

### 9.4 Scene Title Formatting

Use `═══ {title} ═══` for scene headers (e.g., `═══ The Prancing Pony ═══`).

### 9.5 Choice Display with DC Hint

Choices with skill_check show DC: `[B] Join adventurers (DC 12 CHA)`

### 9.6 Screen Classes (Reference)

```python
class TitleScreen(Screen):
    def compose(self):
        yield Static(TITLE_ART, id="title-art")
        yield Static("A Narrative D&D Adventure", id="subtitle")
        yield Button("New Game", id="btn_new")
        yield Button("Continue", id="btn_continue")
        yield Button("Load Game", id="btn_load")
        yield Button("Quit", id="btn_quit")

class NarrativeGameScreen(Screen):
    def compose(self):
        yield Horizontal(
            ScrollableContainer(Static(id="scene_title"), Static(id="scene_description")),
            Vertical(Static("CHOICES"), Vertical(id="choices_container"),
                     Static(id="dice_display"), Static(id="status_info"))
        )
```

### 9.7 ASCII Wireframes

Full ASCII mockups: see [docs/PRD.md](docs/PRD.md) Appendix B.

## 10. Game Flow State Machine

```
                    ┌──────────────┐
                    │   TITLE      │
                    └──────┬───────┘
                           │ new_game
                           ▼
                    ┌──────────────┐
                    │CHARACTER     │
                    │CREATION      │
                    └──────┬───────┘
                           │ start
                           ▼
                    ┌──────────────┐
                    │    SCENE     │◄────────────────────┐
                    └──────┬───────┘                     │
                           │                              │
                           ▼                              │
                    ┌──────────────┐                     │
                    │   CHOICE     │                     │
                    │  SELECTION   │                     │
                    └──────┬───────┘                     │
                           │                              │
            ┌──────────────┼──────────────┐              │
            ▼              ▼              ▼              │
     ┌──────────┐   ┌──────────┐   ┌──────────┐        │
     │  SKILL   │   │COMBAT    │   │  DIRECT  │        │
     │  CHECK   │   │  SCENE   │   │  SCENE   │        │
     └─────┬────┘   └─────┬────┘   └─────┬────┘        │
           │              │              │              │
           ▼              ▼              ▼              │
     ┌──────────┐   ┌──────────┐   ┌──────────┐        │
     │ OUTCOME  │   │ OUTCOME  │   │ OUTCOME  │        │
     └─────┬────┘   └─────┬────┘   └─────┬────┘        │
           │              │              │              │
           └──────────────┼──────────────┘              │
                          ▼                              │
                   ┌──────────┐                         │
                   │  NEXT    │─────────────────────────┘
                   │  SCENE   │
                   └─────┬────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
     ┌─────────────┐           ┌─────────────┐
     │ NOT ENDING  │           │   ENDING    │
     │   SCENE     │           │   SCREEN    │
     └──────┬──────┘           └─────────────┘
            │
            └─────────────────────────────┐
                                          │
                                          ▼ (loop back to SCENE)
```

## 11. Configuration

```python
# config.py additions

AI_CONFIG = {
    "enabled": True,
    "provider": "openrouter",
    "api_key_env": "OPENROUTER_API_KEY",
    "default_model": "meta-llama/llama-3.1-8b-instruct",
    "fallback_models": [
        "qwen/qwen-2.5-7b-instruct",
        "mistralai/mistral-7b-instruct",
    ],
    "max_tokens": 500,
    "temperature": 0.7,
    "timeout_seconds": 10,
}

NARRATIVE_CONFIG = {
    "story_directory": "src/story/scenes",
    "default_act": 1,
    "max_choices": 4,
    "enable_ai_enhancement": True,
    "enable_fallback": True,
}

GAME_CONFIG = {
    "title": "AI Dungeon Chronicles",
    "version": "1.0.0",
    "save_directory": "saves",
    "auto_save": True,
}
```

## 12. Persistence Schema

```sql
-- Game saves table
CREATE TABLE game_saves (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    character_name TEXT NOT NULL,
    current_scene TEXT NOT NULL,
    current_act INTEGER DEFAULT 1,
    flags_json TEXT NOT NULL,
    choices_json TEXT NOT NULL,
    relationships_json TEXT,
    inventory_json TEXT,
    turns_spent INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Character table (existing, reuse)
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    character_class TEXT NOT NULL,
    race TEXT NOT NULL,
    strength INTEGER NOT NULL,
    dexterity INTEGER NOT NULL,
    constitution INTEGER NOT NULL,
    intelligence INTEGER NOT NULL,
    wisdom INTEGER NOT NULL,
    charisma INTEGER NOT NULL,
    hit_points INTEGER NOT NULL,
    armor_class INTEGER DEFAULT 10,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 13. Error Handling

```python
class NarrativeError(Exception):
    """Base exception for narrative system."""
    pass

class SceneNotFoundError(NarrativeError):
    """Scene ID not found."""
    pass

class InvalidChoiceError(NarrativeError):
    """Invalid choice selected."""
    pass

class AIError(NarrativeError):
    """AI generation failed."""
    pass

class SaveLoadError(NarrativeError):
    """Save/load operation failed."""
    pass
```

## 14. Testing Strategy

### Unit Tests
- Scene loading and parsing
- Choice filtering logic
- Consequence application
- Flag tracking
- Dice rolling

### Integration Tests
- Full scene flow
- AI integration (with mocks)
- Save/load cycle
- Ending determination

### TDD Approach
1. Write failing test
2. Run test (expect failure)
3. Implement code
4. Run test (expect pass)
5. Refactor if needed
6. Commit

---

## Appendix A: ASCII Dice Reference

### D20 Natural 20
```
    ╭─────────────╮
    │  ★ 20 ★    │
    ╰─────────────╯
```

### D20 Natural 1
```
    ╭─────────────╮
    │    1       │
    ╰─────────────╯
```

### Damage Roll (2d6+3)
```
Damage: 2d6+3 = [4, 2] + 3 = 9 slashing!
```

### Skill Check Success
```
    ╭─────────────╮
    │    17      │
    ╰─────────────╯
    d20 = 17 + 3 = 20 vs DC 15 ✓ SUCCESS!
```

---

## Appendix B: Sample Scene JSON

```json
{
  "id": "dungeon_entrance",
  "act": 1,
  "title": "The Dungeon Awaits",
  "description": "You stand before the gaping entrance of the ancient dungeon. A cold wind escapes from within, carrying the scent of earth and something else... something old.\n\nTorches flicker on either side of the entrance, casting dancing shadows on the moss-covered stones.",
  "choices": [
    {
      "id": "enter_boldly",
      "text": "Enter the dungeon boldly, weapon drawn",
      "shortcut": "A",
      "next_scene": "dungeon_entry_hall",
      "skill_check": {
        "ability": "dex",
        "dc": 10,
        "success_next_scene": "dungeon_entry_hall",
        "failure_next_scene": "trap_triggered"
      }
    },
    {
      "id": "examine",
      "text": "Carefully examine the entrance for traps",
      "shortcut": "B",
      "next_scene": "entrance_examined",
      "skill_check": {
        "ability": "int",
        "dc": 12,
        "success_next_scene": "traps_identified",
        "failure_next_scene": "traps_missed"
      }
    },
    {
      "id": "call_out",
      "text": "Call out to see if anyone responds",
      "shortcut": "C",
      "next_scene": "call_out_response"
    },
    {
      "id": "return_town",
      "text": "Return to town for more preparation",
      "shortcut": "D",
      "next_scene": "town_preparation",
      "consequences": [
        {
          "type": "flag",
          "target": "returned_unprepared",
          "value": true
        }
      ]
    }
  ],
  "flags_set": {
    "visited_dungeon_entrance": true
  }
}
```
