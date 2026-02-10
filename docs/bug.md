# Bug Documentation

This file documents bugs found during development and their fixes.

## Bugs Found

### Bug 1: Missing main.css file
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The TUI application was looking for `src/tui/styles/main.css` which didn't exist.

**Fix:** Created the `src/tui/styles/main.css` file with basic styling.

---

### Bug 2: Dungeon Generator BSP Split Logic
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The BSP dungeon generator was not creating any rooms. The split conditions allowed splits that left children too small to be split further, causing the algorithm to fail.

**Root Cause:** In `_build_bsp()`, the condition for horizontal/vertical splitting only checked if the current node was large enough, but didn't ensure that children would be large enough to potentially split again.

**Fix:** Added additional constraint `node.height >= self.config.min_room_size * 2` to the `can_split_horizontally` check and similar for vertical splits.

**File:** `src/world/dungeon_generator.py`

---

### Bug 3: Dungeon Generator Rooms Not Synced to Map
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The dungeon generator was populating its internal `self.rooms` list but not syncing it to `self.map.rooms`.

**Fix:** Added `self.map.rooms = self.rooms` after room carving in `_generate_bsp_rooms()`.

**File:** `src/world/dungeon_generator.py`

---

### Bug 4: Textual CSS Theme Variables
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The `themes.css` file used custom theme variables like `$surface-light`, `$accent`, etc. that aren't valid in Textual CSS.

**Fix:** Rewrote `themes.css` to use direct color values instead of custom variables.

**File:** `src/tui/styles/themes.css`

---

### Bug 5: Textual CSS Unknown Pseudo-classes
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The `themes.css` used pseudo-classes like `selected` that don't exist in Textual.

**Fix:** Removed invalid pseudo-class selectors from the CSS.

**File:** `src/tui/styles/themes.css`

---

### Bug 6: Screen visible Parameter
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** The `Screen` class in newer Textual versions doesn't accept a `visible` parameter in `__init__`.

**Fix:** Removed `visible=False` from Screen composition and use `push_screen()`/`pop_screen()` for navigation instead.

**File:** `src/tui/app.py`

---

### Bug 7: ListView items Parameter
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** `ListView` in newer Textual versions doesn't accept an `items` parameter in `__init__`.

**Fix:** Removed the `items=[]` parameter from ListView initialization in InventoryScreen.

**File:** `src/tui/screens/__init__.py`

---

### Bug 8: Screen Navigation API
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** Used `get_screen_by_id()` which doesn't exist in Textual. Also used `visible` attribute on screens.

**Fix:** 
- Added `SCREENS` class attribute to register screens by name
- Simplified compose to only yield Header and Footer
- Use `push_screen("screen_name")` for navigation

**File:** `src/tui/app.py`

---

### Bug 9: Widget render() Method
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** Widgets used `self.update()` which doesn't exist in Textual 4.x. Also `render()` method returned `None` instead of `str`.

**Fix:** Changed all widgets to return strings from `render()` method:
- `MapWidget.render()` returns `str`
- `StatusWidget.render()` returns `str`
- `CombatWidget.render()` returns `str`
- `LogWidget.render()` returns `str`

**File:** `src/tui/widgets/__init__.py`

---

### Bug 10: Dungeon Generator Only Creating 2-3 Rooms
**Date:** 2026-02-10
**Severity:** High
**Status:** Fixed

**Description:** BSP dungeon generator was only creating 2-3 rooms even when configured for 8-12 rooms.

**Root Cause:** The split logic was stopping too early. The algorithm kept splitting horizontally which resulted in thin strips that couldn't split further.

**Fix:** 
- Changed split conditions to check both dimensions
- Added logic to prefer splitting the larger dimension
- Increased max_depth to 8

**File:** `src/world/dungeon_generator.py`

---

## Known Remaining Issues

### LSP Type Errors
There are many LSP type errors in the codebase related to:
- Optional types not being handled (e.g., `game_engine` could be None)
- `render()` method return type mismatches
- Various attribute access on potentially None objects

These are type checking warnings, not runtime errors. They don't affect functionality but should be addressed for code quality.

---

## Notes for Future Development

1. **Textual Version:** The codebase was developed for Textual 4.x. Some APIs have changed from earlier versions.

2. **Screen Management:** In modern Textual, screens are registered via `SCREENS` dict and managed via `push_screen()`/`pop_screen()`.

3. **CSS Variables:** Custom theme variables aren't supported in Textual CSS. Use direct color values.

4. **Widget API:** Some widget initialization parameters have changed (e.g., `ListView` no longer accepts `items`).
