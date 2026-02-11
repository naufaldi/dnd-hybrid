# Product Requirements Document (PRD)

## AI Dungeon Chronicles - Narrative D&D Interactive Fiction

**Version:** 2.1.0  
**Status:** Draft  
**Last Updated:** 2026-02-11

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

## 8. Story Structure

### Acts
- **Act 1:** Introduction, first choices, initial adventure
- **Act 2:** Rising action, major branches, NPCs
- **Act 3:** Climax, final choices, endings

### Endings (v1.0)
1. **Hero** - Saved the realm
2. **Tragic** - Self-sacrifice
3. **Merchant** - Wealth achieved
4. **Corrupted** - Fell to darkness
5. **Mystery** - Discovered secret

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
