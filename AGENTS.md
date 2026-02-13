# D&D Roguelike Hybrid - Agent Documentation

## Project Summary

A Python CLI/TUI roguelike game combining D&D 5th Edition mechanics with procedural dungeon generation. Designed to test LLM capabilities across multiple domains.

**Tech Stack:** Python 3.10+, Textual TUI, SQLite
**Documentation:** `docs/RFC.md`, `docs/PRD.md`, `docs/LLM_BENCHMARK.md`

---

## Architecture Overview

```
src/
├── cli/           # Command parser, display, input handler
├── tui/           # Textual app, screens, widgets, bindings
├── core/          # Game engine, event bus, config
├── entities/      # Character, Enemy, Item base classes
├── world/         # Dungeon generator, map, FOV, tiles
├── combat/        # Combat engine, dice, initiative, status effects
├── character/     # Attributes, inventory, equipment, leveling
├── persistence/   # Database, save manager, migrations
├── concurrency/   # Tick system, async spawner, worker pool
└── utils/        # Logger, exceptions, validators
```

---

## Agent Working Guidelines

### 1. Always Check Available Skills

Before starting ANY task, check available skills and invoke relevant ones first. Skills provide specialized capabilities and domain knowledge.

**Rule:** If there's even a 1% chance a skill applies, invoke it.

#### Priority Order
1. **Process Skills** (invoke before implementation)
   - `brainstorming` - Before creative work, feature design
   - `systematic-debugging` - When encountering bugs/test failures
   - `test-driven-development` - Before writing implementation code
   - `executing-plans` - When implementing multi-step plans

2. **Implementation Skills** (use for specific domains)
   - `frontend-design` - For TUI/UI components
   - `backend-development:*` - For game logic, persistence
   - `theme-factory` - For styling
   - `api-design-principles` - For designing interfaces

3. **Utility Skills**
   - `copywriting` - For in-game text, documentation

**How to use:**
```bash
# Invoke a skill
Skill skill=skill_name

# Example
Skill skill=systematic-debugging  # When bug found
Skill skill=brainstorming  # Before adding new feature
```

### 2. Superpowers Skills (Critical)

Special skills marked with `superpowers:*` provide enhanced workflows:

| Skill | When to Use |
|-------|-------------|
| `superpowers:brainstorming` | Before any feature implementation |
| `superpowers:systematic-debugging` | Before proposing bug fixes |
| `superpowers:test-driven-development` | Before writing any code |
| `superpowers:executing-plans` | When implementing multi-step plans |
| `superpowers:dispatching-parallel-agents` | AVOID - leads to memory leaks |
| `superpowers:requesting-code-review` | Before merging/committing |
| `superpowers:finishing-a-development-branch` | When completing a feature |

**Important:** Superpowers skills should be invoked FIRST before normal Claude Code behavior.

---

## Key Technical Decisions

### D&D 5e Rules (Follow Exactly)

From `docs/RFC.md` Appendix A:

| Rule | Implementation |
|------|----------------|
| Attack Roll | `d20 + ability_mod + proficiency` vs AC |
| Critical Hit | Natural 20 = damage dice rolled twice |
| Natural 1 | Automatic miss |
| Ability Modifier | `(score - 10) // 2` |
| Proficiency | Level 1-4: +2, 5-8: +3, 9-12: +4, 13-16: +5, 17-20: +6 |

### Algorithms Required

| Algorithm | Purpose | RFC Section |
|-----------|---------|-------------|
| A* Pathfinding | Enemy navigation | 5.2 |
| BSP Partitioning | Room placement | 5.1 |
| Cellular Automata | Cave generation | 5.1 |
| Shadow Casting | Field of view | 5.3 |

### Performance Requirements

| Metric | Target |
|--------|--------|
| Save/Load | < 500ms |
| Map redraw (80x24) | < 5ms |
| Pathfinding (100 enemies) | < 10ms |
| Memory | < 50MB |

---

## Module Responsibilities

### Core (`core/`)
- `game_engine.py`: Main loop, tick management, action execution
- `event_bus.py`: Pub/sub event system for module communication
- `config.py`: Game configuration constants

### World (`world/`)
- `dungeon_generator.py`: BSP + cellular automata dungeon creation
- `map.py`: Tile grid, pathfinding interface
- `fov.py`: Shadow casting visibility calculation
- `tile_types.py`: Tile type definitions, properties

### Combat (`combat/`)
- `combat_engine.py`: Attack resolution, damage calculation
- `dice.py`: D&D dice rolling utilities
- `initiative.py`: Turn order management
- `status_effects.py`: Conditions (poisoned, stunned, etc.)

### Character (`character/`)
- `attributes.py`: 6 attributes, modifier calculations
- `inventory.py`: Item storage, weight limits, stacking
- `equipment.py`: Slot management, bonuses
- `leveling.py`: XP, level-up logic

### Persistence (`persistence/`)
- `database.py`: SQLite wrapper, schema management
- `save_manager.py`: JSON serialization, compression (LZ4/zlib)
- `migrations.py`: Schema version upgrades

### TUI (`tui/`)
- `app.py`: Textual App subclass, bindings
- `screens/*.py`: Game, character, inventory, log, menu screens
- `widgets/*.py`: Map, status, log, combat widgets
- `reactivity/state_store.py`: Observable state pattern

---

## Data Models (Follow RFC Section 4)

### Character Fields Required
```python
@dataclass
class Character:
    id: str
    name: str
    level: int
    experience: int
    character_class: str
    race: str

    # 6 Attributes (6-20)
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    # Derived (calculate, don't store)
    armor_class: int  # 10 + dex_mod
    max_hp: int        # class + con_mod
    proficiency_bonus: int  # based on level

    # Resources
    hit_points: int
    temporary_hp: int
    exhaustion_level: int
    class_resources: Dict[str, int]

    # State
    alive: bool
    conditions: List[StatusEffect]
    death_saves: Tuple[int, int]

    # Inventory
    inventory: Inventory
    equipment: Equipment

    # Position
    current_floor: int
    position: Tuple[int, int]
```

---

## Implementation Guidelines

### Code Style
- Follow PEP 8 (enforced by ruff)
- Full type hints on all public APIs
- Docstrings on classes and public methods
- Use dataclasses for data models

### Error Handling
- Use custom exceptions from `utils/exceptions.py`
- Log errors with context before raising
- Graceful degradation on non-critical failures

### Testing
- Minimum 3 unit tests per module
- Test edge cases from `docs/LLM_BENCHMARK.md` section 4
- Mock external dependencies (dice rolls, RNG)

### Performance
- Profile before optimizing
- Lazy evaluation for expensive calculations
- Cache FOV and pathfinding results

---

## Common Pitfalls

### Algorithms
- A*: Missing visited set causes infinite loops
- FOV: Light bleeding through diagonal walls
- BSP: Rooms extending beyond partition bounds

### State Management
- Mutable default arguments (use `None` defaults)
- Missing state notifications to UI
- Race conditions in async code

### Persistence
- Forgetting to commit transactions
- Not validating save version on load
- Missing compression error handling

### TUI
- Blocking calls in async contexts
- Forgetting to call `refresh()` after updates
- Incorrect widget composition
- Using outdated Textual APIs (see compatibility notes below)

---

## Textual Compatibility Notes

This codebase uses Textual 4.x. Key compatibility notes:

### Screen Management
- Use `SCREENS` class dict to register screens by name
- Use `push_screen("name")` / `pop_screen()` for navigation
- Don't use `visible` parameter on screens
- Don't use `get_screen_by_id()` (doesn't exist)

### CSS
- Custom theme variables (`$surface`, `$accent`, etc.) are NOT supported
- Use direct color values: `background: #0d1117;`
- Pseudo-class `selected` doesn't exist; use `hover` or `focus`

### Widgets
- `ListView` doesn't accept `items` parameter in constructor
- Widget `render()` method should return `str`, not `None`
- Use `query_one()` to find widgets by ID

### See Also
- Bug documentation: `docs/bug.md`

---

## Commands

```bash
# Development
pip install -e .
python -m src.main

# Testing
pytest tests/ -v
pytest tests/integration/ -v

# Quality
mypy src/ --strict
ruff check src/

# Benchmarks
pytest tests/ -k "benchmark" --benchmark-only
```

---

## External Resources

- D&D 5e SRD: https://5thsrd.org/
- Textual Docs: https://textual.textualize.io/
- Python asyncio: https://docs.python.org/3/library/asyncio.html

---

## LLM Benchmark Context

This project is designed as an LLM capability benchmark. See `docs/LLM_BENCHMARK.md` for:
- Challenge definitions
- Scoring rubrics
- Known failure patterns
- Test execution protocols

When implementing features, consider:
1. Edge case handling (not just happy path)
2. Error recovery mechanisms
3. Performance implications
4. Code maintainability
