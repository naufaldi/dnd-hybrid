# Product Requirements Document (PRD)

## AI Dungeon Chronicles - Narrative D&D Interactive Fiction

**Version:** 2.0.0  
**Status:** Draft  
**Last Updated:** 2026-02-10

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

## 3. Target Audience

- Interactive fiction enthusiasts
- D&D players who enjoy narrative storytelling
- Players who prefer text adventures over graphics
- Developers interested in AI integration examples

## 4. Core Features

### 4.1 Narrative System

| Feature | Description | Priority |
|---------|-------------|----------|
| Scene Engine | Load/render story scenes from YAML | Must Have |
| Choice System | 2-4 choices per scene, keyboard shortcuts | Must Have |
| Branching Paths | Choices lead to different scenes | Must Have |
| Story Flags | Track decisions and state | Must Have |
| Ending Manager | Determine ending based on flags | Must Have |

### 4.2 AI Integration (OpenRouter)

| Feature | Description | Priority |
|---------|-------------|----------|
| API Client | OpenRouter wrapper for free models | Must Have |
| Scene Enhancement | AI expands template descriptions | Must Have |
| NPC Dialogue | AI generates conversational responses | Should Have |
| Fallback System | Templates when AI unavailable | Must Have |
| Rate Limiting | Respect API limits | Must Have |

### 4.3 Dice & Combat System

| Feature | Description | Priority |
|---------|-------------|----------|
| ASCII Dice Display | Visual d4/d6/d8/d10/d12/d20 | Must Have |
| Attack Rolls | d20 + modifiers vs AC | Must Have |
| Skill Checks | Ability checks with DC | Must Have |
| Damage Rolls | Explicit damage dice display | Must Have |
| Combat Narrator | Describe outcomes textually | Must Have |

### 4.4 Character System

| Feature | Description | Priority |
|---------|-------------|----------|
| 6 Attributes | STR, DEX, CON, INT, WIS, CHA | Must Have |
| Derived Stats | AC, HP, Proficiency | Must Have |
| Classes | Fighter, Wizard, Rogue, Cleric | Must Have |
| Races | Human, Elf, Dwarf, Halfling | Must Have |
| Backstory | Narrative character creation | Should Have |
| Equipment | Items affect stats | Could Have |

### 4.5 Persistence

| Feature | Description | Priority |
|---------|-------------|----------|
| Save Character | Store character data | Must Have |
| Save Progress | Track story flags/choices | Must Have |
| Load Game | Resume from save | Must Have |
| Multiple Saves | Save slots | Could Have |

### 4.6 User Interface

| Feature | Description | Priority |
|---------|-------------|----------|
| Title Screen | ASCII art, menu options | Must Have |
| Character Creation | Step-by-step with descriptions | Must Have |
| Game Screen | Narrative text + choices | Must Have |
| Combat Screen | Dice display + outcomes | Must Have |
| Ending Screen | Show ending + stats | Must Have |

## 5. Game Flow

```
[Title] → [New/Continue] → [Character Creation] → [Story Loop] → [Ending]
                                                     ↓
                                          Scene → Description → Choices
                                                     ↓
                                              [Roll Dice?]
                                                     ↓
                                              Outcome → Next Scene
```

## 6. AI Integration Points

| Point | Purpose | Fallback |
|-------|---------|----------|
| Scene Intro | Expand atmosphere | Static text |
| NPC Response | Generate dialogue | Scripted |
| Outcome Text | Describe results | Generic |
| Flavor | Add atmosphere | None |

## 7. Story Structure

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

## 8. Non-Functional Requirements

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

## 9. Out of Scope

- Multiplayer
- Audio/sound
- Graphical UI
- Mod support
- Network features

## 10. Future Considerations

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

## Appendix B: Screen Layouts

### Title Screen
```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║      ⚔️  AI DUNGEON CHRONICLES  ⚔️               ║
║                                                   ║
║          A Narrative D&D Adventure                ║
║                                                   ║
║     [N] New Game                                 ║
║     [C] Continue                                 ║
║     [L] Load Game                                ║
║     [Q] Quit                                    ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

### Game Screen
```
═══════════════════════════════════════════════════════════
                     SCENE TITLE

───────────────────────────────────────────────────────────
Scene description text here. Can be multiple lines describing
what's happening and what the player sees.

What do you do?

  [A] ▶ First choice option
  [B]   Second choice option
  [C]   Third choice option
  [D]   Fourth choice option

  ════════════════════════════════════════════════════════
  STR 14  DEX 12  CON 16  HP: 12/12  Level 1 Fighter
═══════════════════════════════════════════════════════════
```

### Combat Screen
```
═══════════════════════════════════════════════════════════
                     ⚔️ COMBAT: Goblin ⚔️

You swing your sword at the goblin!

    ╭─────────────╮
    │  ★ 18 ★    │
    ╰─────────────╯
    d20 = 18 + 5 = 23 vs AC 12 ✓ HIT!

Damage: 1d8+3 = 6 + 3 = 9 slashing!

The goblin stumbles back, bloodied but alive...

═══════════════════════════════════════════════════════════
```
