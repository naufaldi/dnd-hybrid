# Implementation Tasks - AI Dungeon Chronicles

**Project:** AI Dungeon Chronicles - Narrative D&D Interactive Fiction
**Source:** RFC.md (v2), PRD.md (v2.2)
**Purpose:** Fully executable tasks for AI agents without human supervision
**Last Updated:** 2026-02-12

---

## Quick Start for AI Agents

```bash
# 1. Verify project structure
ls -la src/

# 2. Install dependencies
pip install -e .

# 3. Run tests
pytest tests/ -v

# 4. Run the game
python -m src.main
```

---

## PHASE 1: Act 1 MVP (Current Focus)

### 1.1 Screen Flow Wiring

| Task | Description | Status |
|------|-------------|--------|
| T001 | Title Screen with New/Continue/Load/Quit | DONE ✓ |
| T002 | Character Creation flow (name → class → race) | DONE ✓ |
| T003 | Narrative Game Screen (story + choices + stats) | DONE ✓ |
| T004 | Combat Screen integration | DONE ✓ |
| T005 | Ending Screen (determination + display) | DONE ✓ |
| T006 | Save/Load integration | DONE ✓ |

### 1.2 Core Systems

| Task | Description | Status |
|------|-------------|--------|
| T010 | Game state management (flags, character, inventory) | DONE ✓ |
| T011 | Scene navigation (next_scene, skill checks, consequences) | DONE ✓ |
| T012 | Flag-based choice filtering | DONE ✓ |
| T013 | Gold/inventory management | DONE ✓ |
| T014 | Character stats (HP, AC, attributes) | DONE ✓ |

### 1.3 Missing Scenes (Act 1)

| Task | Description | Status |
|------|-------------|--------|
| T020 | Pit scenarios (pit_escaped, pit_exhausted) | DONE ✓ |
| T021 | Loot collection scenes | DONE ✓ |
| T022 | Secret compartment outcomes | DONE ✓ |
| T023 | Dock collapse/far_shore continuation | DONE ✓ |
| T024 | Cultist boss continuation | DONE ✓ |

### 1.4 Act 1 Completion

| Task | Description | Status |
|------|-------------|--------|
| T030 | All 39 scenes implemented | DONE ✓ |
| T031 | All paths lead to ending (no dead ends) | DONE ✓ |
| T032 | 4 endings working (Hero, Survivor, Mystery, Fallen) | DONE ✓ |
| T033 | Victory/defeat paths complete | DONE ✓ |

---

## PHASE 2: Polish

### 2.1 Narrative Enhancement

| Task | Description | Status |
|------|-------------|--------|
| T040 | Rich scene descriptions | DONE ✓ |
| T041 | Vivid prose for outcomes | DONE ✓ |
| T042 | Scene transitions | DONE ✓ |

### 2.2 Dice Display

| Task | Description | Status |
|------|-------------|--------|
| T050 | ASCII dice art (d4, d6, d8, d10, d12, d20) | DONE ✓ |
| T051 | Rolling animation (Rolling... → reveal) | DONE ✓ |
| T052 | Critical hit/miss visual drama | DONE ✓ |
| T053 | DC display before roll | DONE ✓ |
| T054 | Modifier display | DONE ✓ |

### 2.3 UI Polish

| Task | Description | Status |
|------|-------------|--------|
| T060 | Two-column layout (story \| choices+stats) | DONE ✓ |
| T061 | Character info panel | DONE ✓ |
| T062 | Save prompt | DONE ✓ |

---

## PHASE 3: Act 2-3 (Future)

### 3.1 Act 2: Rising Action

| Task | Description | Status |
|------|-------------|--------|
| T070 | Define Act 2 story premise and structure | FUTURE |
| T071 | New location scenes (Town + surroundings) | FUTURE |
| T072 | New NPCs (Merchant, Guard Captain, Mage) | FUTURE |
| T073 | Branch continuation from Act 1 | FUTURE |
| T074 | Side quests (~25 scenes) | FUTURE |

### 3.2 Act 3: Climax

| Task | Description | Status |
|------|-------------|--------|
| T080 | Define Act 3 story premise and structure | FUTURE |
| T081 | Final confrontation scenes | FUTURE |
| T082 | Multiple ending paths | FUTURE |
| T083 | Extended ending sequence | FUTURE |
| T084 | New ending types (~20 scenes) | FUTURE |

---

## PHASE 4: AI NPCs

### 4.1 Dialogue Generation

| Task | Description | Status |
|------|-------------|--------|
| T100 | OpenRouter integration for NPC responses | DONE ✓ |
| T101 | Context: character class, race, past choices | DONE ✓ |
| T102 | NPC personality templates | DONE ✓ |
| T103 | Fallback to scripted dialogue | DONE ✓ |

### 4.2 NPC Memory System

| Task | Description | Status |
|------|-------------|--------|
| T110 | Track player interactions | DONE ✓ |
| T111 | Relationship values per NPC | DONE ✓ |
| T112 | Conditional dialogue based on history | DONE ✓ |

---

## PHASE 5: AI Branches

### 5.1 Dynamic Scene Generation

| Task | Description | Status |
|------|-------------|--------|
| T120 | Generate new scenes on dead ends | PENDING |
| T121 | Context-aware scene descriptions | PENDING |
| T122 | Maintain narrative consistency | PENDING |

### 5.2 AI Story Branches

| Task | Description | Status |
|------|-------------|--------|
| T130 | Generate choices at key decision points | PENDING |
| T131 | Procedural quest generation | PENDING |
| T132 | Unique endings per playthrough | PENDING |

### 5.3 Performance & Safety

| Task | Description | Status |
|------|-------------|--------|
| T140 | Response caching | DONE ✓ |
| T141 | Timeout handling (10s max) | DONE ✓ |
| T142 | Fallback content always available | PENDING |
| T143 | Rate limiting | DONE ✓ |

---

## COMPLETED TASKS ✓

### Phase 1: Act 1 MVP

| Task ID | Description | Status |
|---------|-------------|--------|
| N-1 | OpenRouter AI Client | DONE ✓ |
| N-2 | Scene Data Models | DONE ✓ |
| N-3 | Scene Manager | DONE ✓ |
| N-4 | ASCII Dice Display | DONE ✓ |
| N-5 | Choice System | DONE ✓ |
| N-6 | Ending Manager | DONE ✓ |
| N-7 | Create Story Scenes (Act 1 - 39 scenes) | DONE ✓ |
| N-8 | Narrative Game Screen | DONE ✓ |
| N-9 | Integration Tests | DONE ✓ |

### Phase 4: AI Integration (Already Done)

| Task ID | Description | Status |
|---------|-------------|--------|
| AI-1 | OpenRouter Client with retry/rate-limit | DONE ✓ |
| AI-2 | AI Service with disk cache | DONE ✓ |
| AI-3 | Scene model updates (ai_dialogue flags) | DONE ✓ |

---

## What's Been Implemented

### Core Modules
- `src/narrative/models.py` - Scene, Choice, GameState, etc.
- `src/narrative/scene_manager.py` - Scene loading and navigation
- `src/narrative/choice_system.py` - Choice handling
- `src/narrative/ending_manager.py` - Ending determination
- `src/narrative/ai_service.py` - AI enhancement with caching
- `src/ai/openrouter_client.py` - OpenRouter API wrapper
- `src/combat/dice_display.py` - ASCII dice rendering

### Scenes (39 total in Act 1)
- `tavern_entry.yaml` - Starting scene
- `mysterious_figure.yaml` - NPC interaction
- `dungeon_entrance.yaml` - Dungeon entry
- `dungeon_entry_hall.yaml` - Hub area
- All branch scenes (goblins, lake, armory, shrine, etc.)
- All endings (hero, survivor, mystery, death)

### Tests
- 517+ tests passing

## NEW FEATURES IMPLEMENTED

### Phase 4: AI Integration (OpenRouter)

**OpenRouter Client Enhancements:**
- `src/ai/openrouter_client.py` - Enhanced with:
  - Retry logic with exponential backoff (max 3 retries)
  - Rate limiter (30 requests/minute)
  - `openrouter/free` as default model (auto-selects best free model)
  - 5 second timeout
  - Fallback models: deepseek, qwen

**AI Service:**
- `src/narrative/ai_service.py` - New service with:
  - Disk-based response cache (`~/.dnd_roguelike/cache/ai_cache.json`)
  - Per-game caching with 30-day expiration
  - Fallback templates for offline/error states
  - Methods: `enhance_dialogue()`, `narrate_outcome()`

**Scene Model Updates:**
- Added `ai_dialogue: bool` field
- Added `npc_name: Optional[str]` field
- Added `npc_mood: Optional[str]` field

**Scene Updates:**
- `mysterious_figure.yaml` - Added AI dialogue flags

**Tests:**
- `tests/unit/test_narrative/test_ai_service.py` - 18 tests

---

## Quick Reference Commands

```bash
# Run all tests
pytest tests/ -v

# Run narrative tests
pytest tests/unit/test_narrative/ tests/unit/test_ai/ -v

# Run integration tests
pytest tests/integration/test_tui_menu.py tests/integration/test_tui_character.py -v

# Type check
mypy src/

# Lint
ruff check src/
```

---

## Notes for AI Agents

1. Always use TDD - write failing test first
2. Run tests after each implementation
3. Check `mypy src/` and `ruff check src/` before committing
4. Follow RFC specs exactly
5. Test TUI with `app.run_test()` and `pilot.click()`/`pilot.press()`
6. **Priority:** Focus on Phase 1 (Act 1 MVP) tasks first
7. AI features have fallback to static content - always implement fallbacks
8. For TUI work, use Textual 4.x compatibility notes in CLAUDE.md
