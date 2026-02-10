# Implementation Tasks - AI Agent Ready

**Project:** D&D Roguelike Hybrid CLI Game
**Source:** RFC.md, PRD.md
**Purpose:** Fully executable tasks for AI agents without human supervision
**Last Updated:** 2026-02-09

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

## Phase 1: Core Foundation

### Task 1.1: Project Setup & Utils Module

**Priority:** P0 (Blocker)
**Complexity:** Low
**Files to Create:**

```
src/utils/
├── __init__.py
├── exceptions.py      # Custom exceptions
├── logger.py          # Logging utilities
└── validators.py      # Input validation

tests/unit/test_utils/
├── __init__.py
├── test_exceptions.py
├── test_logger.py
└── test_validators.py
```

**Step 1: Create exceptions.py**

```python
# src/utils/exceptions.py
"""Custom exceptions for the game."""

class GameError(Exception):
    """Base exception for all game errors."""
    pass


class SaveError(GameError):
    """Save/load related errors."""
    pass


class SaveCorruptionError(SaveError):
    """Save file is corrupted."""
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Save file '{filename}' is corrupted")


class SaveVersionError(SaveError):
    """Save file version is incompatible."""
    pass


class SaveNotFoundError(SaveError):
    """Save file does not exist."""
    pass


class CombatError(GameError):
    """Combat-related errors."""
    pass


class TargetNotFoundError(CombatError):
    """Target not found for attack."""
    pass


class InvalidActionError(GameError):
    """Player attempted invalid action."""
    pass


class MovementError(GameError):
    """Movement-related errors."""
    pass


class BlockedPathError(MovementError):
    """Path is blocked by obstacle."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        super().__init__(f"Path blocked at ({x}, {y})")


class ValidationError(GameError):
    """Input validation error."""
    pass
```

**Step 2: Create validators.py**

```python
# src/utils/validators.py
"""Input validation utilities."""

from typing import Tuple, Optional
from .exceptions import ValidationError


def validate_coordinate(x: int, y: int, width: int, height: int) -> Tuple[int, int]:
    """Validate and clamp coordinates to bounds."""
    return (
        max(0, min(x, width - 1)),
        max(0, min(y, height - 1))
    )


def validate_character_name(name: str) -> None:
    """Validate character name."""
    if not name:
        raise ValidationError("Character name cannot be empty")
    if len(name) > 50:
        raise ValidationError("Character name cannot exceed 50 characters")
    if not name.replace(" ", "").replace("-", "").replace("'", "").isalnum():
        raise ValidationError("Character name contains invalid characters")


def validate_direction(direction: str) -> str:
    """Validate and normalize direction input."""
    direction_map = {
        "n": "north", "north": "north",
        "s": "south", "south": "south",
        "e": "east", "east": "east",
        "w": "west", "west": "west",
    }
    normalized = direction.lower()
    if normalized not in direction_map:
        raise ValidationError(f"Invalid direction: {direction}")
    return direction_map[normalized]


def validate_attribute_value(value: int, attr_name: str) -> int:
    """Validate attribute value (6-20)."""
    if not 6 <= value <= 20:
        raise ValidationError(f"{attr_name} must be between 6 and 20, got {value}")
    return value
```

**Step 3: Create logger.py**

```python
# src/utils/logger.py
"""Logging utilities for the game."""

import logging
import sys
from pathlib import Path
from typing import Optional


class GameLogger:
    """Game logger with file and console output."""

    def __init__(self, name: str = "dnd_roguelike", log_file: Optional[Path] = None, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        # Console handler
        console = logging.StreamHandler(sys.stderr)
        console.setLevel(level)
        console.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        ))
        self.logger.addHandler(console)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self.logger.addHandler(file_handler)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg)


# Default logger instance
default_logger: Optional[GameLogger] = None


def get_logger(name: str = "dnd_roguelike", log_file: Optional[Path] = None) -> GameLogger:
    """Get or create a logger instance."""
    global default_logger
    if default_logger is None:
        default_logger = GameLogger(name, log_file)
    return default_logger
```

**Step 4: Create test_exceptions.py**

```python
# tests/unit/test_utils/test_exceptions.py
"""Tests for custom exceptions."""

import pytest
from src.utils.exceptions import (
    GameError, SaveError, SaveCorruptionError, SaveVersionError,
    CombatError, TargetNotFoundError, MovementError, BlockedPathError,
    ValidationError
)


class TestExceptionHierarchy:
    def test_game_error_is_base(self):
        assert issubclass(SaveError, GameError)
        assert issubclass(CombatError, GameError)
        assert issubclass(MovementError, GameError)

    def test_save_error_hierarchy(self):
        assert issubclass(SaveCorruptionError, SaveError)
        assert issubclass(SaveVersionError, SaveError)

    def test_combat_error_hierarchy(self):
        assert issubclass(TargetNotFoundError, CombatError)

    def test_movement_error_hierarchy(self):
        assert issubclass(BlockedPathError, MovementError)
        assert issubclass(MovementError, GameError)


class TestSaveCorruptionError:
    def test_error_message_includes_filename(self):
        err = SaveCorruptionError("test.sav")
        assert "test.sav" in str(err)
        assert "corrupted" in str(err).lower()

    def test_error_stores_filename(self):
        err = SaveCorruptionError("save.sav")
        assert err.filename == "save.sav"


class TestBlockedPathError:
    def test_error_message_includes_coordinates(self):
        err = BlockedPathError(5, 10)
        assert "5" in str(err)
        assert "10" in str(err)
        assert "blocked" in str(err).lower()

    def test_error_stores_coordinates(self):
        err = BlockedPathError(3, 7)
        assert err.x == 3
        assert err.y == 7


class TestValidationError:
    def test_validation_error_is_game_error(self):
        assert issubclass(ValidationError, GameError)
```

**Step 5: Create test_validators.py**

```python
# tests/unit/test_utils/test_validators.py
"""Tests for validators."""

import pytest
from src.utils.validators import (
    validate_coordinate, validate_character_name,
    validate_direction, validate_attribute_value
)
from src.utils.exceptions import ValidationError


class TestValidateCoordinate:
    def test_valid_coordinate_returns_unchanged(self):
        assert validate_coordinate(5, 5, 100, 100) == (5, 5)
        assert validate_coordinate(0, 0, 100, 100) == (0, 0)
        assert validate_coordinate(99, 99, 100, 100) == (99, 99)

    def test_negative_coordinates_clamped(self):
        assert validate_coordinate(-1, 5, 100, 100) == (0, 5)
        assert validate_coordinate(5, -10, 100, 100) == (5, 0)

    def test_out_of_bounds_clamped(self):
        assert validate_coordinate(101, 50, 100, 100) == (99, 50)
        assert validate_coordinate(50, 200, 100, 100) == (50, 99)


class TestValidateCharacterName:
    def test_valid_name_passes(self):
        validate_character_name("TestChar")
        validate_character_name("Sir Lancelot")
        validate_character_name("Dark-Knight")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_character_name("")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError, match="50"):
            validate_character_name("a" * 51)

    def test_invalid_characters_raise(self):
        with pytest.raises(ValidationError, match="invalid"):
            validate_character_name("test@char")


class TestValidateDirection:
    def test_valid_directions_normalized(self):
        assert validate_direction("n") == "north"
        assert validate_direction("N") == "north"
        assert validate_direction("north") == "north"
        assert validate_direction("s") == "south"

    def test_invalid_direction_raises(self):
        with pytest.raises(ValidationError, match="Invalid direction"):
            validate_direction("up")


class TestValidateAttributeValue:
    def test_valid_attribute_passes(self):
        assert validate_attribute_value(10, "strength") == 10
        assert validate_attribute_value(6, "dexterity") == 6
        assert validate_attribute_value(20, "intelligence") == 20

    def test_below_minimum_raises(self):
        with pytest.raises(ValidationError, match="must be between 6 and 20"):
            validate_attribute_value(5, "constitution")

    def test_above_maximum_raises(self):
        with pytest.raises(ValidationError, match="must be between 6 and 20"):
            validate_attribute_value(21, "wisdom")
```

**Step 6: Run Tests**

```bash
cd /Users/mac/WebApps/oss/dnd-hybrid
pytest tests/unit/test_utils/ -v
```

**Expected:** All tests pass

**Step 7: Commit**

```bash
git add src/utils/ tests/unit/test_utils/
git commit -m "feat(utils): add exceptions, validators, and logger modules

- Add GameError base exception with hierarchy
- Add SaveError, CombatError, MovementError categories
- Add validation utilities for coords, names, directions
- Add GameLogger with file and console output"
```

---

### Task 1.2: Core Module - Config & Event Bus

**Priority:** P0 (Blocker)
**Complexity:** Medium
**Files to Create:**

```
src/core/
├── __init__.py
├── config.py          # Game configuration
├── event_bus.py       # Event-driven communication
└── game_engine.py     # Main game loop (stub)

tests/unit/test_core/
├── __init__.py
├── test_config.py
└── test_event_bus.py
```

**Step 1: Create config.py**

```python
# src/core/config.py
"""Game configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os


@dataclass
class GameConfig:
    """Game configuration with defaults."""

    # Map settings
    map_width: int = 80
    map_height: int = 24
    min_room_size: int = 5
    max_room_size: int = 15
    min_rooms: int = 5
    max_rooms: int = 10

    # Game settings
    tick_rate: float = 0.1  # seconds
    fov_radius: int = 8
    debug: bool = False

    # Paths
    save_directory: Path = field(default_factory=lambda: Path.home() / ".dnd_roguelike" / "saves")
    log_directory: Path = field(default_factory=lambda: Path.home() / ".dnd_roguelike" / "logs")

    # Combat
    base_enemy_scaling: float = 1.0  # per floor

    @classmethod
    def from_env(cls) -> "GameConfig":
        """Load config from environment variables."""
        return cls(
            map_width=int(os.getenv("DND_MAP_WIDTH", "80")),
            map_height=int(os.getenv("DND_MAP_HEIGHT", "24")),
            debug=os.getenv("DND_DEBUG", "").lower() == "true",
            save_directory=Path(os.getenv("DND_SAVE_DIR", "")) or cls().save_directory,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "GameConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def ensure_directories(self) -> None:
        """Create save and log directories."""
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.log_directory.mkdir(parents=True, exist_ok=True)


# Global config instance
config = GameConfig.from_env()
```

**Step 2: Create event_bus.py**

```python
# src/core/event_bus.py
"""Event-driven communication system."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Set
from collections import defaultdict
import asyncio


@dataclass
class Event:
    """Base event class."""

    type: str
    data: Dict[str, Any]
    source: str = "unknown"


class EventBus:
    """Pub/sub event system with sync and async support."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to synchronous events."""
        self._subscribers[event_type].append(callback)

    def subscribe_async(self, event_type: str, callback: Callable) -> None:
        """Subscribe to asynchronous events."""
        self._async_subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe a callback."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
        if callback in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(callback)

    def publish(self, event: Event) -> None:
        """Publish a synchronous event."""
        for callback in self._subscribers.get(event.type, []):
            callback(event)

    async def publish_async(self, event: Event) -> None:
        """Publish an asynchronous callback in self._subscribers.get(event.type, []):
 event."""
        for            callback(event)

        for callback in self._async_subscribers.get(event.type, []):
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)


# Event types
class GameEvents:
    PLAYER_ACTION = "player_action"
    COMBAT = "combat"
    MOVEMENT = "movement"
    TICK = "tick"
    GAME_STATE_CHANGE = "game_state_change"
    FLOOR_CHANGE = "floor_change"
    LEVEL_UP = "level_up"
    DEATH = "death"
    SAVE = "save"
    LOAD = "load"


# Global event bus
event_bus = EventBus()
```

**Step 3: Create game_engine.py (stub)**

```python
# src/core/game_engine.py
"""Main game engine (stub implementation)."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .config import config
from .event_bus import EventBus, event_bus, GameEvents


class GameState(Enum):
    """Game state."""
    MENU = auto()
    PLAYING = auto()
    COMBAT = auto()
    PAUSED = auto()
    GAMEOVER = auto()


@dataclass
class GameEngine:
    """Main game engine."""

    state: GameState = GameState.MENU
    event_bus: EventBus = field(default_factory=lambda: event_bus)
    current_floor: int = 1
    turn_count: int = 0

    def start(self) -> None:
        """Start the game."""
        self.state = GameState.PLAYING
        self.event_bus.publish(GameEvents.GAME_STATE_CHANGE, {"state": self.state})

    def stop(self) -> None:
        """Stop the game."""
        self.state = GameState.GAMEOVER
        self.event_bus.publish(GameEvents.GAME_STATE_CHANGE, {"state": self.state})

    def pause(self) -> None:
        """Pause the game."""
        self.state = GameState.PAUSED

    def resume(self) -> None:
        """Resume the game."""
        self.state = GameState.PLAYING

    def get_state(self) -> dict:
        """Get current game state for serialization."""
        return {
            "state": self.state.name,
            "current_floor": self.current_floor,
            "turn_count": self.turn_count,
        }
```

**Step 4: Create test_config.py**

```python
# tests/unit/test_core/test_config.py
"""Tests for game config."""

import pytest
from src.core.config import GameConfig, config


class TestGameConfigDefaults:
    def test_default_map_size(self):
        cfg = GameConfig()
        assert cfg.map_width == 80
        assert cfg.map_height == 24

    def test_default_tick_rate(self):
        cfg = GameConfig()
        assert cfg.tick_rate == 0.1

    def test_default_fov_radius(self):
        cfg = GameConfig()
        assert cfg.fov_radius == 8

    def test_default_room_sizes(self):
        cfg = GameConfig()
        assert cfg.min_room_size == 5
        assert cfg.max_room_size == 15


class TestGameConfigFromDict:
    def test_partial_override(self):
        cfg = GameConfig.from_dict({"map_width": 100, "debug": True})
        assert cfg.map_width == 100
        assert cfg.debug is True
        assert cfg.map_height == 24  # default

    def test_ignore_unknown_fields(self):
        cfg = GameConfig.from_dict({"unknown_field": "value"})
        assert cfg.map_width == 80  # unchanged


class TestConfigSingleton:
    def test_config_is_singleton(self):
        from src.core.config import config
        assert isinstance(config, GameConfig)
```

**Step 5: Create test_event_bus.py**

```python
# tests/unit/test_core/test_event_bus.py
"""Tests for event bus."""

import pytest
from unittest.mock import Mock
from src.core.event_bus import EventBus, Event, GameEvents


class TestEventBusSync:
    def test_sync_subscriber_receives_event(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe("test_event", handler)
        bus.publish(Event("test_event", {"data": "value"}))

        assert len(received) == 1
        assert received[0].data["data"] == "value"

    def test_multiple_subscribers(self):
        bus = EventBus()
        received1 = []
        received2 = []

        bus.subscribe("event", lambda e: received1.append(e))
        bus.subscribe("event", lambda e: received2.append(e))
        bus.publish(Event("event", {}))

        assert len(received1) == 1
        assert len(received2) == 1

    def test_unsubscribe_removes_handler(self):
        bus = EventBus()
        handler = Mock()
        bus.subscribe("event", handler)
        bus.unsubscribe("event", handler)
        bus.publish(Event("event", {}))
        handler.assert_not_called()

    def test_unsubscribe_one_preserves_others(self):
        bus = EventBus()
        handler1 = Mock()
        handler2 = Mock()
        bus.subscribe("event", handler1)
        bus.subscribe("event", handler2)
        bus.unsubscribe("event", handler1)
        bus.publish(Event("event", {}))
        handler1.assert_not_called()
        handler2.assert_called()


class TestEventBusAsync:
    @pytest.mark.asyncio
    async def test_async_subscriber_receives_event(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe_async("test_event", handler)
        await bus.publish_async(Event("test_event", {"data": "value"}))

        assert len(received) == 1


class TestEventStructure:
    def test_event_has_type_and_data(self):
        event = Event("combat", {"damage": 10})
        assert event.type == "combat"
        assert event.data["damage"] == 10

    def test_event_default_source(self):
        event = Event("test", {})
        assert event.source == "unknown"
```

**Step 6: Run Tests**

```bash
pytest tests/unit/test_core/ -v
```

**Step 7: Commit**

```bash
git add src/core/ tests/unit/test_core/
git commit -m "feat(core): add config and event bus

- Add GameConfig with environment variable support
- Add EventBus with sync/async pub/sub
- Add GameState enum and stub GameEngine
- Add Event dataclass with type and data"
```

---

### Task 1.3: Entity Data Models

**Priority:** P0 (Blocker)
**Complexity:** Medium
**Files to Create:**

```
src/entities/
├── __init__.py
├── entity.py          # Base entity class
├── character.py       # Character implementation
├── enemy.py           # Enemy implementation
└── item.py            # Item implementation

tests/unit/test_entities/
├── __init__.py
├── test_entity.py
├── test_character.py
├── test_enemy.py
└── test_item.py
```

**Step 1: Create enums and base entity**

```python
# src/entities/entity.py
"""Base entity class."""

from dataclasses import dataclass, field
from typing import Optional, Tuple
from enum import Enum, auto


class EntityType(Enum):
    """Entity types."""
    PLAYER = auto()
    ENEMY = auto()
    ITEM = auto()
    FEATURE = auto()


@dataclass
class Entity:
    """Base entity class."""

    id: str
    name: str
    entity_type: EntityType
    position: Tuple[int, int] = (0, 0)
    alive: bool = True

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def move_to(self, x: int, y: int) -> None:
        """Move entity to position."""
        self.position = (x, y)
```

**Step 2: Create character.py**

```python
# src/entities/character.py
"""Character entity."""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from .entity import Entity, EntityType


# XP thresholds for levels 1-20
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]


def attribute_modifier(score: int) -> int:
    """Calculate attribute modifier from score."""
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus from level."""
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6


def level_from_xp(experience: int) -> int:
    """Calculate level from XP."""
    for i, threshold in enumerate(XP_THRESHOLDS):
        if experience < threshold:
            return i
    return 20


@dataclass
class Character(Entity):
    """Player character."""

    entity_type: EntityType = field(default=EntityType.PLAYER, init=False)

    # Core
    level: int = 1
    experience: int = 0
    character_class: str = "fighter"
    race: str = "human"
    background: str = "soldier"

    # Attributes (6-20)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Derived (use properties)
    hit_points: int = 10
    temporary_hp: int = 0
    exhaustion_level: int = 0
    class_resources: Dict[str, int] = field(default_factory=dict)

    # State
    conditions: List = field(default_factory=list)
    death_save_successes: int = 0
    death_save_failures: int = 0

    # History
    damage_dealt: int = 0
    damage_taken: int = 0
    turns_survived: int = 0
    kills: Dict[str, int] = field(default_factory=dict)

    # Position
    current_floor: int = 1

    @property
    def strength_mod(self) -> int:
        return attribute_modifier(self.strength)

    @property
    def dexterity_mod(self) -> int:
        return attribute_modifier(self.dexterity)

    @property
    def constitution_mod(self) -> int:
        return attribute_modifier(self.constitution)

    @property
    def intelligence_mod(self) -> int:
        return attribute_modifier(self.intelligence)

    @property
    def wisdom_mod(self) -> int:
        return attribute_modifier(self.wisdom)

    @property
    def charisma_mod(self) -> int:
        return attribute_modifier(self.charisma)

    @property
    def armor_class(self) -> int:
        """AC = 10 + dex modifier."""
        return 10 + self.dexterity_mod

    @property
    def max_hp(self) -> int:
        """Max HP (simplified - real implementation uses class)."""
        return 10 + (self.level - 1) * (5 + self.constitution_mod)

    @property
    def proficiency_bonus(self) -> int:
        return proficiency_bonus(self.level)

    @property
    def current_hp(self) -> int:
        return self.hit_points

    @property
    def is_dying(self) -> bool:
        """Character is at 0 HP and alive."""
        return self.hit_points <= 0 and self.alive

    def take_damage(self, damage: int) -> int:
        """Take damage, returns actual damage taken."""
        if self.temporary_hp > 0:
            temp_used = min(self.temporary_hp, damage)
            self.temporary_hp -= temp_used
            damage -= temp_used
        self.hit_points = max(0, self.hit_points - damage)
        self.damage_taken += damage
        if self.hit_points == 0:
            self.alive = False
        return damage

    def heal(self, amount: int) -> int:
        """Heal, returns actual healing."""
        old_hp = self.hit_points
        self.hit_points = min(self.max_hp, self.hit_points + amount)
        return self.hit_points - old_hp

    def add_experience(self, xp: int) -> None:
        """Add XP and handle level ups."""
        self.experience += xp
        new_level = level_from_xp(self.experience)
        while self.level < new_level:
            self.level_up()

    def level_up(self) -> None:
        """Level up the character."""
        self.level += 1
        # HP increase
        hp_gain = 5 + self.constitution_mod  # Simplified
        self.hit_points = min(self.max_hp, self.hit_points + hp_gain)
```

**Step 3: Create item.py**

```python
# src/entities/item.py
"""Item entity."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto
from .entity import Entity, EntityType


class ItemType(Enum):
    """Item types."""
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    SCROLL = auto()
    RING = auto()
    AMMO = auto()
    TREASURE = auto()
    FOOD = auto()


class Rarity(Enum):
    """Item rarity tiers."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


class WeaponType(Enum):
    """Weapon types."""
    SIMPLE_MELEE = auto()
    MARTIAL_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_RANGED = auto()


class ArmorType(Enum):
    """Armor types."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()


@dataclass
class Item(Entity):
    """Item entity."""

    entity_type: EntityType = field(default=EntityType.ITEM, init=False)

    # Classification
    item_type: ItemType = ItemType.TREASURE
    rarity: Rarity = Rarity.COMMON

    # Physical
    weight: float = 0.0
    quantity: int = 1
    stackable: bool = False
    max_stack: int = 1

    # Magical
    attunement_required: bool = False
    attunement_slots: int = 0
    magical_bonus: int = 0
    charges: int = 0
    max_charges: int = 0

    # Description
    description: str = ""
    lore_text: Optional[str] = None

    # For weapons
    weapon_type: Optional[WeaponType] = None
    damage_die: str = "1d4"  # notation like "1d8"
    damage_type: Optional[str] = None
    properties: List[str] = field(default_factory=list)

    # For armor
    armor_type: Optional[ArmorType] = None
    base_ac: int = 10
    stealth_disadvantage: bool = False

    # For potions/scrolls
    spell_id: Optional[str] = None
    uses_remaining: int = 1

    def can_stack_with(self, other: "Item") -> bool:
        """Check if items can stack."""
        if not self.stackable or not other.stackable:
            return False
        if self.name != other.name:
            return False
        if self.item_type != other.item_type:
            return False
        return True

    def add(self, quantity: int) -> None:
        """Add to stack."""
        if not self.stackable:
            return
        self.quantity = min(self.quantity + quantity, self.max_stack)

    def remove(self, quantity: int) -> int:
        """Remove from stack, returns actual removed."""
        removed = min(quantity, self.quantity)
        self.quantity -= removed
        return removed

    @property
    def attack_bonus(self) -> int:
        """Attack bonus from magical item."""
        return self.magical_bonus

    @property
    def total_weight(self) -> float:
        """Total weight of stack."""
        return self.weight * self.quantity
```

**Step 4: Create enemy.py**

```python
# src/entities/enemy.py
"""Enemy entity."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum, auto
from .entity import Entity, EntityType


class AIType(Enum):
    """Enemy AI behavior types."""
    PASSIVE = auto()
    AGGRESSIVE = auto()
    DEFENSIVE = auto()
    PATROL = auto()


class EnemyType(Enum):
    """Enemy types."""
    BEAST = auto()
    UNDEAD = auto()
    ABERRATION = auto()
    CONSTRUCT = auto()
    DRAGON = auto()
    ELEMENTAL = auto()
    FEY = auto()
    FIEND = auto()
    GIANT = auto()
    HUMANOID = auto()
    MONSTROSITY = auto()
    OOZE = auto()
    PLANT = auto()


@dataclass
class Enemy(Entity):
    """Enemy entity."""

    entity_type: EntityType = field(default=EntityType.ENEMY, init=False)

    # Classification
    enemy_type: EnemyType = EnemyType.HUMANOID
    cr: float = 1.0  # Challenge rating

    # Stats
    armor_class: int = 10
    max_hp: int = 10
    current_hp: int = 10
    attack_bonus: int = 2
    damage_per_round: int = 5

    # Attributes
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Behavior
    ai_type: AIType = AIType.AGGRESSIVE
    aggro_range: int = 5
    patrol_route: Optional[List[Tuple[int, int]]] = None
    abilities: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    immunities: List[str] = field(default_factory=list)

    # State
    status_effects: List = field(default_factory=list)

    @property
    def strength_mod(self) -> int:
        return (self.strength - 10) // 2

    @property
    def dexterity_mod(self) -> int:
        return (self.dexterity - 10) // 2

    def take_damage(self, damage: int) -> int:
        """Take damage."""
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp == 0:
            self.alive = False
        return damage

    def heal(self, amount: int) -> int:
        """Heal."""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def can_see(self, target_pos: Tuple[int, int], map_fov: set) -> bool:
        """Check if enemy can see target position."""
        return target_pos in map_fov

    def is_in_aggro_range(self, target_pos: Tuple[int, int]) -> bool:
        """Check if target is within aggro range."""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        return (dx * dx + dy * dy) ** 0.5 <= self.aggro_range
```

**Step 5: Create test files and run tests**

```bash
# Create __init__.py files
touch src/entities/__init__.py
touch tests/unit/test_entities/__init__.py

# Create tests
cat > tests/unit/test_entities/test_character.py << 'EOF'
"""Tests for Character class."""

import pytest
from src.entities.character import (
    Character, attribute_modifier, proficiency_bonus, level_from_xp
)


class TestAttributeModifier:
    def test_modifier_table(self):
        assert attribute_modifier(1) == -5
        assert attribute_modifier(8) == -1
        assert attribute_modifier(10) == 0
        assert attribute_modifier(12) == 1
        assert attribute_modifier(16) == 3
        assert attribute_modifier(20) == 5


class TestProficiencyBonus:
    def test_levels_1_to_4(self):
        assert proficiency_bonus(1) == 2
        assert proficiency_bonus(4) == 2

    def test_levels_5_to_8(self):
        assert proficiency_bonus(5) == 3
        assert proficiency_bonus(8) == 3

    def test_levels_9_to_12(self):
        assert proficiency_bonus(9) == 4
        assert proficiency_bonus(12) == 4


class TestCharacter:
    def test_character_creation(self):
        char = Character(
            id="test", name="TestChar",
            character_class="fighter", race="human",
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=12, charisma=8
        )
        assert char.id == "test"
        assert char.alive is True

    def test_derived_stats(self):
        char = Character(
            id="test", name="Test", character_class="fighter", race="human",
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=12, charisma=8
        )
        assert char.strength_mod == 3
        assert char.dexterity_mod == 2
        assert char.armor_class == 12  # 10 + dex

    def test_take_damage(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         hit_points=20)
        damage = char.take_damage(5)
        assert char.current_hp == 15
        assert char.damage_taken == 5

    def test_take_damage_with_temp_hp(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         hit_points=20, temporary_hp=10)
        damage = char.take_damage(5)
        assert char.temporary_hp == 5
        assert char.current_hp == 20

    def test_level_up(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         constitution=14, hit_points=10)
        char.level_up()
        assert char.level == 2

    def test_xp_level_up(self):
        char = Character(id="test", name="Test", character_class="fighter", race="human",
                         constitution=14, experience=0)
        char.add_experience(1000)  # Should reach level 5
        assert char.level == 5
EOF

cat > tests/unit/test_entities/test_item.py << 'EOF'
"""Tests for Item class."""

import pytest
from src.entities.item import Item, ItemType, Rarity, WeaponType


class TestItem:
    def test_item_creation(self):
        item = Item(id="sword1", name="Longsword", item_type=ItemType.WEAPON)
        assert item.id == "sword1"
        assert item.alive is True

    def test_item_stackable(self):
        potion = Item(
            id="p1", name="Health Potion", item_type=ItemType.POTION,
            rarity=Rarity.COMMON, stackable=True, quantity=5, max_stack=99
        )
        assert potion.can_stack_with(potion)

    def test_stack_different_items(self):
        potion = Item(id="p1", name="Health Potion", item_type=ItemType.POTION, stackable=True)
        mana = Item(id="p2", name="Mana Potion", item_type=ItemType.POTION, stackable=True)
        assert not potion.can_stack_with(mana)

    def test_item_add_quantity(self):
        potion = Item(id="p1", name="Potion", stackable=True, quantity=5, max_stack=99)
        potion.add(3)
        assert potion.quantity == 8

    def test_item_remove_quantity(self):
        potion = Item(id="p1", name="Potion", stackable=True, quantity=5)
        removed = potion.remove(2)
        assert removed == 2
        assert potion.quantity == 3

    def test_non_stackable_cannot_add(self):
        sword = Item(id="s1", name="Sword", stackable=False, quantity=1)
        sword.add(5)  # Should not change
        assert sword.quantity == 1
EOF

cat > tests/unit/test_entities/test_enemy.py << 'EOF'
"""Tests for Enemy class."""

import pytest
from src.entities.enemy import Enemy, AIType, EnemyType


class TestEnemy:
    def test_enemy_creation(self):
        enemy = Enemy(
            id="goblin1", name="Goblin", enemy_type=EnemyType.HUMANOID,
            cr=0.25, armor_class=15, max_hp=7, position=(5, 5)
        )
        assert enemy.id == "goblin1"
        assert enemy.alive is True

    def test_enemy_aggressive_default(self):
        enemy = Enemy(id="test", name="Test", ai_type=AIType.AGGRESSIVE, aggro_range=5)
        assert enemy.ai_type == AIType.AGGRESSIVE

    def test_enemy_in_aggro_range(self):
        enemy = Enemy(id="test", name="Test", position=(5, 5), aggro_range=5)
        assert enemy.is_in_aggro_range((7, 5)) is True  # distance 2
        assert enemy.is_in_aggro_range((15, 5)) is False  # distance 10

    def test_enemy_take_damage(self):
        enemy = Enemy(id="test", name="Test", max_hp=10, current_hp=10)
        enemy.take_damage(4)
        assert enemy.current_hp == 6

    def test_enemy_dies_at_zero(self):
        enemy = Enemy(id="test", name="Test", max_hp=10, current_hp=5)
        enemy.take_damage(5)
        assert enemy.current_hp == 0
        assert enemy.alive is False
EOF

# Run tests
pytest tests/unit/test_entities/ -v
```

**Step 6: Commit**

```bash
git add src/entities/ tests/unit/test_entities/
git commit -m "feat(entities): add data models for Entity, Character, Item, Enemy

- Add base Entity class with position and alive state
- Add Character with 6 attributes, derived stats, XP/leveling
- Add Item with stacking, equipment properties
- Add Enemy with AI types, aggro, scaling"
```

---

## Continue Tasks...

**Tasks 1.4-5.3 follow the same pattern:**
1. Write failing test
2. Implement minimal code
3. Run tests
4. Commit

### Summary of Remaining Tasks

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1.4-1.6 | World module (map, FOV, dungeon), Persistence |
| 2 | 2.1-2.4 | Combat, Character system, Enemy AI, Status effects |
| 3 | 3.1-3.3 | Game engine integration, Save compression, Concurrency |
| 4 | 4.1-4.5 | TUI (App, Widgets, Bindings, Screens, Themes) |
| 5 | 5.1-5.3 | Integration tests, Performance, Edge cases |

---

## Quick Reference Commands

```bash
# Run all tests
pytest tests/ -v

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

1. **Always use TDD**: Write test first, then implementation
2. **Commit frequently**: Every task completion should be a commit
3. **Run linters**: `ruff check` before every commit
4. **Type check**: `mypy src/` should pass
5. **No placeholder code**: Full implementations only
6. **Follow RFC specs**: Implement exactly as documented
7. **Handle edge cases**: Tests should cover them
