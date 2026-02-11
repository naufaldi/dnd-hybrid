# Implementation Tasks - AI Dungeon Chronicles

**Project:** AI Dungeon Chronicles - Narrative D&D Interactive Fiction  
**Source:** RFC.md (v2), PRD.md (v2)  
**Purpose:** Fully executable tasks for AI agents without human supervision  
**Last Updated:** 2026-02-10

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

## COMPLETED TASKS ✓

### Task N-1: OpenRouter AI Client ✓
- Module: `src/ai/openrouter_client.py`
- Tests: `tests/unit/test_ai/test_openrouter_client.py` (7 tests)
- Status: **PASSING**

### Task N-2: Scene Data Models ✓
- Module: `src/narrative/models.py`
- Tests: `tests/unit/test_narrative/test_models.py` (19 tests)
- Status: **PASSING**

### Task N-3: Scene Manager ✓
- Module: `src/narrative/scene_manager.py`
- Tests: `tests/unit/test_narrative/test_scene_manager.py` (7 tests)
- Status: **PASSING**

### Task N-4: ASCII Dice Display ✓
- Module: `src/combat/dice_display.py`
- Tests: `tests/unit/test_combat/test_dice_display.py` (8 tests)
- Status: **PASSING**

### Task N-5: Choice System ✓
- Module: `src/narrative/choice_system.py`
- Tests: `tests/unit/test_narrative/test_choice_system.py` (9 tests)
- Status: **PASSING**

---

## REMAINING TASKS TODO

### Task N-6: Ending Manager ✓
- Module: `src/narrative/ending_manager.py`
- Tests: `tests/unit/test_narrative/test_ending_manager.py` (10 tests)
- Status: **PASSING**

### Task N-7: Create Story Scenes (Act 1) ✓
- Created: `src/story/scenes/act_1/`
  - `tavern_entry.yaml`
  - `mysterious_figure.yaml`
  - `dungeon_entrance.yaml`
  - `dungeon_entry_hall.yaml`
  - `trap_triggered.yaml`
  - `traps_identified.yaml`
  - `goblin_encounter.yaml`
  - `goblin_victory.yaml`
  - `underground_lake.yaml`
- Status: **COMPLETED**

### Task N-8: Create Narrative Game Screen ✓
- Module: `src/tui/screens/narrative_game_screen.py`
- Status: **COMPLETED**

### Task N-9: Integration Tests ✓
- Tests: `tests/integration/test_narrative_flow.py` (9 tests)
- Status: **PASSING**

---

## Test Results

```
517 tests passing ✓
```

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
