# Product Requirements Document (PRD)

## D&D Roguelike Hybrid CLI Game

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-02-09

---

## 1. Executive Summary

A procedurally-generated roguelike CLI game combining D&D tabletop mechanics with traditional roguelike gameplay. Players explore randomly generated dungeons, engage in D20-based combat, manage character progression, and experience persistent campaigns with save compression.

## 2. Product Vision

Create a technically demanding CLI game that serves dual purposes:
- An engaging roguelike experience for players
- A comprehensive benchmark for testing LLM model capabilities across coding, architecture, and edge case handling

## 3. Target Audience

- Developers testing LLM capabilities
- Roguelike enthusiasts seeking D&D mechanics
- CLI game players who enjoy procedurally generated content

## 4. Core Features

### 4.1 Character System

| Feature | Description | Priority |
|---------|-------------|----------|
| Six Attributes | STR, DEX, CON, INT, WIS, CHA | Must Have |
| Derived Stats | AC, HP, Saves, Skills from attributes | Must Have |
| Class System | Fighter, Wizard, Rogue, Cleric, Paladin | Must Have |
| Equipment Slots | Head, Body, Main Hand, Off Hand, Ring, Boots | Must Have |
| Inventory | Weight-limited, stackable items | Must Have |
| Abilities | Class-specific with cooldowns and resources | Should Have |

### 4.2 Procedural Generation

| Feature | Description | Priority |
|---------|-------------|----------|
| Dungeon Layout | BSP trees, cellular automata | Must Have |
| Room Connection | Corridor generation algorithms | Must Have |
| Loot Generation | Rarity tiers, stat scaling | Must Have |
| Enemy Scaling | Difficulty increases with depth | Must Have |
| Quest Generation | Procedural quest objectives | Could Have |

### 4.3 Combat System

| Feature | Description | Priority |
|---------|-------------|----------|
| D20 Attack Rolls | 1d20 + mods vs AC | Must Have |
| Damage Formulas | Die-based with multipliers | Must Have |
| Critical Hits | Expanded threat range, doubled damage | Must Have |
| Status Effects | Buffs/debuffs with stacking | Should Have |
| Initiative Tracker | Turn order management | Must Have |

### 4.4 AI & Pathfinding

| Feature | Description | Priority |
|---------|-------------|----------|
| A* Pathfinding | Enemy navigation to player | Must Have |
| Field of View | Shadow casting algorithm | Must Have |
| Fog of War | Explored area persistence | Should Have |
| Enemy AI | Aggro ranges, attack patterns | Must Have |

### 4.5 Persistence & Storage

| Feature | Description | Priority |
|---------|-------------|----------|
| SQLite Database | Character, world state storage | Must Have |
| Save Compression | zlib/LZ4 compressed save files | Must Have |
| Auto-save | Periodic save on milestones | Should Have |
| Multiple Save Slots | Backup and restore | Could Have |

### 4.6 Concurrency

| Feature | Description | Priority |
|---------|-------------|----------|
| Background Spawner | Async enemy spawns | Must Have |
| Tick System | Game loop with delta time | Must Have |
| Event Queue | Asynchronous event processing | Should Have |

### 4.7 User Experience

| Feature | Description | Priority |
|---------|-------------|----------|
| ASCII Graphics | Traditional roguelike visuals | Must Have |
| Color Output | ANSI color support | Should Have |
| Command Interface | Intuitive input system | Must Have |
| Help System | In-game documentation | Should Have |

### 4.8 TUI Interface (Textual)

| Feature | Description | Priority |
|---------|-------------|----------|
| Panel-based Layout | Status, map, log, action panels | Must Have |
| Rich ASCII Rendering | Colors, styles, gradients | Must Have |
| Keyboard Navigation | Vim-style and arrow keys | Must Have |
| Mouse Support | Click to select, context menus | Could Have |
| Real-time Updates | Tick-based refresh without flicker | Must Have |
| Scrollable Logs | Combat log, message history | Must Have |
| Modal Dialogs | Character creation, inventory | Should Have |
| Responsive Layout | Adapt to terminal resize | Should Have |

## 5. Non-Functional Requirements

### 5.1 Performance
- Save load time < 2 seconds for 100+ hour saves
- Pathfinding < 10ms for 100+ enemies
- Memory footprint < 100MB
- TUI render time < 16ms (60fps target)
- Map redraw < 5ms for 80x24 viewport

### 5.2 Reliability
- Save corruption handled gracefully
- Input validation on all commands
- No crashes from invalid game states
- TUI handles terminal resize gracefully
- No flicker or tearing on updates

### 5.3 Compatibility
- macOS, Linux, Windows (via cross-platform libs)
- Python 3.10+ or equivalent

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| LLM Test Coverage | 100% features implemented |
| Save Corruption Recovery | 100% graceful handling |
| Edge Case Coverage | All identified cases handled |
| Code Complexity | Maintainable module structure |

## 7. Out of Scope

- Multiplayer/multiplayer
- Audio/sound effects
- Graphical UI (beyond TUI - native GUI/Web UI)
- Mod support (v1)
- Network features

## 8. Future Considerations

- Modding API (v2)
- Daily challenge leaderboards
- Steam/cloud saves
- Cross-platform persistent world

---

## Appendix A: Attribute System

| Attribute | Primary Use | Secondary Use |
|-----------|-------------|---------------|
| STR | Melee attack/damage | Carrying capacity |
| DEX | Ranged attack, AC | Initiative |
| CON | HP, Fortitude save | Poison resistance |
| WIS | Perception, Will save | Spellcasting (Cleric) |
| INT | Skills, Will save | Spellcasting (Wizard) |
| CHA | Social checks | Spellcasting (Paladin) |

## Appendix B: Rarity Tiers

| Rarity | Color | Drop Chance |
|--------|-------|-------------|
| Common | White | 60% |
| Uncommon | Green | 25% |
| Rare | Blue | 10% |
| Epic | Purple | 4% |
| Legendary | Orange | 1% |
