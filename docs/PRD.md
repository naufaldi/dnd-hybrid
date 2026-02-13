# Product Requirements Document (PRD)

## AI Dungeon Chronicles - Narrative D&D Interactive Fiction

**Version:** 2.2.0
**Status:** In Progress
**Last Updated:** 2026-02-12

---

## 1. Executive Summary

A terminal-based narrative D&D interactive fiction game with AI-enhanced storytelling. Players experience branching storylines with meaningful choices, explicit dice rolling with ASCII visuals, and multiple endings based on their decisions. Combines the storytelling depth of interactive fiction with D&D mechanics and AI generation.

## 2. Product Vision

Create an engaging narrative RPG experience that showcases AI integration in interactive fiction:
- **Text-first gameplay** - No graphics, pure storytelling
- **Meaningful choices** - Every decision affects the story
- **Visible dice** - ASCII dice rolls for transparency
- **AI enhancement** - Dynamic content via OpenRouter
- **Multiple endings** - Replayable with different outcomes
- **BG3-style feel** - Dice drama, choice weight, narrative flow in terminal

## 3. User Stories

| ID | As a... | I want... | so that... | Priority |
|----|---------|-----------|------------|----------|
| US-1 | player | New Game to take me into the narrative story (tavern entry) | I experience the D&D interactive fiction | High |
| US-2 | player | to load saved narrative games from Continue/Load | I can resume my story | High |
| US-3 | player | character creation to produce a character with attributes for skill checks | my class/race choices matter | High |
| US-4 | player | the main menu to reflect "AI Dungeon Chronicles" | the branding matches the experience | Medium |
| US-5 | player | dice rolls to animate (Rolling... → reveal) | they feel dramatic like BG3 | High |
| US-6 | player | NPCs to remember my choices and unlock different dialogue | choices have weight and consequences | Medium |
| US-7 | player | to see DC and modifier before rolling | I know the stakes of each check | High |
| US-8 | player | scene transitions and rich prose | the story feels like a light novel | Medium |

## 4. Target Audience

- Interactive fiction enthusiasts
- D&D players who enjoy narrative storytelling
- Players who prefer text adventures over graphics
- Developers interested in AI integration examples

## 5. Core Features

### 5.1 Narrative System

| Feature | Description | Priority |
|---------|-------------|----------|
| Scene Engine | Load/render story scenes from YAML | Must Have |
| Choice System | 2-4 choices per scene, keyboard shortcuts | Must Have |
| Branching Paths | Choices lead to different scenes | Must Have |
| Story Flags | Track decisions and state | Must Have |
| Ending Manager | Determine ending based on flags | Must Have |

### 5.2 AI Integration (OpenRouter)

| Feature | Description | Priority |
|---------|-------------|----------|
| API Client | OpenRouter wrapper for free models | Must Have |
| Scene Enhancement | AI expands template descriptions | Must Have |
| NPC Dialogue | AI generates conversational responses | Should Have |
| Fallback System | Templates when AI unavailable | Must Have |
| Rate Limiting | Respect API limits | Must Have |

### 5.3 Dice & Combat System

| Feature | Description | Priority |
|---------|-------------|----------|
| ASCII Dice Display | Visual d4/d6/d8/d10/d12/d20 | Must Have |
| Attack Rolls | d20 + modifiers vs AC | Must Have |
| Skill Checks | Ability checks with DC | Must Have |
| Damage Rolls | Explicit damage dice display | Must Have |
| Combat Narrator | Describe outcomes textually | Must Have |

### 5.3.1 Reusable Combat System

The combat system is designed to be reusable for any enemy type through configuration.

#### Architecture

```
Scene YAML                          Game Engine
────────────                        ───────────
combat_encounter: <enemy_type>  →  Load enemy from definitions
                                  →  Run combat loop
                                  →  On victory → victory_next_scene
                                  →  On defeat → defeat_scene
```

#### Enemy Definitions

Enemies are defined in `src/data/enemies.yaml` or `src/entities/enemies.py`:

```yaml
goblin:
  name: Goblin
  hp: 7
  ac: 15
  challenge: 1/4
  speed: 30
  abilities:
    - Nimble Escape (disengage/hide as bonus action)
  attacks:
    - name: Scimitar
      damage: 1d6+3
      type: slashing
      range: melee
    - name: Shortbow
      damage: 1d6+3
      type: piercing
      range: 80/320
```

#### Adding New Enemies

To add a new enemy type (hobgoblin, ghost, bandit):

1. Add enemy definition to `enemies.yaml`
2. In scene YAML, use `combat_encounter: <enemy_type>`

Example for new enemy:

```yaml
# enemies.yaml
hobgoblin:
  name: Hobgoblin
  hp: 11
  ac: 18
  challenge: 1/2
  attacks:
    - name: Longsword
      damage: 1d10+3
      type: slashing

# scene YAML
choices:
  - id: fight
    text: "Stand and fight!"
    combat_encounter: hobgoblin
    victory_next_scene: hobgoblin_victory
    defeat_scene: death_in_dungeon
```

#### Combat Flow

1. Player selects combat choice in narrative scene
2. System loads enemy definition by type
3. Combat screen displays: enemy name, HP, player HP, action options
4. Player chooses action (Attack, Defend, Item, Flee)
5. System resolves action with dice rolls
6. Enemy takes turn (AI-controlled)
7. Repeat until victory or defeat
8. Transition to appropriate scene

#### Combat Actions

| Action | Description |
|--------|-------------|
| Attack | Standard attack roll vs enemy AC |
| Defend | Gain +2 AC until next turn |
| Item | Use inventory item |
| Flee | DEX check (DC 12) to escape |

#### D&D 5e Combat Rules (Per RFC)

| Rule | Implementation |
|------|----------------|
| Attack Roll | `d20 + ability_mod + proficiency` vs AC |
| Critical Hit | Natural 20 = damage dice rolled twice |
| Natural 1 | Automatic miss |
| Ability Modifier | `(score - 10) // 2` |
| Proficiency | Level 1-4: +2, 5-8: +3, 9-12: +4, 13-16: +5, 17-20: +6 |

### 5.4 Character System

| Feature | Description | Priority |
|---------|-------------|----------|
| 6 Attributes | STR, DEX, CON, INT, WIS, CHA | Must Have |
| Derived Stats | AC, HP, Proficiency | Must Have |
| Classes | Fighter, Wizard, Rogue, Cleric | Must Have |
| Races | Human, Elf, Dwarf, Halfling | Must Have |
| Backstory | Narrative character creation | Should Have |
| Equipment | Items affect stats | Could Have |

### 5.5 Persistence

| Feature | Description | Priority |
|---------|-------------|----------|
| Save Character | Store character data | Must Have |
| Save Progress | Track story flags/choices | Must Have |
| Load Game | Resume from save | Must Have |
| Multiple Saves | Save slots | Could Have |

### 5.6 User Interface

| Feature | Description | Priority |
|---------|-------------|----------|
| Title Screen | ASCII art, menu options | Must Have |
| Character Creation | Step-by-step with descriptions | Must Have |
| Game Screen | Narrative text + choices | Must Have |
| Combat Screen | Dice display + outcomes | Must Have |
| Ending Screen | Show ending + stats | Must Have |

## 6. Game Flow

```
[Title] → [New/Continue] → [Character Creation] → [Story Loop] → [Ending]
                                                     ↓
                                          Scene → Description → Choices
                                                     ↓
                                              [Roll Dice?]
                                                     ↓
                                              Outcome → Next Scene
```

## 7. AI Integration Points

| Point | Purpose | Fallback |
|-------|---------|----------|
| Scene Intro | Expand atmosphere | Static text |
| NPC Response | Generate dialogue | Scripted |
| Outcome Text | Describe results | Generic |
| Flavor | Add atmosphere | None |

---

## Implementation Roadmap

### Phase Overview

| Phase | Focus | Description | Target |
|-------|-------|-------------|--------|
| **Phase 1** | Act 1 MVP | Full playable Act 1: tavern → dungeon → ending | 1-2 weeks |
| **Phase 2** | Polish | Narrative prose + BG3-style dice drama | 1 week |
| **Phase 3** | Act 2-3 | Outline + core scenes for full campaign | 2 weeks |
| **Phase 4** | AI NPCs | Dialogue generation for NPCs | 1-2 weeks |
| **Phase 5** | AI Branches | Dynamic story branches + endings | Ongoing |

---

### Phase 1: Act 1 MVP (Priority)

**Goal:** Complete playable experience from tavern to ending

#### 1.1 Screen Flow Wiring
- [ ] Title Screen → New/Continue/Load/Quit
- [ ] Character Creation flow (name → class → race)
- [ ] Narrative Game Screen (story + choices + stats)
- [ ] Combat Screen (if needed)
- [ ] Ending Screen (determination + display)
- [ ] Save/Load integration

#### 1.2 Core Systems
- [ ] Game state management (flags, character, inventory)
- [ ] Scene navigation (next_scene, skill checks, consequences)
- [ ] Flag-based choice filtering
- [ ] Gold/inventory management
- [ ] Character stats (HP, AC, attributes)

#### 1.3 Missing Scenes (Act 1)
- [ ] Pit scenarios (pit_escaped, pit_exhausted)
- [ ] Loot collection scenes
- [ ] Secret compartment outcomes
- [ ] Dock collapse/far_shore continuation
- [ ] Cultist boss continuation

#### 1.4 Act 1 Completion Checklist
- [ ] All 39 scenes implemented
- [ ] All paths lead to ending (no dead ends)
- [ ] 4 endings working (Hero, Survivor, Mystery, Fallen)
- [ ] Victory/defeat paths complete

---

### Phase 2: Polish

#### 2.1 Narrative Enhancement
- [ ] Rich scene descriptions
- [ ] Vivid prose for outcomes
- [ ] Scene transitions

#### 2.2 Dice Display
- [ ] ASCII dice art (d4, d6, d8, d10, d12, d20)
- [ ] Rolling animation (Rolling... → reveal)
- [ ] Critical hit/miss visual drama
- [ ] DC display before roll
- [ ] Modifier display

#### 2.3 UI Polish
- [ ] Two-column layout (story | choices+stats)
- [ ] Character info panel
- [ ] Save prompt

---

### Phase 3: Act 2-3

#### 3.1 Act 2: Rising Action
**Premise:** Player returns to town with knowledge of dungeon. New threats emerge.

**Key Elements:**
- New location: Town + surrounding areas
- New NPCs: Merchant, Guard Captain, local Mage
- Branch continuation from Act 1 choices
- Side quests available
- Dungeon deeper levels accessible

**Scene Count Target:** ~25 new scenes

#### 3.2 Act 3: Climax
**Premise:** Final confrontation with cultist leader + ancient evil.

**Key Elements:**
- Multiple final paths (combat, diplomatic, secret)
- Culmination of all Act 1-2 choices
- Extended ending sequence
- New ending types based on full campaign

**Scene Count Target:** ~20 new scenes

#### 3.3 Endings (Full Campaign)
| Ending | Requirements |
|--------|--------------|
| **Legendary** | All side quests + hero ending |
| **Hero** | Defeated cultist + saved town |
| **Survivor** | Escaped with answers |
| **Martyr** | Self-sacrifice for greater good |
| **Corrupted** | Fell to darkness |
| **Mystery** | Left with questions |

---

### Phase 4: AI NPCs

#### 4.1 Dialogue Generation
- [ ] OpenRouter integration for NPC responses
- [ ] Context: character class, race, past choices
- [ ] NPC personality templates
- [ ] Fallback to scripted dialogue

#### 4.2 NPC Memory System
- [ ] Track player interactions
- [ ] Relationship values per NPC
- [ ] Conditional dialogue based on history

---

### Phase 5: AI Branches

#### 5.1 Dynamic Scene Generation
- [ ] Generate new scenes on dead ends
- [ ] Context-aware scene descriptions
- [ ] Maintain narrative consistency

#### 5.2 AI Story Branches
- [ ] Generate choices at key decision points
- [ ] Procedural quest generation
- [ ] Unique endings per playthrough

#### 5.3 Performance & Safety
- [ ] Response caching
- [ ] Timeout handling (10s max)
- [ ] Fallback content always available
- [ ] Rate limiting

---

## 8. Story Structure

### Acts
- **Act 1:** Introduction, first choices, initial adventure (MVP - playable)
- **Act 2:** Rising action, major branches, NPCs (future)
- **Act 3:** Climax, final choices, endings (future)

---

## 8.1 Act 1 MVP - Complete Story Flow

### Overview
**Goal:** A complete, playable experience from tavern start to satisfying ending (~15-20 scenes)

**Story Premise:** A mysterious dungeon has appeared outside a small town. A hooded stranger in the local tavern knows its secrets. The player must explore the dungeon, defeat (or ally with) its creatures, and discover the truth behind the ancient evil within.

### Scene Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TAVERN ENTRY (START)                                │
│                   "The Prancing Pony"                                      │
│         A → Mysterious Figure    C → Ask Barkeep (-2g)                     │
│         B → Skill Check → Dungeon's Secret OR Return to Town              │
│         D → Dungeon Entrance                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DUNGEON ENTRANCE                                     │
│         A → Entry Hall (DEX check trap trigger)                            │
│         B → Skill Check → Identify Traps OR Miss                          │
│         C → Call Out Response (treasure goblin encounter)                 │
│         D → Return to Tavern                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENTRY HALL                                          │
│         A → Goblin Encounter (combat path)                                 │
│         B → Underground Lake (exploration path)                            │
│         C → Old Armory (loot path)                                         │
│         D → Search Room → Secret Compartment                               │
└─────────────────────────────────────────────────────────────────────────────┘
          │                       │                        │
          ▼                       ▼                        ▼
   ┌─────────────┐      ┌─────────────────┐    ┌─────────────────┐
   │   GOBLIN    │      │ UNDERGROUND LAKE│    │  OLD ARMORY     │
   │  ENCOUNTER  │      │                 │    │                 │
   │ (combat)    │      │ A → Lockbox    │    │ A → Find Weapon│
   │             │      │ B → Creature   │    │ B → Trap        │
   │ A → Fight  │      │ C → Dock Cross  │    │ C → Search      │
   │ B → Negoti │      │                 │    │                 │
   │ C → Flee   │      │                 │    │                 │
   └──────┬──────┘      └────────┬────────┘    └────────┬────────┘
          │                       │                        │
          ▼                       ▼                        ▼
   ┌─────────────┐      ┌─────────────────┐    ┌─────────────────┐
   │   VICTORY  │      │  CREATURE LAIR  │    │   TREASURE      │
   │  or DEATH  │      │  (Plesiosaur)   │    │   (Magic Item) │
   │            │      │                 │    │                 │
   │ +XP +Gold │      │ A → Fight       │    │ Set flag:       │
   │ +Flag:     │      │ B → Negotiate   │    │ found_weapon    │
   │ defeated_  │      │                 │    │                 │
   │  goblins   │      └────────┬────────┘    └────────┬────────┘
   └──────┬──────┘               │                      │
          │                      ▼                      ▼
          │            ┌─────────────────┐    ┌─────────────────┐
          │            │    VICTORY     │    │    VICTORY     │
          │            │  +XP +Gold    │    │  +XP +Gold     │
          │            │  +Flag:       │    │ +Flag:         │
          │            │  befriended_  │    │ found_magic_   │
          │            │  creature     │    │   item         │
          │            └─────────────────┘    └────────┬────────┘
          │                                             │
          └─────────────────────┬───────────────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │    ACT 1 CLIMAX         │
                   │   "The Dark Shrine"      │
                   │                         │
                   │  Mini-boss: cultist     │
                   │  leader +2 goblins     │
                   │                         │
                   │ A → Fight (combat)      │
                   │ B → Sneak past         │
                   │ C → Diplomatic         │
                   │ D → Search for secret  │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │    ACT 1 CONCLUSION     │
                   │   "Escape from Dark"   │
                   │                         │
                   │ Returns to tavern      │
                   │ Sets flags:            │
                   │ - escaped_dungeon      │
                   │ - defeated_cultist     │
                   │ - found_treasure (if)  │
                   │                         │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │      ENDINGS            │
                   │                         │
                   │ HERO: defeated_cultist  │
                   │     + escaped_dungeon   │
                   │     + saved_town       │
                   │                         │
                   │ SURVIVOR: escaped      │
                   │     _dungeon only      │
                   │                         │
                   │ MYSTERY: default       │
                   └─────────────────────────┘
```

### Scene Inventory

#### Total Act 1 MVP Scenes: 39

| Scene ID | File | Status |
|----------|------|--------|
| tavern_entry | tavern_entry.yaml | ✅ Complete |
| mysterious_figure | mysterious_figure.yaml | ✅ Complete |
| dungeon_entrance | dungeon_entrance.yaml | ✅ Complete |
| dungeon_entry_hall | dungeon_entry_hall.yaml | ✅ Complete |
| goblin_encounter | goblin_encounter.yaml | ✅ Complete |
| underground_lake | underground_lake.yaml | ✅ Complete |
| trap_triggered | trap_triggered.yaml | ✅ Complete |
| traps_identified | traps_identified.yaml | ✅ Complete |
| goblin_victory | goblin_victory.yaml | ✅ Complete |
| dungeon_info | dungeon_info.yaml | ✅ Complete |
| offer_heroic | offer_heroic.yaml | ✅ Complete |
| confrontation_success | confrontation_success.yaml | ✅ Complete |
| confrontation_fail | confrontation_fail.yaml | ✅ Complete |
| call_out_response | call_out_response.yaml | ✅ Complete |
| traps_missed | traps_missed.yaml | ✅ Complete |
| entrance_examined | entrance_examined.yaml | ✅ Complete |
| goblin_negotiation | goblin_negotiation.yaml | ✅ Complete |
| goblin_bribe | goblin_bribe.yaml | ✅ Complete |
| goblin_attack | goblin_attack.yaml | ✅ Complete |
| goblin_flee | goblin_flee.yaml | ✅ Complete |
| goblin_escape | goblin_escape.yaml | ✅ Complete |
| lockbox_contents | lockbox_contents.yaml | ✅ Complete |
| broken_lockbox | broken_lockbox.yaml | ✅ Complete |
| creature_lair | creature_lair.yaml | ✅ Complete |
| dock_collapse | dock_collapse.yaml | ✅ Complete |
| far_shore | far_shore.yaml | ✅ Complete |
| old_armory | old_armory.yaml | ✅ Complete |
| secret_compartment | secret_compartment.yaml | ✅ Complete |
| trap_pit | trap_pit.yaml | ✅ Complete |
| dark_shrine | dark_shrine.yaml | ✅ Complete |
| cultist_boss | cultist_boss.yaml | ✅ Complete |
| act1_conclusion | act1_conclusion.yaml | ✅ Complete |
| death_in_dungeon | death_in_dungeon.yaml | ✅ Complete |
| hero_ending | hero_ending.yaml | ✅ Complete |
| survivor_ending | survivor_ending.yaml | ✅ Complete |
| pit_escaped | pit_escaped.yaml | ✅ Complete |
| pit_exhausted | pit_exhausted.yaml | ✅ Complete |
| loot_collection | loot_collection.yaml | ✅ Complete |
| nothing_found | nothing_found.yaml | ✅ Complete |

#### New Scenes Needed (MVP)
| Priority | Scene ID | Purpose | Path From |
|----------|----------|---------|-----------|
| **P0** | dungeon_info | Stranger tells about dungeon | mysterious_figure:A |
| **P0** | offer_heroic | Stranger offers quest | mysterious_figure:B |
| **P0** | confrontation_success | Intimidate stranger (pass) | mysterious_figure:C→success |
| **P0** | confrontation_fail | Intimidate stranger (fail) | mysterious_figure:C→fail |
| **P0** | call_out_response | Goblin responds to call | dungeon_entrance:C |
| **P0** | traps_missed | Failed trap check | dungeon_entrance:B→fail |
| **P0** | entrance_examined | Successful trap ID | dungeon_entrance:B→success |
| **P1** | goblin_negotiation | CHA check to negotiate | goblin_encounter:B |
| **P1** | goblin_bribe | Pay goblins to pass | goblin_encounter:B→success |
| **P1** | goblin_attack | Negotiation fails | goblin_encounter:B→fail |
| **P1** | goblin_flee | Run from goblins | goblin_encounter:C |
| **P1** | lockbox_contents | Success: get gold/items | underground_lake:A→success |
| **P1** | broken_lockbox | Fail: nothing | underground_lake:A→fail |
| **P1** | creature_lair | Find underwater creature | underground_lake:B |
| **P1** | dock_collapse | Dock breaks | underground_lake:C→fail |
| **P1** | far_shore | Cross lake safely | underground_lake:C→success |
| **P2** | old_armory | Find old weapons | dungeon_entry_hall:C |
| **P2** | secret_compartment | Secret room | dungeon_entry_hall:D→success |
| **P2** | nothing_found | Search fails | dungeon_entry_hall:D→fail |
| **P2** | trap_pit | Fall into pit | dungeon_entry_hall:B→fail |
| **P2** | dark_shrine | Act 1 climax location | Entry Hall OR Goblin OR Lake |
| **P2** | cultist_battle | Fight cultist leader | dark_shrine:A |
| **P2** | sneak_past | Sneak through shrine | dark_shrine:B |
| **P3** | act1_conclusion | Return to town | cultist OR sneak |
| **P3** | death_in_dungeon | Player dies | Any combat |

### Flags Used in Act 1

| Flag | Set When | Used For |
|------|----------|----------|
| visited_tavern | tavern_entry | Track player started |
| met_stranger | Approach stranger | Unlock dialogue |
| learned_dungeon_secret | Ask about dungeon | Bonus in ending |
| allied_with_stranger | Offer help | Special ending |
| visited_dungeon_entrance | Enter dungeon | Branching |
| identified_traps | Pass trap check | Safe passage |
| defeated_goblins | Kill goblins | XP + gold |
| befriended_goblins | Pass CHA check | Alternative path |
| found_treasure | Find loot | Better ending |
| found_magic_item | Get magic weapon | Bonus stats |
| escaped_dungeon | Complete Act 1 | Survivor ending |
| defeated_cultist | Beat boss | Hero ending |
| player_died | HP <= 0 | Death ending |

### Endings (Act 1 MVP)

| Ending | Requirements | Description |
|--------|--------------|-------------|
| **Hero** | defeated_cultist + escaped_dungeon | Defeated the cult leader, saved town |
| **Survivor** | escaped_dungeon (no cultist) | Escaped but didn't finish |
| **Mystery** | default (no flags) | Left with questions unanswered |
| **Fallen** | player_died | Died in the dungeon |

### Act 1 Quest Summary

**Main Quest:** Investigate the mysterious dungeon threatening the town

**Side Opportunities:**
- Help the mysterious stranger → ally ending
- Befriend goblins → alternate path
- Find treasure → richer ending
- Discover secret lore → mystery ending

---

### Endings (v1.0)
1. **Hero** - Saved the realm
2. **Tragic** - Self-sacrifice
3. **Merchant** - Wealth achieved
4. **Corrupted** - Fell to darkness
5. **Mystery** - Discovered secret

---

## 8.2 AI-Enhanced Storytelling

### Overview
The game uses OpenRouter API to dynamically generate narrative content, making each playthrough unique. AI enhances:
- Scene descriptions
- NPC dialogue
- Outcome narration
- Branching story extensions

### AI Integration Points

| Point | Trigger | AI Role | Fallback |
|-------|---------|---------|----------|
| **Scene Intro** | Every scene | Expand base description with atmospheric detail | Static YAML text |
| **NPC Dialogue** | When `ai_dialogue: true` | Generate contextual NPC responses | "The stranger says nothing." |
| **Choice Outcomes** | When `ai_outcome: true` | Describe success/failure in narrative | Generic pass/fail text |
| **Dynamic Branches** | When `ai_branches: true` | Generate 2-3 new choices based on context | Fixed choices only |
| **Ending Epilogue** | Ending determination | Personalized ending narration | Static ending text |

### AI Configuration (per scene)

```yaml
# Scene YAML example with AI
id: mysterious_figure
ai_dialogue: true        # Enable AI NPC responses
ai_branches: false       # Don't generate new choices
ai_outcome: true        # AI describes skill check results
npc_name: "Stranger"
npc_mood: "enigmatic"

# AI generates response based on:
# - player character (name, class, race)
# - story flags set
# - previous choices
# - game state
```

### AI-Generated Endings

When enabled, AI can generate personalized endings based on:
- Player's choices throughout game
- Flags accumulated
- Character class/race
- Items collected

```yaml
# endings.yaml - AI-generated ending
legendary_ai:
  title: "The [Title Generated by AI]"
  description: "[AI generates personalized epilogue]"
  ai_generated: true
  requirements:
    flags_required:
      discovered_secret: true
      defeated_boss: true
```

### AI Safety & Fallbacks

| Scenario | Behavior |
|----------|----------|
| API unavailable | Use static YAML content |
| API timeout (10s) | Use fallback text |
| API error | Log error, use fallback |
| Empty response | Use fallback |
| Rate limited | Queue for retry, use fallback |

### Performance

- Scene with AI: < 3 seconds (with timeout)
- Cached responses: instant (same scene, same state)
- Async generation: player can read while generating

---

## 8.3 AI-Controlled NPCs (Intelligent NPCs)

### Overview
NPCs are powered by AI to think, reason, and make contextual decisions - not just generate dialogue. This creates emergent storytelling where NPCs react authentically to player actions.

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI NPC Decision Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Player Action                                                 │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────┐                                          │
│   │  NPC "Thinks"   │  ← AI analyzes:                          │
│   │  (reasoning)    │     - Player's class/race                │
│   └────────┬────────┘     - Previous interactions              │
│            │              - Current game state                  │
│            ▼              - Story flags                         │
│   ┌─────────────────┐     - NPC's personality                 │
│   │  AI Decision    │                                          │
│   │  Engine         │                                          │
│   └────────┬────────┘                                          │
│            │                                                     │
│            ▼                                                     │
│   ┌─────────────────┐                                          │
│   │  Response +     │                                          │
│   │  Action         │  ← AI generates:                         │
│   │                 │     - What NPC says                      │
│   └─────────────────┘     - What NPC does                      │
│                           - How NPC reacts                      │
└─────────────────────────────────────────────────────────────────┘
```

### NPC Personality System

Each NPC has a defined personality that shapes AI decisions:

```yaml
npc:
  id: mysterious_stranger
  name: "Aldric"
  personality:
    # Core traits (affects decision-making)
    alignment: "chaotic_good"
    intelligence: "high"
    mood: "enigmatic"

    # Decision weights
    decision_weights:
      helps_player: 0.7      # 70% likely to help
      reveals_secrets: 0.4   # 40% likely to share lore
      attacks_if_threatened: 0.6

    # Memory
    memory:
      - "player_approached"
      - "player_refused_help"
```

### AI Reasoning Examples

| Player Action | NPC "Thinking" (AI) | NPC Decision |
|---------------|---------------------|--------------|
| Player attacks goblin | "This fighter shows aggression. May be useful ally or potential threat." | Offer quest OR attack |
| Player helps tavern patron | "Demonstrates compassion. Likely hero type." | Share dungeon secret |
| Player steals from merchant | "Greedy. Untrustworthy." | Refuse to trade, alert guards |
| Player is mage class | "Arcane user. May understand the ancient texts." | Give lore book |

### NPC Decision Types

| Decision | Description | Examples |
|----------|-------------|----------|
| **Dialogue** | What NPC says | Greeting, warning, quest offer |
| **Action** | What NPC does | Attack, flee, give item |
| **Reaction** | How NPC responds | Friendly, hostile, neutral |
| **Relationship** | Change in NPC attitude | Trust +, hostility + |
| **Memory** | NPC remembers player | Store for future encounters |

### Dynamic Quest Generation

AI NPCs can offer procedurally generated quests:

```yaml
npc_quest:
  ai_generated: true
  trigger: "player_approaches"
  generation_prompt: |
    NPC is a mysterious wizard.
    Player is a {class} {race}.
    Generate a short quest that:
    - Relates to player's abilities
    - Connects to main dungeon plot
    - Has clear reward

  # AI returns:
  # - Quest text
  # - Quest objectives
  # - Rewards
  # - Success/failure outcomes
```

### Technical Implementation

| Component | Purpose |
|-----------|---------|
| `NPCBrain` | Manages NPC thinking, memory, decisions |
| `PersonalityEngine` | Loads/defines NPC personalities |
| `DecisionTree` | AI reasons through options |
| `ActionResolver` | Executes NPC decisions in game |
| `MemoryStore` | Persists NPC memories |

### Example AI NPC Session

```
Player: "What do you know about the dungeon?"

NPC (Aldric the Stranger):
  [AI Thinking...]
  "The player is a fighter who helped the tavern keeper.
   They seem heroic but naive. I should test their worthiness."

  [AI Decision: Share partial truth + test]

  "The dungeon... yes. It calls to those with courage.
   But courage alone won't suffice. Take this symbol.
   Return when you've proven yourself worthy."

  → Gives player "Amulet of Proof"
  → Sets flag: "stranger_testing_player"
```

### NPC vs Static Content

| Feature | Static | AI NPC |
|---------|--------|--------|
| Dialogue | Fixed text | Dynamic generation |
| Reactions | Hardcoded | Contextual |
| Memory | None | Full history |
| Quests | Pre-written | Procedural |
| Replayability | Same each time | Unique each play |

---

## 8.4 AI-Generated Story Branches

### Overview
AI can dynamically generate new story branches based on player actions, creating emergent narratives that go beyond pre-written content.

### How Branch Generation Works

```
Player Action → AI Analyzes Context → Generate New Branches → Player Chooses
                                              │
                            ┌─────────────────┴─────────────────┐
                            ▼                                   ▼
                    2-4 AI-generated                   Original static
                    choices with                   choices (fallback)
                    narrative text
```

### Branch Generation Triggers

| Trigger | When AI Generates | Example |
|---------|-------------------|---------|
| Dead end | No valid next scene | Player takes unmapped path |
| Custom moment | `ai_branches: true` | Major story decision point |
| Random event | 10% chance per scene | Unexpected encounter |
| Player request | Player asks "what if..." | Speculative action |

### Branch Structure

```yaml
# AI-generated branch example
ai_branch:
  generated: true
  based_on:
    - player_class: wizard
    - flag: learned_dungeon_secret
    - gold: 50

  choices:
    - id: ai_choice_1
      text: "Search the ancient library for arcane knowledge"
      shortcut: A
      ai_generated: true
      next_scene: arcane_library

    - id: ai_choice_2
      text: "Seek out the local mages' guild for intel"
      shortcut: B
      ai_generated: true
      next_scene: mages_guild
```

### AI-Generated Endings

Beyond branches, AI can create unique endings:

```yaml
# endings.yaml
dynamic_endings:
  ai_generated: true

  # AI generates ending based on:
  # - Total flags set
  # - Choices made
  # - Character stats
  # - Playtime
  # - Items collected

  generation_template: |
    The player has {flags_set} flags and made {choices_count} choices.
    Their class is {class} and they have {gold} gold.

    Generate a creative ending that:
    - Reflects their choices
    - Provides closure
    - Is 2-3 sentences
    - Has a fitting title
```

### Branch/Ending Quality Controls

| Control | Purpose |
|---------|---------|
| Context window | AI sees relevant game state |
| Prompt templates | Consistent style guide |
| Validation | Check for inappropriate content |
| Caching | Same context → same branches |
| Max length | Prevent overly long text |

### Emergent Story Example

```
Traditional Path:
  Tavern → Dungeon → Goblins → Boss → Ending

Emergent AI Path (Player: Wizard + Learned Secrets):
  Tavern → Dungeon → [AI generates: "Search arcane ruins nearby"]
      → Ancient Library (AI generated scene)
      → [AI generates: "Discovered spellbook, attracted attention"]
      → Boss (Alternative: Magical construct)
      → [AI generates unique ending based on spellbook choice]
```

### Comparison

| Feature | Static Story | AI-Enhanced |
|---------|--------------|-------------|
| Total scenes | ~20 | Unlimited |
| Branching | Fixed tree | Emergent |
| Endings | 4-6 fixed | Infinite unique |
| Replayability | Low | High |
| Consistency | Guaranteed | AI-dependent |

### Performance Considerations

- AI thinking: 2-5 seconds per NPC decision
- Caching: Same situation → cached decision
- Queue: Max 1 pending NPC thought
- Fallback: Static response if AI unavailable

## 9. Non-Functional Requirements

### Performance
- Scene load time < 100ms
- AI response timeout < 10s (fallback to template)
- Memory footprint < 50MB
- Terminal responsive at 60fps

### Reliability
- Graceful AI fallback
- Save corruption handling
- Input validation

### Compatibility
- Python 3.10+
- macOS, Linux, Windows
- Terminal width: min 80 cols

## 10. Out of Scope

- Multiplayer
- Audio/sound
- Graphical UI
- Mod support
- Network features

## 11. Future Considerations

- More AI models
- User-created stories
- Achievement system
- Statistics tracking

---

## Appendix A: Dice ASCII Reference

### D20 (Natural 20)
```
    ╭─────────────╮
    │  ★ 20 ★    │
    ╰─────────────╯
```

### D20 (Natural 1)
```
    ╭─────────────╮
    │    1       │
    ╰─────────────╯
```

### Roll Animation
```
    ┌──────────────────┐
    │   Rolling...     │
    │   ╭─────────╮    │
    │   │   ?    │    │
    │   ╰─────────╯    │
    └──────────────────┘
```

---

## Appendix B: ASCII Screen Layouts (80x24 Terminal)

### B.1 Title Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI Dungeon Chronicles                                           21:45      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              ╔═══════════════════════════════════════════╗                   │
│              ║   ⚔ AI DUNGEON CHRONICLES ⚔             ║                   │
│              ║   A Narrative D&D Adventure               ║                   │
│              ╚═══════════════════════════════════════════╝                   │
│                                                                             │
│                             [N] New Game                                    │
│                             [C] Continue                                    │
│                             [L] Load Game                                   │
│                             [Q] Quit                                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  escape: Back    q: Quit                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.2 Character Creation Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI Dungeon Chronicles                                           21:46      │
├─────────────────────────────────────────────────────────────────────────────┤
│                    ═══ Create Your Character ═══                            │
│                    Enter your name: [_______________]                        │
│                    Choose your class: > fighter  wizard  rogue  cleric      │
│                    Choose your race:  > human  elf  dwarf  halfling          │
│                    [Start Game]                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  enter: Next    escape: Back                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.3 Narrative Game Screen (Two-Column Layout)

Left: story + scene title. Right: choices + stats.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI Dungeon Chronicles                                           21:47      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ═══ The Prancing Pony ═══                                                  │
│                                                                             │
│  The warm glow of hearth fire spills onto the cobblestones...               │
│  A group of rough-looking adventurers argue in one corner.                  │
│  Near the bar, a hooded figure sits alone, nursing a drink.                  │
│                                                                             │
├───────────────────────────────────────┬─────────────────────────────────────┤
│  What do you do?                       │  CHOICES                            │
│                                        │  [A] Approach the mysterious figure  │
│                                        │  [B] Join adventurers (DC 12 CHA)   │
│                                        │  [C] Ask barkeep about rumors       │
│                                        │  [D] Leave for the dungeon         │
│                                        │  ─────────────────────────────────  │
│                                        │  Cynux | Lv1 Fighter                │
│                                        │  HP: 12/12  AC: 10                  │
│                                        │  [S] Save                           │
├───────────────────────────────────────┴─────────────────────────────────────┤
│  A-D: Choose    S: Save    escape: Menu                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.4 Dice Roll (Phase 1: Rolling)

```
│                                        │     ┌─────────────────────┐         │
│  Persuasion (CHA) check. DC 12. +3     │     │    Rolling...        │         │
│                                        │     │    ╭───────────╮     │         │
│                                        │     │    │     ?     │     │         │
│                                        │     │    ╰───────────╯     │         │
│                                        │     │  DC 12 · CHA (+3)    │         │
│                                        │     └─────────────────────┘         │
```

### B.5 Dice Roll (Phase 2: Reveal - Nat 20)

```
│                                        │     ┌─────────────────────┐         │
│                                        │     │   ★ CRITICAL! ★     │         │
│                                        │     │    ╭───────────╮     │         │
│                                        │     │    │  ★ 20 ★  │     │         │
│                                        │     │    ╰───────────╯     │         │
│                                        │     │  d20 = 20 + 3 = 23   │         │
│                                        │     │  vs DC 12 ✓ SUCCESS! │         │
│                                        │     └─────────────────────┘         │
```

### B.6 Combat Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ═══ ⚔ Combat: Goblin ⚔ ═══                                                │
│  The goblin snarls and lunges! You raise your sword—                        │
│     ┌─────────────────────┐   d20 = 18 + 5 = 23 vs AC 12 ✓ HIT!             │
│     │    Attack Roll      │   Damage: 1d8+3 = 9 slashing!                    │
│     │    ╭───────────╮    │   The goblin stumbles back, bloodied...          │
│     │    │    18     │    │   [A] Attack  [B] Defend  [C] Item  [D] Flee     │
│     │    ╰───────────╯    │   HP: 12/12  vs  Goblin HP: 3/12                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.7 Ending Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ═══ THE HERO'S TRIUMPH ═══                                │
│  With the dark lord defeated and the realm saved, you stand victorious.      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Your Journey: Scenes: 24  Choices: 18  Playtime: 28 min                    │
│                    [Return to Title]                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.8 Load Game Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ═══ Load Game ═══                                         │
│  > save_001.json  Cynux · Tavern Entry · 2026-02-11 21:40                   │
│    save_002.json  Elara · Dungeon Hall · 2026-02-10 18:22                    │
│  Enter: Load    escape: Back                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### B.9 Screen Layout Summary

| Screen | Layout | Key Elements |
|--------|--------|---------------|
| Title | Centered | New Game, Continue, Load, Quit |
| Character Creation | Single column | Name → Class → Race → Start |
| Narrative Game | Two columns | Left: story; Right: choices + stats |
| Dice Roll | Story + dice box | Pre-roll (DC) → Rolling → Reveal |
| Combat | Single column | Narrative + dice + choices |
| Ending | Single column | Ending text + journey stats |
| Load | Single column | Save list with character/scene |
