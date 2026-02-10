# LLM Benchmark Testing Guide

## D&D Roguelike Hybrid - Model Evaluation Framework

**Version:** 1.0.0
**Status:** Draft
**Purpose:** Structured testing methodology for evaluating LLM capabilities across software engineering domains

---

## 1. Overview

This benchmark framework provides a structured methodology for evaluating LLM performance on a complex, modular CLI game project. The D&D Roguelike Hybrid serves as a comprehensive test environment spanning algorithms, state management, persistence, and TUI development.

### 1.1 Testing Philosophy

| Principle | Description |
|-----------|-------------|
| **Incremental Complexity** | Start with simple modules, progress to integration challenges |
| **Measurable Outcomes** | All tests have clear pass/fail criteria |
| **Edge Case Coverage** | Deliberately introduce failures to test error handling |
| **Architecture Awareness** | Evaluate cross-module dependency management |

### 1.2 Test Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Benchmark Matrix                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Fundamentals   │  Intermediate   │        Advanced         │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Data Models   │ • Algorithms    │ • Async Concurrency    │
│ • Basic Logic   │ • State Mgmt    │ • TUI Integration     │
│ • Unit Tests    │ • Persistence   │ • System Integration   │
│ • Error Handling│ • CLI Interface │ • Performance Tuning   │
└─────────────────┴─────────────────┴─────────────────────────┘
```

---

## 2. Module-by-Module Challenges

### 2.1 Core Data Models (`entities/`, `character/`)

**Difficulty:** Beginner

**Challenge 1.1: Character Implementation**
```
Task: Implement Character dataclass from RFC section 4.1

Evaluation Criteria:
□ All 6 attributes present (STR, DEX, CON, INT, WIS, CHA)
□ Derived stats calculated correctly (AC, HP, proficiency)
□ Property decorators for computed values
□ Type hints on all fields
□ Reasonable default values

Common Failure Points:
- Forgetting exhaustion_level field
- Hardcoding proficiency bonus instead of calculating from level
- Missing death_saves tuple
```

**Challenge 1.2: Item System**
```
Task: Implement Item hierarchy from RFC section 4.4

Evaluation Criteria:
□ Weapon, Armor, Potion types distinguished
□ Rarity enum implemented
□ StatModifier structure for bonuses
□ Stackable item handling
□ Item comparison for inventory merging

Common Failure Points:
- Mixing damage_die (string "1d8") with actual die rolling
- Not handling max_stack limits
- Missing attunement slots logic
```

**Challenge 1.3: Inventory Management**
```
Task: Implement Inventory class with weight limits

Evaluation Criteria:
□ Add/remove items
□ Weight tracking with capacity
□ Stack merging on add
□ Equipment slot validation
□ Sorting/filtering capabilities

Test Edge Cases:
- Adding item that exceeds weight capacity
- Merging non-stackable items
- Removing from empty inventory
```

---

### 2.2 Algorithms (`world/`)

**Difficulty:** Intermediate

**Challenge 2.1: A* Pathfinding**
```
Task: Implement Pathfinder from RFC section 5.2

Evaluation Criteria:
□ Returns valid path or empty list
□ Handles blocked paths correctly
□ Optimized neighbor checking
□ Manhattan distance heuristic
□ Diagonal movement option

Test Scenarios:
- Start and end are the same tile
- No valid path exists
- Path through narrow corridors
- Diagonal movement enabled/disabled

Performance Target: < 10ms for 100 enemies

Common Failure Points:
- Not checking walkability
- Infinite loop on blocked paths
- Path includes non-adjacent steps
- Missing path reconstruction
```

**Challenge 2.2: Dungeon Generation (BSP)**
```
Task: Implement DungeonGenerator from RFC section 5.1

Evaluation Criteria:
□ BSP tree partitions space correctly
□ Rooms placed in leaf nodes
□ Corridors connect all rooms
□ No overlapping rooms
□ Cellular automata for caves
□ Special features placed

Test Scenarios:
- Single room dungeon
- Maximum room density
- Cave-only generation
- Multiple floor generation consistency

Common Failure Points:
- Rooms extending beyond partition bounds
- Disconnected room graph
- Corridor cutting through rooms
- Seed reproducibility issues
```

**Challenge 2.3: Field of View (Shadow Casting)**
```
Task: Implement FieldOfView from RFC section 5.3

Evaluation Criteria:
□ Player always visible
□ Walls block sight correctly
□ Diagonal octant handling
□ Radius limiting works
□ Explored tile tracking

Test Scenarios:
- Open room visibility
- Corridor visibility
- Pillar/counter visibility
- Corner peeking behavior

Common Failure Points:
- Light bleeding through walls
- Missing diagonal corners
- Inconsistent radius calculation
- Performance degradation with large maps
```

---

### 2.3 Combat System (`combat/`)

**Difficulty:** Intermediate

**Challenge 3.1: Attack Resolution**
```
Task: Implement CombatEngine.resolve_attack from RFC section 5.4

Evaluation Criteria:
□ Natural 20 = critical hit
□ Natural 1 = automatic miss
□ Attack bonus calculated correctly
□ Damage formula follows D&D rules
□ Critical damage = 2x dice (no modifier)

Test Scenarios:
- Roll 20 vs AC 15 (proficient)
- Roll 1 vs any AC
- Roll 15 vs AC 20 (need 20 to hit)
- Critical hit calculation

D&D Rules Reference (RFC Appendix A):
- Attack = d20 + ability mod + proficiency (if applicable)
- Critical = roll damage dice twice
- No ability modifier on extra critical dice
```

**Challenge 3.2: Status Effects**
```
Task: Implement status_effects.py

Evaluation Criteria:
□ Common conditions (poisoned, stunned, etc.)
□ Stacking rules per condition
□ Duration tracking
□ Removal on appropriate triggers
□ Effect application/removal hooks

Test Scenarios:
- Multiple poison stacks
- Condition preventing other conditions
- Healing removing dying state
- Duration expiration
```

---

### 2.4 Persistence (`persistence/`)

**Difficulty:** Intermediate

**Challenge 4.1: Database Schema**
```
Task: Implement schema from RFC section 7.1

Evaluation Criteria:
□ All tables created with correct columns
□ Foreign key relationships
□ Indexes on frequently queried fields
□ Schema version tracking
□ Migration capability

Test Scenarios:
- Fresh database creation
- Database already exists
- Migration from v1 to v2
- Concurrent write attempts
```

**Challenge 4.2: Save/Load with Compression**
```
Task: Implement SaveManager from RFC section 7.2

Evaluation Criteria:
□ Saves character and world state
□ Compression reduces file size
□ Checksum validation works
□ Version migration functional
□ Load restores exact state

Test Scenarios:
- Save mid-combat
- Save with full inventory
- Load save from previous version
- Corrupted save file
- Disk full on save

Performance Targets (RFC Appendix C):
- Save time < 500ms
- Load time < 500ms
- Compression ratio > 5:1
```

---

### 2.5 Concurrency (`concurrency/`)

**Difficulty:** Advanced

**Challenge 5.1: Tick System**
```
Task: Implement TickSystem from RFC section 6.1

Evaluation Criteria:
□ Consistent tick rate
□ Subscribers notified each tick
□ Graceful shutdown
□ Tick counting accuracy
□ Sleep compensation for lag

Test Scenarios:
- Heavy subscriber load
- Rapid start/stop cycling
- Tick rate faster than processing
- Long-running stability
```

**Challenge 5.2: Async Spawner**
```
Task: Implement EnemySpawner from RFC section 6.2

Evaluation Criteria:
□ Spawns enemies at correct intervals
□ Queue processing doesn't block
□ Task cancellation handled
□ Spawn location validation
□ Error recovery

Test Scenarios:
- Queue overflow
- Spawn location blocked
- Cancel during spawn
- Multiple simultaneous spawns
```

---

### 2.6 TUI/Textual (`tui/`)

**Difficulty:** Advanced

**Challenge 6.1: Map Widget**
```
Task: Implement MapPanel from RFC section 8.2

Evaluation Criteria:
□ FOV-based visibility
□ Explored vs unseen tiles
□ Entity rendering (player, enemies, items)
□ Color-coded tile types
□ Viewport scrolling

Performance Target: < 5ms render time

Test Scenarios:
- Terminal resize
- Player at map edge
- Multiple enemies visible
- Items on same tile as entity
```

**Challenge 6.2: State Store (Observable Pattern)**
```
Task: Implement StateStore from RFC section 8.6

Evaluation Criteria:
□ State changes detected
□ Subscribers notified on changes
□ 30fps polling rate
□ Graceful start/stop
□ Memory-efficient updates

Test Scenarios:
- Rapid state changes
- Subscriber adds/removes mid-run
- No changes for extended period
- Widget destroyed while subscribed
```

**Challenge 6.3: Action Dispatcher**
```
Task: Implement ActionDispatcher from RFC section 8.7

Evaluation Criteria:
□ Actions queued and processed
□ Response futures resolve correctly
□ Timeout handling
□ Error propagation
□ Cleanup on shutdown

Test Scenarios:
- Action timeout
- Action raises exception
- Rapid fire actions
- Dispatcher shutdown mid-action
```

---

## 3. Integration Challenges

### 3.1 Complete Game Loop

```
Difficulty: Advanced

Task: Integrate all modules into playable game

Evaluation Criteria:
□ Character creation → dungeon exploration → combat → level up → save → load
□ All modules communicate via event bus
□ State persists across floors
□ No memory leaks over extended play

Test Scenarios:
1. New game → reach floor 5 → save → load → continue
2. Die → death saves → stabilize → recover
3. Max inventory → find treasure → auto-sort
4. Long session (100+ turns) stability
```

### 3.2 Error Recovery Chain

```
Difficulty: Advanced

Task: Implement error handling across modules

Evaluation Criteria:
□ Save corruption → recovery attempt → graceful fallback
□ Invalid input → validation → helpful message
□ Module error → isolation → continue operation

Test Scenarios:
- Load corrupted save
- Database locked
- Terminal resize during render
- Enemy path blocked unexpectedly
```

---

## 4. Edge Case Stress Tests

### 4.1 Input Validation

| Test Case | Expected Behavior |
|-----------|-----------------|
| Empty command | Helpful prompt, not crash |
| Move into wall | Message "blocked", no movement |
| Attack with no target | Message "nothing there" |
| Invalid direction | List valid options |
| Negative numbers | Reject with explanation |
| Unicode in character name | Handle or reject gracefully |

### 4.2 Boundary Conditions

| Test Case | Expected Behavior |
|-----------|-----------------|
| Max inventory weight | Reject add, suggest drop |
| Level 20 character | No XP overflow |
| 0 HP character | Death saves or stabilize |
| All equipment slots full | Equipment swap prompt |
| Dungeon generation fails | Retry or fallback map |

### 4.3 Concurrency Edge Cases

| Test Case | Expected Behavior |
|-----------|-----------------|
| Save during enemy spawn | Consistent state |
| Load during combat | Combat state preserved |
| Rapid key presses | Action queue, no skipping |
| Terminal close during save | Complete save or warning |

### 4.4 Persistence Edge Cases

| Test Case | Expected Behavior |
|-----------|-----------------|
| Disk full | Clear error, no corruption |
| Corrupted save | Backup recovery or new game |
| Version mismatch | Migration or rejection |
| Concurrent saves | Lock or queue |

---

## 5. Scoring Framework

### 5.1 Per-Challenge Scoring

```
Score: 0-5 per challenge

5 - Exceeds expectations
  - All criteria met
  - Additional polish/optimization
  - Well-documented code

4 - Meets expectations
  - All criteria met
  - Clean implementation
  - Basic documentation

3 - Mostly meets expectations
  - Core functionality works
  - Minor edge cases unhandled
  - Basic error handling

2 - Partially meets expectations
  - Core functionality works
  - Several edge cases fail
  - Limited error handling

1 - Below expectations
  - Partial implementation
  - Multiple failures
  - Poor code quality

0 - Not attempted or completely broken
```

### 5.2 Category Scores

| Category | Weight | Challenges |
|----------|--------|-----------|
| Data Models | 10% | 3 |
| Algorithms | 20% | 3 |
| Combat System | 15% | 2 |
| Persistence | 15% | 2 |
| Concurrency | 15% | 2 |
| TUI Integration | 15% | 3 |
| Integration | 10% | 2 |

### 5.3 Overall Scoring

```
LLM Benchmark Score = Sum(Category_Score × Weight)

Score Ranges:
90-100: Excellent - Production-ready code
75-89:  Good - Minor polish needed
60-74:  Adequate - Several areas need work
45-59:  Below Average - Significant gaps
0-44:   Needs Improvement - Major issues
```

---

## 6. Test Execution Protocol

### 6.1 Sequential Testing

```
Phase 1: Fundamentals (2 hours)
  → Complete Challenges 1.1, 1.2, 1.3
  → Run unit tests
  → Code review for style

Phase 2: Algorithms (3 hours)
  → Complete Challenges 2.1, 2.2, 2.3
  → Performance testing
  → Edge case validation

Phase 3: Systems (3 hours)
  → Complete Challenges 3.1, 4.1, 4.2
  → Integration testing
  → Error handling verification

Phase 4: Advanced (4 hours)
  → Complete Challenges 5.1, 5.2, 6.1, 6.2
  → Full integration
  → Extended playtesting

Total Recommended Time: 12 hours
```

### 6.2 Test Artifacts Required

For each challenge, LLM should produce:
- [ ] Source code implementation
- [ ] Unit tests (minimum 3 per module)
- [ ] Docstrings on public APIs
- [ ] README or inline comments for complex logic

### 6.3 Verification Commands

```bash
# Run all tests
pytest tests/ -v --tb=short

# Type checking
mypy src/ --strict

# Linting
ruff check src/

# Performance benchmarks
python -m pytest tests/ -k "benchmark" --benchmark-only

# Integration test
python -m pytest tests/integration/ -v
```

---

## 7. Evaluation Rubrics

### 7.1 Code Quality (30%)

| Criterion | Excellent (5) | Good (4) | Adequate (3) | Poor (2) | Failing (1) |
|-----------|--------------|----------|--------------|----------|-------------|
| Style | PEP 8, ruff clean | Minor issues | Some issues | Many issues | No style |
| Types | Full type hints | Most typed | Partial | Few types | No types |
| Docs | Complete docstrings | Adequate | Minimal | None | Misleading |
| Tests | >80% coverage | >60% | >40% | <40% | No tests |

### 7.2 Correctness (40%)

| Criterion | Excellent (5) | Good (4) | Adequate (3) | Poor (2) | Failing (1) |
|-----------|--------------|----------|--------------|----------|-------------|
| Functionality | All features work | Minor bugs | Some broken | Many broken | Core broken |
| Edge Cases | All handled | Most handled | Some handled | Few handled | None |
| D&D Rules | Accurate | Minor deviations | Some errors | Many errors | Wrong |
| Persistence | Reliable | Rare failures | Occasional | Frequent | Broken |

### 7.3 Architecture (15%)

| Criterion | Excellent (5) | Good (4) | Adequate (3) | Poor (2) | Failing (1) |
|-----------|--------------|----------|--------------|----------|-------------|
| Modularity | Clean separation | Good separation | Some coupling | Tight coupling | No separation |
| Dependencies | Proper injection | Mostly clean | Some globals | Many globals | Spaghetti |
| Extensibility | Plugin-ready | Easy to extend | Possible with work | Difficult | Impossible |

### 7.4 Performance (15%)

| Criterion | Excellent (5) | Good (4) | Adequate (3) | Poor (2) | Failing (1) |
|-----------|--------------|----------|--------------|----------|-------------|
| Speed | Meets targets | Close to targets | Acceptable | Slow | Unusable |
| Memory | Efficient | Minor leaks | Some leaks | Leaks | Explodes |
| Responsiveness | Smooth | Minor lag | Noticeable lag | Slow | Freezes |

---

## 8. Known LLM Failure Patterns

### 8.1 Algorithm Implementations

| Pattern | Detection | Remediation |
|---------|-----------|-------------|
| A* without visited set | Infinite loops on blocked paths | Add came_from tracking |
| FOV light bleeding | Visible through walls | Check octant math |
| BSP room overlap | Corridors cut through rooms | Bounds checking |
| Dice rolling bugs | Wrong damage on crit | Review RFC rules |

### 8.2 State Management

| Pattern | Detection | Remediation |
|---------|-----------|-------------|
| Mutable default arguments | Intermittent state bugs | Use None default |
| Missing state updates | UI doesn't refresh | Check all mutations |
| Race conditions | Random failures | Add locks/async safety |
| Memory leaks | Growing memory | Check subscriptions |

### 8.3 TUI Specific

| Pattern | Detection | Remediation |
|---------|-----------|-------------|
| Blocking in async | UI freezes | Use await properly |
| Widget not refreshing | Stale display | Call refresh() |
| Size calculation errors | Layout breaks | Add bounds checking |
| Color not applied | Gray output | Check Color type |

### 8.4 Persistence

| Pattern | Detection | Remediation |
|---------|-----------|-------------|
| Missing commits | Data loss | Always commit |
| SQL injection | N/A - use ORM | Parameterized queries |
| Version not checked | Load crashes | Validate version |
| Compression without error handling | Save fails silently | Add try/except |

---

## 9. Appendix: Challenge Checklist

### Pre-Challenge Setup

- [ ] Clone repository
- [ ] Review RFC.md for full specifications
- [ ] Review PRD.md for requirements
- [ ] Check existing test patterns
- [ ] Set up virtual environment

### Per-Challenge Completion

- [ ] Implement required code
- [ ] Add docstrings to public APIs
- [ ] Write unit tests
- [ ] Run full test suite
- [ ] Type check with mypy
- [ ] Lint with ruff
- [ ] Document any deviations from spec

### Final Verification

- [ ] All integration tests pass
- [ ] No performance regressions
- [ ] Clean git history (meaningful commits)
- [ ] README updated if needed

---

## 10. Appendix: Testing Environment

### Required Tools

```bash
# Python environment
Python 3.10+

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
hypothesis>=6.0.0

# Type checking
mypy>=1.0.0

# Linting
ruff>=0.1.0

# Optional - for TUI testing
pytest-textual>=0.1.0
```

### Benchmark System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8 GB |
| Disk | 1 GB | 5 GB |
| Terminal | 80x24 | 120x50 |

---

## 11. Appendix: Quick Reference

### RFC Key Sections

| Section | Content | Test Focus |
|---------|---------|------------|
| 4.x | Data Models | Schema design |
| 5.x | Algorithms | A*, BSP, FOV |
| 6.x | Concurrency | Async patterns |
| 7.x | Persistence | Database, compression |
| 8.x | TUI | Textual widgets |

### PRD Priority Mapping

| Priority | Implementation Required |
|----------|------------------------|
| Must Have | Full implementation |
| Should Have | If time permits |
| Could Have | Skip for MVP |
| Won't Have | Not in scope |

---

*Last Updated: 2026-02-09*
*Maintained by: Development Team*
