# Implementation Tasks - AI Agent Ready

**Project:** D&D Roguelike Hybrid CLI Game
**Source:** RFC.md, PRD.md
**Purpose:** Fully executable tasks for AI agents without human supervision
**Last Updated:** 2026-02-10

---

## Quick Start for AI Agents

```bash
# 1. Initialize project structure
mkdir -p src/{cli,tui/screens,tui/widgets,tui/bindings,tui/styles,tui/reactivity,core,entities,world,combat,character,persistence,concurrency,utils}
mkdir -p tests/{unit,integration,performance}

# 2. Create requirements.txt with latest versions
cat > requirements.txt << 'EOF'
# Core
pytest>=9.0.0
pytest-asyncio>=1.3.0
pytest-cov>=6.0.0
hypothesis>=6.100.0

# TUI Framework
textual>=4.0.0

# Compression
lz4>=4.3.0
cramjam>=2.6.0  # Alternative fast compression

# Type checking & Linting
mypy>=1.15.0
ruff>=0.8.0
types-python-lz4>=0.1.0

# Optional
python-rapidjson>=1.20
EOF

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import textual; print(f'Textual {textual.__version__}')"
pytest --version
ruff --version
```

---

## PHASE COMPLETED: Core Foundation (1.1-1.3)

✅ Task 1.1: Project Setup & Utils Module - DONE
✅ Task 1.2: Core Module - Config & Event Bus - DONE
✅ Task 1.3: Entity Data Models - DONE

---

## PHASE 2: TUI Integration & Testing (NEW - P0)

### Task TUI-1: Menu Screen TDD

**Priority:** P0 (Critical)
**Status:** TODO

**Step 1: Create failing test**

```python
# tests/integration/test_tui_menu.py
"""TUI Menu tests - TDD approach."""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config

config.ensure_directories()

@pytest.fixture
def app():
    return DNDRoguelikeApp()

class TestMenuScreen:
    """Test menu screen functionality."""

    async def test_menu_navigates_to_character_creation(self, app):
        """Clicking New Game should go to character creation screen."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Click New Game button
            await pilot.click("#btn_new")
            await pilot.pause()
            
            # Should be on character creation screen
            assert "character" in str(app.screen).lower()

    async def test_menu_has_new_game_button(self, app):
        """Menu should have a clickable New Game button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Button should exist
            btn = app.query_one("#btn_new")
            assert btn is not None

    async def test_menu_has_continue_button(self, app):
        """Menu should have a Continue button."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            btn = app.query_one("#btn_continue")
            assert btn is not None

    async def test_quit_exits_app(self, app):
        """Clicking Quit should exit the app."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Click quit button
            await pilot.click("#btn_quit")
            await pilot.pause()
            
            # App should have exited
            assert app.is_exiting or len(app.screen.stack) == 0
```

**Step 2: Run test - EXPECTED TO FAIL**

**Step 3: Fix bugs**

**Step 4: Verify test passes**

---

### Task TUI-2: Character Creation Screen TDD

**Priority:** P0 (Critical)
**Status:** TODO

**Step 1: Create failing test**

```python
# tests/integration/test_tui_character.py
"""TUI Character Creation tests - TDD approach."""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config

config.ensure_directories()

@pytest.fixture
def app():
    return DNDRoguelikeApp()

class TestCharacterCreation:
    """Test character creation flow."""

    async def test_can_enter_character_name(self, app):
        """User should be able to enter character name."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Navigate to character creation
            await pilot.click("#btn_new")
            await pilot.pause()
            
            # Type name character by character
            for char in "Hero":
                await pilot.press(char)
            await pilot.pause()
            
            # Press enter to confirm name
            await pilot.press("enter")
            await pilot.pause()
            
            # Should advance to class selection
            assert app.screen is not None

    async def test_can_select_class(self, app):
        """User should be able to select a class."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Navigate to character creation
            await pilot.click("#btn_new")
            await pilot.pause()
            
            # Enter name
            for char in "Test":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            
            # Select class with tab and enter
            await pilot.press("tab")  # Focus class buttons
            await pilot.press("enter")  # Select fighter
            await pilot.pause()
            
            # Should advance to race selection
            assert app.screen is not None

    async def test_can_start_game(self, app):
        """Completing character creation should start the game."""
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Full character creation flow
            await pilot.click("#btn_new")
            await pilot.pause()
            
            # Enter name
            for char in "Player":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            
            # Select class
            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            
            # Select race
            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            
            # Click Start button
            await pilot.click("#btn_start")
            await pilot.pause()
            
            # Should be on game screen
            assert "game" in str(app.screen).lower()
```

**Step 2: Run test - EXPECTED TO FAIL**

**Step 3: Fix bugs**

**Step 4: Verify test passes**

---

### Task TUI-3: Game Screen TDD

**Priority:** P0 (Critical)
**Status:** TODO

**Step 1: Create failing test**

```python
# tests/integration/test_tui_game.py
"""TUI Game Screen tests - TDD approach."""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig

config.ensure_directories()

@pytest.fixture
def app():
    return DNDRoguelikeApp()

@pytest.fixture
def setup_game(app):
    """Set up a game ready for testing."""
    async def _setup():
        engine = app.game_engine
        dungeon = DungeonGenerator(DungeonConfig(width=40, height=20)).generate()
        engine.current_map = dungeon
        engine.create_player("TestHero", "fighter", "human")
        engine.start()
        app.action_show_game()
        return app
    return _setup

class TestGameScreen:
    """Test game screen functionality."""

    async def test_movement_keys_work(self, app, setup_game):
        """Movement keys should move the player."""
        async with app.run_test() as pilot:
            await setup_game()
            await pilot.pause()
            
            player = app.game_engine.player
            initial_pos = player.position
            
            await pilot.press("e")  # Move east
            await pilot.pause()
            
            # Player should have moved
            assert player.position != initial_pos

    async def test_can_open_character_screen(self, app, setup_game):
        """Pressing 'c' should open character screen."""
        async with app.run_test() as pilot:
            await setup_game()
            await pilot.pause()
            
            await pilot.press("c")
            await pilot.pause()
            
            # Should be on character screen
            assert "character" in str(app.screen).lower()

    async def test_can_open_inventory_screen(self, app, setup_game):
        """Pressing 'i' should open inventory screen."""
        async with app.run_test() as pilot:
            await setup_game()
            await pilot.pause()
            
            await pilot.press("i")
            await pilot.pause()
            
            # Should be on inventory screen
            assert "inventory" in str(app.screen).lower()

    async def test_can_open_log_screen(self, app, setup_game):
        """Pressing 'l' should open log screen."""
        async with app.run_test() as pilot:
            await setup_game()
            await pilot.pause()
            
            await pilot.press("l")
            await pilot.pause()
            
            # Should be on log screen
            assert "log" in str(app.screen).lower()

    async def test_can_save_game(self, app, setup_game):
        """Pressing 's' should save the game."""
        async with app.run_test() as pilot:
            await setup_game()
            await pilot.pause()
            
            await pilot.press("s")
            await pilot.pause()
            
            # Game should be saved (verify file exists)
            save_dir = config.save_directory
            saves = list(save_dir.glob("*.json")) + list(save_dir.glob("*.sav"))
            assert len(saves) > 0
```

**Step 2: Run test - EXPECTED TO FAIL**

**Step 3: Fix bugs**

**Step 4: Verify test passes**

---

### Task TUI-4: User Flow Integration Test

**Priority:** P1
**Status:** TODO

**Step 1: Create full flow test**

```python
# tests/integration/test_user_flows.py
"""End-to-end user flow tests."""

import pytest
from src.tui.app import DNDRoguelikeApp
from src.core.config import config

config.ensure_directories()

class TestFullUserFlows:
    """Test complete user journeys."""

    async def test_complete_new_game_flow(self):
        """Test: Menu -> New Game -> Create Character -> Play."""
        app = DNDRoguelikeApp()
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # 1. Start at menu
            assert "menu" in str(app.screen).lower()
            
            # 2. Click New Game
            await pilot.click("#btn_new")
            await pilot.pause()
            
            # 3. Enter character name
            for char in "Adventure":
                await pilot.press(char)
            await pilot.press("enter")
            await pilot.pause()
            
            # 4. Select class (fighter)
            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            
            # 5. Select race (human)
            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            
            # 6. Start game
            await pilot.click("#btn_start")
            await pilot.pause()
            
            # 7. Verify on game screen
            assert "game" in str(app.screen).lower()
            
            # 8. Move around
            for _ in range(5):
                await pilot.press("e")
            await pilot.pause()
            
            # 9. Check character stats
            await pilot.press("c")
            await pilot.pause()
            
            # 10. Return to game
            await pilot.press("escape")
            await pilot.pause()
            
            # 11. Save game
            await pilot.press("s")
            await pilot.pause()
            
            # 12. Verify save exists
            saves = list(config.save_directory.glob("*.json"))
            assert len(saves) > 0
```

**Step 2: Run test - EXPECTED TO FAIL**

**Step 3: Fix bugs**

**Step 4: Verify test passes**

---

## Textual 4.x Compatibility Notes

When working on TUI code, remember:

### ✅ Supported
- `SCREENS` class dict for screen registration
- `push_screen("name")` / `pop_screen()` for navigation
- `query_one("#id")` to find widgets
- `app.run_test()` for testing
- `pilot.click("#btn_id")` for button clicks
- `pilot.press("key")` for key presses
- `widget.refresh()` to update display

### ❌ Not Supported
- `widget.update()` - does not exist
- `visible` parameter on Screen init
- `items` parameter on ListView init
- `get_screen_by_id()` - does not exist
- Custom CSS variables like `$surface`, `$accent`
- Pseudo-class `selected` on widgets

---

## Remaining Core Tasks

| Phase | Tasks | Description | Status |
|-------|-------|-------------|--------|
| 1 | 1.4-1.6 | World module (map, FOV, dungeon), Persistence | DONE |
| 2 | 2.1-2.4 | Combat, Character system, Enemy AI, Status effects | DONE |
| 3 | 3.1-3.3 | Game engine integration, Save compression, Concurrency | DONE |
| 4 | 4.1-4.5 | TUI (App, Widgets, Bindings, Screens, Themes) | IN PROGRESS |
| 5 | 5.1-5.3 | Integration tests, Performance, Edge cases | TODO |

---

## Quick Reference Commands

```bash
# Run all tests
pytest tests/ -v

# Run TUI tests only
pytest tests/integration/test_tui*.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Type check
mypy src/

# Lint
ruff check src/

# Format
ruff format src/

# All quality checks
pytest tests/ && mypy src/ && ruff check src/
```

---

## Notes for AI Agents

1. **Always use TDD**: Write failing test first, then implementation
2. **Commit frequently**: Every task completion should be a commit
3. **Run linters**: `ruff check` before every commit
4. **Type check**: `mypy src/` should pass
5. **No placeholder code**: Full implementations only
6. **Follow RFC specs**: Implement exactly as documented
7. **Handle edge cases**: Tests should cover them
8. **Test TUI with pilot**: Use `app.run_test()` and `pilot.click()`/`pilot.press()`
