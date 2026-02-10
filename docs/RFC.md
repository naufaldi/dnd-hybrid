# Request for Comments (RFC)

## D&D Roguelike Hybrid CLI Game Technical Design

**RFC Number:** 001  
**Status:** Draft  
**Created:** 2026-02-09

---

## 1. Overview

This RFC describes the technical architecture for a D&D Roguelike Hybrid CLI game. The implementation will be structured as a modular, testable codebase designed to stress test LLM capabilities across coding, algorithms, state management, and edge case handling.

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      TUI Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Textual App   │  │  Command Input  │                  │
│  │   (Main App)    │  │   (Optional)    │                  │
│  └────────┬────────┘  └─────────────────┘                  │
│           │                                                    │
│  ┌────────┴────────┐  ┌─────────────────┐                  │
│  │   Widget Tree   │  │  Event Handler  │                  │
│  │  (Reactive)    │  │   (Bindings)    │                  │
│  └────────┬────────┘  └─────────────────┘                  │
└───────────┼────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Interface Bridge                          │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   State Sync    │  │   Action Queue  │                  │
│  │   (Observable)  │  │   (Async)       │                  │
│  └─────────────────┘  └─────────────────┘                  │
└───────────┬────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Game Engine                            │
│                  (Game Loop, Events)                        │
└────────┬─────────────────┬───────────────────┬────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   World     │  │   Character     │  │   Combat        │
│  Manager    │  │   Manager       │  │   Engine        │
└─────────────┘  └─────────────────┘  └─────────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Dungeon    │  │   Inventory     │  │   AI/Enemy      │
│  Generator  │  │   System        │  │   Manager       │
└─────────────┘  └─────────────────┘  └─────────────────┘
         │                 │                   │
         └─────────────────┼───────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Persistence Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   SQLite        │  │   Save Manager  │                  │
│  │   Storage       │  │   (Compression) │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Module Structure

```
src/
├── cli/
│   ├── __init__.py
│   ├── command_parser.py      # Input parsing and validation
│   ├── display.py             # ASCII rendering, colors
│   └── input_handler.py       # User input processing
├── tui/
│   ├── __init__.py
│   ├── app.py                 # Textual App main class
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── game_screen.py     # Main game view
│   │   ├── character_screen.py # Character sheet
│   │   ├── inventory_screen.py # Inventory management
│   │   ├── log_screen.py      # Combat/message log
│   │   └── menu_screen.py     # Main menu, save/load
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── map_widget.py       # ASCII map renderer
│   │   ├── status_widget.py   # HP, stats panel
│   │   ├── log_widget.py      # Scrollable message log
│   │   ├── inventory_widget.py # Item list with actions
│   │   ├── combat_log_widget.py # Combat feed
│   │   └── char_info_widget.py # Character attributes
│   ├── bindings/
│   │   ├── __init__.py
│   │   ├── navigation.py       # Vim-style movement
│   │   ├── game_actions.py     # Game command bindings
│   │   └── modal_bindings.py   # Modal dialog bindings
│   ├── styles/
│   │   ├── __init__.py
│   │   ├── theme.py            # Color themes
│   │   ├── tiles.py            # ASCII tile styling
│   │   └── widgets.py          # Widget-specific styles
│   ├── layout/
│   │   ├── __init__.py
│   │   ├── layout_manager.py   # Responsive layout logic
│   │   └── panels.py           # Panel configurations
│   └── reactivity/
│       ├── __init__.py
│       ├── state_store.py      # Observable game state
│       ├── action_dispatcher.py # Async action handling
│       └── subscriptions.py   # Widget state subscriptions
├── core/
│   ├── __init__.py
│   ├── game_engine.py         # Main game loop, tick system
│   ├── event_bus.py           # Event-driven communication
│   └── config.py              # Game configuration
├── entities/
│   ├── __init__.py
│   ├── character.py           # Character class, attributes
│   ├── enemy.py               # Enemy AI, behaviors
│   ├── item.py                # Items, equipment, loot
│   └── entity.py              # Base entity class
├── world/
│   ├── __init__.py
│   ├── dungeon_generator.py   # Procedural generation
│   ├── map.py                 # Map representation, tiles
│   ├── fov.py                 # Field of view calculations
│   └── tile_types.py          # Tile definitions
├── combat/
│   ├── __init__.py
│   ├── combat_engine.py       # Combat resolution
│   ├── dice.py                # D&D dice mechanics
│   ├── initiative.py          # Turn order management
│   └── status_effects.py      # Buffs, debuffs, conditions
├── character/
│   ├── __init__.py
│   ├── attributes.py          # 6 attributes, calculations
│   ├── inventory.py           # Inventory management
│   ├── equipment.py           # Equipment slots, bonuses
│   └── leveling.py            # XP, levels, class features
├── persistence/
│   ├── __init__.py
│   ├── database.py            # SQLite wrapper
│   ├── save_manager.py        # Save/load with compression
│   └── migrations.py          # Schema migrations
├── concurrency/
│   ├── __init__.py
│   ├── tick_system.py         # Game tick processing
│   ├── spawner.py             # Async enemy spawning
│   └── worker_pool.py         # Background task execution
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging utilities
│   ├── exceptions.py          # Custom exceptions
│   └── validators.py          # Input validation
└── main.py                    # Entry point
```

## 4. Data Models

### 4.1 Character

```python
@dataclass
class Character:
    id: str
    name: str
    level: int
    experience: int
    character_class: str
    background: str
    race: str

    # Attributes (6-20 range)
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    # Derived stats (calculated from attributes)
    @property
    def armor_class(self) -> int: ...
    @property
    def max_hp(self) -> int: ...
    @property
    def current_hp(self) -> int: ...
    @property
    def proficiency_bonus(self) -> int: ...

    # Resources
    hit_points: int
    temporary_hp: int
    exhaustion_level: int
    class_resources: Dict[str, int]  # e.g., {"spell_slots": {...}}

    # State
    alive: bool
    conditions: List[StatusEffect]
    death_saves: Tuple[int, int]  # successes, failures

    # Inventory
    inventory: Inventory
    equipment: Equipment

    # Position
    current_floor: int
    position: Tuple[int, int]

    # History
    kills: Dict[str, int]
    damage_dealt: int
    damage_taken: int
    turns_survived: int
```

### 4.2 Dungeon/Map

```python
@dataclass
class Tile:
    char: str                    # ASCII character
    color: str                   # ANSI color
    blocking: bool               # Movement blocking
    transparent: bool            # FOV transparency
    walkable: bool               # Can walk on it
    opaque: bool                 # Blocks FOV
    tile_type: TileType          # Floor, Wall, Door, etc.
    contents: List[Item]         # Items on tile
    entity: Optional[Entity]     # Entity on tile

@dataclass
class Map:
    width: int
    height: int
    tiles: List[List[Tile]]
    rooms: List[Room]
    connections: List[Connection]

    def get_tile(self, x: int, y: int) -> Tile: ...
    def is_walkable(self, x: int, y: int) -> bool: ...
    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]: ...

@dataclass
class Room:
    id: str
    x: int
    y: int
    width: int
    height: int
    room_type: RoomType          # Corridor, Chamber, Shrines
    special_features: List[str]  # Fountain, Statue, etc.
    spawns: List[EnemySpawn]     # Enemy spawn data
```

### 4.3 Enemy

```python
@dataclass
class Enemy:
    id: str
    name: str
    enemy_type: str              # Undead, Beast, Aberration, etc.
    cr: float                    # Challenge rating

    # Stats (calculated)
    armor_class: int
    max_hp: int
    attack_bonus: int
    damage_per_round: int

    # Attributes
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    # Behavior
    ai_type: AIType              # Passive, Aggressive, Defensive
    aggro_range: int
    patrol_route: Optional[List[Tuple[int, int]]]
    abilities: List[EnemyAbility]
    resistances: List[str]
    immunities: List[str]

    # State
    current_hp: int
    status_effects: List[StatusEffect]
    alive: bool

    # Position
    map_id: str
    position: Tuple[int, int]
```

### 4.4 Item

```python
@dataclass
class Item:
    id: str
    name: str
    item_type: ItemType           # Weapon, Armor, Potion, Scroll, etc.
    rarity: Rarity

    # Physical properties
    weight: float
    quantity: int
    stackable: bool
    max_stack: int

    # Magical properties
    attunement_required: bool
    attunement_slots: int
    magical_bonus: int
    modifiers: List[StatModifier]
    charges: int
    max_charges: int

    # Description
    description: str
    lore_text: Optional[str]

    # For weapons
    weapon_type: Optional[WeaponType]
    damage_die: str               # "1d8"
    damage_type: Optional[str]
    properties: List[str]        # Finesse, Heavy, Reach, etc.

    # For armor
    armor_type: Optional[ArmorType]
    base_ac: int
    stealth_disadvantage: bool

    # For potions/scrolls
    spell: Optional[Spell]
    uses_remaining: int
```

## 5. Core Algorithms

### 5.1 Dungeon Generation (BSP + Cellular Automata)

```python
class DungeonGenerator:
    def __init__(self, config: DungeonConfig):
        self.config = config
        self.map = Map(...)
        self.rooms = []

    def generate(self) -> Map:
        # Phase 1: BSP partition for room placement
        bsp_tree = self._build_bsp(depth=6)

        # Phase 2: Generate rooms from leaf nodes
        rooms = self._generate_rooms(bsp_tree)

        # Phase 3: Cellular automata for cave sections
        caves = self._generate_caves()

        # Phase 4: Connect rooms with corridors
        self._connect_rooms(rooms, caves)

        # Phase 5: Place enemies and loot
        self._populate(rooms, caves)

        # Phase 6: Add special features
        self._add_features(rooms)

        return self.map

    def _build_bsp(self, depth: int) -> BSPNode:
        """Binary Space Partitioning for room placement."""
        ...

    def _generate_rooms(self, bsp_tree: BSPNode) -> List[Room]:
        """Generate rooms in BSP leaf nodes."""
        ...

    def _generate_caves(self) -> List[List[Tile]]:
        """Cellular automata for natural cave systems."""
        ...

    def _connect_rooms(self, rooms: List[Room], caves: List[List[Tile]]):
        """Connect rooms using corridor algorithms."""
        ...
```

### 5.2 A* Pathfinding

```python
class Pathfinder:
    def __init__(self, map: Map):
        self.map = map
        self.heuristic = self._manhattan_distance

    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A* pathfinding implementation."""
        open_set: PriorityQueue[Node] = PriorityQueue()
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = defaultdict(lambda: inf)
        f_score: Dict[Tuple[int, int], float] = defaultdict(lambda: inf)

        g_score[start] = 0
        f_score[start] = self.heuristic(start, end)
        open_set.push(Node(start, f_score[start]))

        while not open_set.empty():
            current = open_set.pop()

            if current.position == end:
                return self._reconstruct_path(came_from, current.position)

            for neighbor in self._get_neighbors(current.position):
                tentative_g = g_score[current.position] + self._movement_cost(current.position, neighbor)

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current.position
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, end)
                    open_set.push(Node(neighbor, f_score[neighbor]))

        return []  # No path found
```

### 5.3 Shadow Casting FOV

```python
class FieldOfView:
    def __init__(self, map: Map):
        self.map = map

    def compute(self, x: int, y: int, radius: int) -> Set[Tuple[int, int]]:
        """Shadow casting algorithm for FOV calculation."""
        visible_tiles = {(x, y)}

        for octant in range(8):
            visible_tiles |= self._cast_light(x, y, radius, 1, 1.0, 0.0, [], octant)

        return visible_tiles

    def _cast_light(self, cx, cy, row, start, end, radius, cells, octant):
        """Recursive shadow casting."""
        ...
```

### 5.4 Combat Resolution

```python
class CombatEngine:
    def __init__(self, dice: DiceRoller):
        self.dice = dice

    def resolve_attack(self, attacker: Entity, defender: Entity, attack_type: str = "melee") -> AttackResult:
        # Roll attack
        d20 = self.dice.roll("1d20")[0]
        bonus = self._calculate_attack_bonus(attacker, attack_type)
        total = d20 + bonus

        # Check for natural 20 (crit)
        if d20 == 20:
            damage = self._calculate_crit_damage(attacker, defender)
            return AttackResult(critical=True, hit=True, damage=damage)

        # Check for natural 1 (miss)
        if d20 == 1:
            return AttackResult(critical=False, hit=False, damage=0)

        # Compare to AC
        ac = defender.armor_class
        if total >= ac:
            damage = self._calculate_damage(attacker, defender)
            return AttackResult(critical=False, hit=True, damage=damage)

        return AttackResult(critical=False, hit=False, damage=0)

    def roll_damage(self, attacker: Entity, weapon: Optional[Item], damage_type: str) -> int:
        """Roll weapon damage with modifiers."""
        ...
```

## 6. Concurrency Model

### 6.1 Tick System

```python
class TickSystem:
    def __init__(self, tick_rate: float = 0.1):
        self.tick_rate = tick_rate
        self.running = False
        self.current_tick = 0
        self.subscribers: List[TickSubscriber] = []

    def start(self):
        """Start the game tick loop."""
        self.running = True
        while self.running:
            start_time = time.monotonic()
            self._tick()
            elapsed = time.monotonic() - start_time
            sleep_time = max(0, self.tick_rate - elapsed)

            if sleep_time > 0:
                time.sleep(sleep_time)

    def _tick(self):
        """Execute one game tick."""
        self.current_tick += 1
        for subscriber in self.subscribers:
            subscriber.on_tick(self.current_tick)

    def subscribe(self, subscriber: TickSubscriber):
        """Subscribe to tick events."""
        self.subscribers.append(subscriber)
```

### 6.2 Async Spawner

```python
class EnemySpawner:
    def __init__(self, game_state: GameState, spawner_config: SpawnerConfig):
        self.game_state = game_state
        self.config = spawner_config
        self.spawn_queue: asyncio.Queue[EnemySpawnTask] = asyncio.Queue()
        self.spawning = False
        self._spawn_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the async spawner."""
        self.spawning = True
        self._spawn_task = asyncio.create_task(self._spawn_loop())

    async def stop(self):
        """Stop the async spawner."""
        self.spawning = False
        if self._spawn_task:
            await self._spawn_task

    async def _spawn_loop(self):
        """Background loop for spawning enemies."""
        while self.spawning:
            try:
                # Wait for spawn signal with timeout
                task = await asyncio.wait_for(
                    self.spawn_queue.get(),
                    timeout=self.config.spawn_interval
                )
                await self._execute_spawn(task)
            except asyncio.TimeoutError:
                # Periodic spawn check
                if self._should_periodic_spawn():
                    await self._periodic_spawn()
            except Exception as e:
                logger.error(f"Spawner error: {e}")

    async def queue_spawn(self, spawn: EnemySpawnTask):
        """Queue a spawn task."""
        await self.spawn_queue.put(spawn)

    async def _execute_spawn(self, task: EnemySpawnTask):
        """Execute a single spawn."""
        enemy = await self._create_enemy(task.enemy_type, task.location)
        self.game_state.add_enemy(enemy)
```

### 6.3 Event Bus

```python
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable):
        self._subscribers[event_type].append(callback)

    def subscribe_async(self, event_type: str, callback: Callable):
        self._async_subscribers[event_type].append(callback)

    def publish(self, event: Event):
        for callback in self._subscribers.get(event.type, []):
            callback(event)

        for callback in self._async_subscribers.get(event.type, []):
            asyncio.create_task(callback(event))
```

## 7. Persistence Layer

### 7.1 Database Schema

```sql
-- Characters table
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    character_class TEXT NOT NULL,
    race TEXT NOT NULL,
    background TEXT,

    -- Attributes (6-20)
    strength INTEGER NOT NULL,
    dexterity INTEGER NOT NULL,
    constitution INTEGER NOT NULL,
    intelligence INTEGER NOT NULL,
    wisdom INTEGER NOT NULL,
    charisma INTEGER NOT NULL,

    -- Resources
    hit_points INTEGER NOT NULL,
    temporary_hp INTEGER DEFAULT 0,
    exhaustion_level INTEGER DEFAULT 0,

    -- State
    alive INTEGER DEFAULT 1,
    death_save_successes INTEGER DEFAULT 0,
    death_save_failures INTEGER DEFAULT 0,

    -- Position
    current_floor INTEGER DEFAULT 1,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,

    -- History
    damage_dealt INTEGER DEFAULT 0,
    damage_taken INTEGER DEFAULT 0,
    turns_survived INTEGER DEFAULT 0,

    -- Metadata
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    playtime_seconds INTEGER DEFAULT 0
);

-- Character class resources (spell slots, etc.)
CREATE TABLE class_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_level INTEGER,
    current_value INTEGER,
    max_value INTEGER,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Inventory items
CREATE TABLE inventory_items (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    is_equipped INTEGER DEFAULT 0,
    slot TEXT,
    identified INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- World state (dungeons, explored areas)
CREATE TABLE world_states (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    floor_number INTEGER NOT NULL,
    dungeon_seed INTEGER NOT NULL,
    explored_tiles BLOB NOT NULL,
    placed_items BLOB NOT NULL,
    placed_enemies BLOB NOT NULL,
    room_data BLOB NOT NULL,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Kill tracking
CREATE TABLE kills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    enemy_type TEXT NOT NULL,
    kill_count INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Indexes
CREATE INDEX idx_inventory_character ON inventory_items(character_id);
CREATE INDEX idx_world_state_character ON world_states(character_id, floor_number);
CREATE INDEX idx_kills_character ON kills(character_id, enemy_type);
```

### 7.2 Save Manager with Compression

```python
class SaveManager:
    def __init__(self, save_dir: Path, compression: str = "lz4"):
        self.save_dir = save_dir
        self.compression = compression
        self.compressor = self._get_compressor(compression)

    def save_game(self, character: Character, world_state: WorldState, filename: Optional[str] = None) -> Path:
        """Save game with compression."""
        if filename is None:
            filename = f"{character.id}.sav"

        # Serialize game state
        save_data = {
            "version": SAVE_FORMAT_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "character": self._serialize_character(character),
            "world": self._serialize_world(world_state),
            "checksum": None  # Calculated after serialization
        }

        # Calculate checksum
        json_bytes = json.dumps(save_data, indent=2).encode("utf-8")
        save_data["checksum"] = self._calculate_checksum(json_bytes)

        # Compress
        compressed = self.compressor.compress(json.dumps(save_data).encode("utf-8"))

        # Write to file
        save_path = self.save_dir / filename
        with open(save_path, "wb") as f:
            f.write(compressed)

        return save_path

    def load_game(self, save_path: Path) -> Tuple[Character, WorldState]:
        """Load and decompress game."""
        with open(save_path, "rb") as f:
            compressed = f.read()

        # Decompress
        decompressed = self.compressor.decompress(compressed)

        # Parse JSON
        save_data = json.loads(decompressed)

        # Verify checksum
        json_bytes = json.dumps(save_data, indent=2).encode("utf-8")
        calculated_checksum = self._calculate_checksum(json_bytes)

        if calculated_checksum != save_data["checksum"]:
            raise SaveCorruptionError("Save file checksum mismatch - file may be corrupted")

        # Handle version migration
        if save_data["version"] < SAVE_FORMAT_VERSION:
            save_data = self._migrate_save(save_data)

        # Deserialize
        character = self._deserialize_character(save_data["character"])
        world = self._deserialize_world(save_data["world"])

        return character, world

    def _get_compressor(self, compression: str) -> Compressor:
        if compression == "lz4":
            return LZ4Compressor()
        elif compression == "zlib":
            return ZlibCompressor()
        elif compression == "gzip":
            return GzipCompressor()
        else:
            raise ValueError(f"Unknown compression: {compression}")
```

### 7.3 Compression Strategies

```python
class LZ4Compressor:
    """High-speed compression for quick saves."""
    BLOCK_SIZE = 64 * 1024  # 64KB blocks

    def compress(self, data: bytes) -> bytes:
        import lz4.frame
        return lz4.frame.compress(
            data,
            compression_level=1,  # Fastest
            block_size=self.BLOCK_SIZE,
            checksum=True
        )

    def decompress(self, data: bytes) -> bytes:
        import lz4.frame
        return lz4.frame.decompress(data)

class ZlibCompressor:
    """Better compression for storage efficiency."""
    LEVEL = 6  # Balanced speed/size

    def compress(self, data: bytes) -> bytes:
        import zlib
        return zlib.compress(data, level=self.LEVEL)

    def decompress(self, data: bytes) -> bytes:
        import zzlib
        return zlib.decompress(data)
```

## 8. CLI Interface

### 8.1 Command Parser

```python
class CommandParser:
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine
        self.commands = {
            "move": self.cmd_move,
            "attack": self.cmd_attack,
            "look": self.cmd_look,
            "inventory": self.cmd_inventory,
            "equip": self. cmd_equip,
            "use": self.cmd_use,
            "rest": self.cmd_rest,
            "character": self.cmd_character,
            "map": self.cmd_map,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "help": self.cmd_help,
            "quit": self.cmd_quit,
        }

    def parse(self, input_str: str) -> Command:
        """Parse user input into a command."""
        tokens = input_str.strip().lower().split()

        if not tokens:
            raise EmptyCommandError()

        command = tokens[0]
        args = tokens[1:]

        if command not in self.commands:
            raise UnknownCommandError(f"Unknown command: {command}")

        # Validate arguments
        self._validate_args(command, args)

        return Command(name=command, args=args)

    def _validate_args(self, command: str, args: List[str]):
        """Validate command arguments."""
        validation = {
            "move": {"min": 1, "max": 1, "valid": ["n", "s", "e", "w", "north", "south", "east", "west"]},
            "attack": {"min": 1, "max": 1},
            "inventory": {"min": 0, "max": 0},
            "equip": {"min": 1, "max": 1},
            "use": {"min": 1, "max": 1},
            "rest": {"min": 0, "max": 1},
            "character": {"min": 0, "max": 0},
            "map": {"min": 0, "max": 0},
            "save": {"min": 0, "max": 1},
            "load": {"min": 1, "max": 1},
            "help": {"min": 0, "max": 0},
            "quit": {"min": 0, "max": 0},
        }

        config = validation.get(command, {"min": 0, "max": 0})
        arg_count = len(args)

        if arg_count < config["min"]:
            raise MissingArgumentError(f"Command '{command}' requires at least {config['min']} arguments")

        if arg_count > config["max"]:
            raise TooManyArgumentsError(f"Command '{command}' accepts at most {config['max']} arguments")
```

### 8.2 Display/Renderer

```python
class Display:
    COLORS = {
        "wall": "\033[90m",          # Dark gray
        "floor": "\033[37m",         # White
        "player": "\033[94m",        # Blue
        "enemy": "\033[91m",         # Red
        "item": "\033[93m",          # Yellow
        "stairs": "\033[95m",         # Magenta
        "fog": "\033[30m",           # Black
        "explored": "\033[30;1m",    # Dark gray (dim)
        "reset": "\033[0m",
    }

    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.viewport = Viewport(width, height)

    def render(self, game_state: GameState):
        """Render the game state to the terminal."""
        self._clear_screen()
        self._render_map(game_state)
        self._render_status(game_state)
        self._render_messages(game_state)

    def _render_map(self, game_state: GameState):
        """Render the game map with FOV."""
        visible_tiles = game_state.fov.compute(
            game_state.player.position,
            game_state.player.fov_radius
        )

        for y in range(self.height):
            for x in range(self.width):
                world_pos = self.viewport.to_world(x, y)
                if world_pos in visible_tiles:
                    self._render_visible_tile(world_pos, game_state)
                elif game_state.map.is_explored(world_pos):
                    self._render_explored_tile(world_pos, game_state)
                else:
                    self._render_unexplored_tile()
```

## 8. TUI Interface (Textual)

### 8.1 Textual App Architecture

```python
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

class DndRoguelikeApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3;
        grid-rows: 1fr 4fr 1fr;
        grid-columns: 1fr 3fr 1fr;
    }
    #map-panel {
        column-span: 2;
        row-span: 2;
    }
    #status-panel {
        column-span: 1;
        row-span: 1;
    }
    #log-panel {
        column-span: 3;
        row-span: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        (":", "command_mode", "Command"),
        ("h", "move(left)", "Left"),
        ("j", "move(down)", "Down"),
        ("k", "move(up)", "Up"),
        ("l", "move(right)", "Right"),
        ("<tab>", "next_panel", "Next Panel"),
    ]

    def __init__(self, game_engine: GameEngine):
        super().__init__()
        self.game = game_engine
        self.state_store = StateStore(game_engine)
        self.command_mode = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield MapPanel(id="map-panel", state_store=self.state_store)
        yield StatusPanel(id="status-panel", state_store=self.state_store)
        yield LogPanel(id="log-panel", state_store=self.state_store)
        yield Footer()

    async def on_mount(self) -> None:
        await self.state_store.start()
        self.game.start()

    def action_quit(self) -> None:
        self.game.stop()
        self.exit()

    async def action_command_mode(self) -> None:
        self.command_mode = True
        command_input = self.query_one("#command-input", CommandInput)
        command_input.focus()

    def action_move(self, direction: str) -> None:
        if not self.command_mode:
            asyncio.create_task(self.game.execute_command(f"move {direction}"))
```

### 8.2 Map Panel Widget

```python
from textual.widgets import Static
from textual.color import Color

class MapPanel(Static):
    DEFAULT_CSS = """
    MapPanel {
        background: $surface;
        border: solid $primary;
        overflow: hidden;
    }
    """

    TILE_COLORS = {
        "@": Color(0, 100, 255),      # Player - Blue
        "#": Color(80, 80, 80),        # Wall - Gray
        ".": Color(200, 200, 200),     # Floor - Light Gray
        "+": Color(139, 69, 19),       # Door - Brown
        ">": Color(255, 215, 0),       # Stairs - Gold
        "$": Color(255, 215, 0),       # Gold - Gold
        "!": Color(255, 0, 255),      # Potion - Magenta
        "?": Color(255, 255, 255),     # Scroll - White
        "E": Color(255, 0, 0),         # Enemy - Red
    }

    def __init__(self, state_store: "StateStore", **kwargs):
        super().__init__(**kwargs)
        self.state_store = state_store
        self.viewport_width = 40
        self.viewport_height = 20

    def watch_state(self) -> None:
        state = self.state_store.get_state()
        if state and state.map:
            self.refresh_map(state)

    def render_map(self, game_state: "GameState") -> str:
        visible = game_state.fov.compute(
            game_state.player.position,
            game_state.player.fov_radius
        )
        explored = game_state.map.explored_tiles

        lines = []
        for y in range(self.viewport_height):
            line = []
            for x in range(self.viewport_width):
                world_x, world_y = self.viewport_to_world(x, y)
                tile_char, tile_color = self.get_tile_display(
                    world_x, world_y, visible, explored, game_state
                )
                line.append(self.format_char(tile_char, tile_color))
            lines.append("".join(line))
        return "\n".join(lines)

    def get_tile_display(self, x: int, y: int, visible: Set, explored: Set, state: "GameState") -> Tuple[str, Color]:
        if (x, y) == state.player.position:
            return ("@", self.TILE_COLORS["@"])

        if (x, y) in visible:
            tile = state.map.get_tile(x, y)
            if tile.entity and isinstance(tile.entity, Enemy):
                return ("E", self.TILE_COLORS["E"])
            if tile.contents:
                item = tile.contents[0]
                if isinstance(item, Gold):
                    return ("$", self.TILE_COLORS["$"])
                # ... other item types
            return (tile.char, self.TILE_COLORS.get(tile.char, Color(255, 255, 255)))

        if (x, y) in explored:
            return (".", Color(60, 60, 60))  # Dim floor

        return (" ", Color(0, 0, 0))  # Unexplored
```

### 8.3 Status Panel

```python
class StatusPanel(Static):
    def compose(self) -> ComposeResult:
        yield CharacterWidget(id="character-info")
        yield CombatStatsWidget(id="combat-stats")

    def watch_state(self) -> None:
        state = self.state_store.get_state()
        if state:
            self.query_one("#character-info", CharacterWidget).update(state.player)
            self.query_one("#combat-stats", CombatStatsWidget).update(state)


class CharacterWidget(Static):
    def update(self, character: Character) -> None:
        self.update(f"""\
[bold]Character[/bold]
Name: {character.name}
Class: {character.character_class}
Level: {character.level} ({character.xp} XP)

[bold]Attributes[/bold]
STR: {character.strength:2d} ({character.strength_mod:+d})
DEX: {character.dexterity:2d} ({character.dexterity_mod:+d})
CON: {character.constitution:2d} ({character.constitution_mod:+d}
INT: {character.intelligence:2d} ({character.intelligence_mod:+d}
WIS: {character.wisdom:2d} ({character.wisdom_mod:+d})
CHA: {character.charisma:2d} ({character.charisma_mod:+d})

[bold]Resources[/bold]
HP: {character.current_hp}/{character.max_hp}
AC: {character.armor_class}
Prof: +{character.proficiency_bonus}
""")


class CombatStatsWidget(Static):
    def update(self, state: "GameState") -> None:
        enemies_nearby = len([
            e for e in state.enemies
            if e.position in state.fov.visible_tiles
        ])
        self.update(f"""\
[bold]Combat[/bold]
Enemies Visible: {enemies_nearby}
Turn: {state.turn_count}
Floor: {state.current_floor}
""")
```

### 8.4 Log Panel with Scrolling

```python
from textual.widgets._log import Log

class LogPanel(Log):
    def __init__(self, state_store: "StateStore", **kwargs):
        super().__init__(**kwargs)
        self.state_store = state_store
        self.max_lines = 100
        self.highlight_patterns = [
            (r"hit", "green"),
            (r"miss", "red"),
            (r"critical", "bold yellow"),
            (r"damage", "red"),
            (r"heal", "green"),
            (r"die", "strike"),
        ]

    def watch_messages(self, messages: List["GameMessage"]) -> None:
        for msg in messages[-10:]:  # Last 10 messages
            self.write_line(self.format_message(msg))

    def format_message(self, message: "GameMessage") -> str:
        text = message.text
        for pattern, style in self.highlight_patterns:
            text = text.replace(pattern, f"[{style}]{pattern}[/]")
        return text


class CombatLogWidget(Log):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles = {
            "player_attack": "green",
            "player_damage": "bold green",
            "enemy_attack": "red",
            "enemy_damage": "bold red",
            "crit": "yellow",
            "miss": "dim",
        }

    def add_combat_event(self, event: "CombatEvent") -> None:
        style = self.styles.get(event.event_type, "")
        timestamp = event.timestamp.strftime("%H:%M:%S")
        self.write_line(f"[{timestamp}] [{style}]{event.description}[/]")
```

### 8.5 Command Input Modal

```python
from textual.widgets import Input

class CommandInput(Input):
    def __init__(self, **kwargs):
        super().__init__(placeholder="Enter command...", **kwargs)
        self.command_parser = None

    def on_submit(self, event: Input.Submit) -> None:
        command_str = self.value.strip()
        if command_str:
            self.app.game.execute_command(command_str)
        self.value = ""
        self.remove_class("--focus")
        self.app.pop_screen()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.value = ""
            self.remove_class("--focus")
            self.app.pop_screen()


class CommandModal(Modal):
    def __init__(self):
        super().__init__()
        self.css = """
        CommandModal {
            align: center top;
            width: 60;
            height: 3;
        }
        #command-input {
            border: solid $primary;
        }
        """

    def compose(self) -> ComposeResult:
        yield CommandInput(id="command-input")

    def on_mount(self) -> None:
        self.query_one("#command-input").focus()
```

### 8.6 State Store (Observable Pattern)

```python
from typing import Dict, Callable, Set
import asyncio

class StateStore:
    def __init__(self, game_engine: GameEngine):
        self.game = game_engine
        self._state: Optional["GameState"] = None
        self._subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self._running = False
        self._update_task: Optional[asyncio.Task] = None

    async def start(self):
        self._running = True
        self._update_task = asyncio.create_task(self._poll_state())

    async def stop(self):
        self._running = False
        if self._update_task:
            self._update_task.cancel()

    async def _poll_state(self):
        while self._running:
            new_state = self.game.get_state()
            if new_state != self._state:
                old_state = self._state
                self._state = new_state
                self._notify_subscribers(old_state, new_state)
            await asyncio.sleep(1/30)  # 30fps update rate

    def subscribe(self, component: str, callback: Callable):
        self._subscribers[component].add(callback)

    def unsubscribe(self, component: str, callback: Callable):
        self._subscribers[component].discard(callback)

    def _notify_subscribers(self, old_state: Optional["GameState"], new_state: "GameState"):
        changes = self._compute_changes(old_state, new_state)
        for component, callbacks in self._subscribers.items():
            for callback in callbacks:
                callback(changes.get(component, new_state))

    def get_state(self) -> Optional["GameState"]:
        return self._state

    def _compute_changes(self, old: Optional["GameState"], new: "GameState") -> Dict[str, Any]:
        if old is None:
            return {"*": new}

        changes = {}
        if old.player != new.player:
            changes["player"] = new.player
        if old.map != new.map:
            changes["map"] = new.map
        if old.enemies != new.enemies:
            changes["enemies"] = new.enemies
        return changes
```

### 8.7 Action Dispatcher (Async Actions)

```python
class ActionDispatcher:
    def __init__(self, game_engine: GameEngine):
        self.game = game_engine
        self._action_queue: asyncio.Queue = asyncio.Queue()
        self._response_futures: Dict[str, asyncio.Future] = {}
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._process_actions())

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def execute(self, action: "GameAction", timeout: float = 5.0) -> "ActionResult":
        action_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._response_futures[action_id] = future

        await self._action_queue.put((action_id, action))
        self.game.events.publish(GameEvent("action_queued", action))

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            del self._response_futures[action_id]
            raise ActionTimeoutError(f"Action {action} timed out")

    async def _process_actions(self):
        while self._running:
            try:
                action_id, action = await self._action_queue.get()
                result = await self.game.execute_action(action)
                if action_id in self._response_futures:
                    self._response_futures[action_id].set_result(result)
                    del self._response_futures[action_id]
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Action processing error: {e}")
                if action_id in self._response_futures:
                    self._response_futures[action_id].set_exception(e)
```

### 8.8 Layout Management

```python
class LayoutManager:
    LAYOUTS = {
        "small": LayoutConfig(
            map_width=40, map_height=20,
            status_width=20, log_height=4
        ),
        "medium": LayoutConfig(
            map_width=60, map_height=30,
            status_width=30, log_height=6
        ),
        "large": LayoutConfig(
            map_width=80, map_height=40,
            status_width=40, log_height=8
        ),
    }

    def __init__(self, terminal_size: Tuple[int, int]):
        self.terminal_width, self.terminal_height = terminal_size
        self.current_layout = self._detect_layout()
        self._register_resize_handler()

    def _detect_layout(self) -> str:
        if self.terminal_width < 80 or self.terminal_height < 30:
            return "small"
        elif self.terminal_width < 120 or self.terminal_height < 50:
            return "medium"
        return "large"

    def _register_resize_handler(self):
        signal.signal(signal.SIGWINCH, self._handle_resize)

    def _handle_resize(self, signum, frame):
        self.terminal_width, self.terminal_height = os.get_terminal_size()
        new_layout = self._detect_layout()
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self.app.notify_layout_change(new_layout)

    def get_layout_config(self) -> "LayoutConfig":
        return self.LAYOUTS[self.current_layout]
```

### 8.9 Theming System

```python
from dataclasses import dataclass
from textual.color import Color

@dataclass
class Theme:
    name: str
    colors: Dict[str, Color]
    styles: Dict[str, str]

    @classmethod
    def dark(cls) -> "Theme":
        return cls(
            name="dark",
            colors={
                "background": Color(0, 0, 0),
                "surface": Color(30, 30, 30),
                "primary": Color(0, 150, 255),
                "secondary": Color(100, 100, 100),
                "success": Color(0, 200, 0),
                "warning": Color(255, 200, 0),
                "error": Color(255, 50, 50),
                "player": Color(0, 100, 255),
                "enemy": Color(255, 0, 0),
                "item": Color(255, 215, 0),
                "wall": Color(80, 80, 80),
                "floor": Color(150, 150, 150),
            },
            styles={
                "header": "bold reverse",
                "footer": "dim",
                "map": "font: monospace",
                "status": "bold",
                "log": "font: monospace",
            }
        )

    @classmethod
    def retro(cls) -> "Theme":
        return cls(
            name="retro",
            colors={
                "background": Color(0, 0, 0),
                "surface": Color(0, 0, 0),
                "primary": Color(0, 255, 0),  # Classic terminal green
                "secondary": Color(0, 128, 0),
                "success": Color(0, 255, 0),
                "warning": Color(255, 255, 0),
                "error": Color(255, 0, 0),
                "player": Color(0, 255, 0),
                "enemy": Color(255, 0, 0),
                "item": Color(255, 255, 0),
                "wall": Color(0, 128, 0),
                "floor": Color(0, 64, 0),
            },
            styles={}
        )

    @classmethod
    def high_contrast(cls) -> "Theme":
        return cls(
            name="high_contrast",
            colors={
                "background": Color(0, 0, 0),
                "surface": Color(0, 0, 0),
                "primary": Color(255, 255, 255),
                "secondary": Color(255, 255, 255),
                "success": Color(0, 255, 0),
                "warning": Color(255, 255, 0),
                "error": Color(255, 0, 0),
                "player": Color(255, 255, 255),
                "enemy": Color(255, 0, 0),
                "item": Color(255, 255, 0),
                "wall": Color(255, 255, 255),
                "floor": Color(128, 128, 128),
            },
            styles={}
        )


class ThemeManager:
    THEMES = {
        "dark": Theme.dark(),
        "retro": Theme.retro(),
        "high_contrast": Theme.high_contrast(),
    }

    def __init__(self, default_theme: str = "dark"):
        self.current_theme = self.THEMES[default_theme]

    def set_theme(self, theme_name: str) -> None:
        if theme_name in self.THEMES:
            self.current_theme = self.THEMES[theme_name]
            self.app.refresh_theme()

    def apply_to_widget(self, widget: "Widget") -> None:
        for prop, color in self.current_theme.colors.items():
            setattr(widget, prop, color)
```

### 8.10 TUI-specific Error Handling

```python
class TUIError(GameError):
    """Base TUI-related error."""
    pass

class TerminalResizeError(TUIError):
    """Terminal resize beyond minimum dimensions."""
    pass

class RenderError(TUIError):
    """Rendering failed."""
    pass

class WidgetUpdateError(TUIError):
    """Widget state update failed."""
    pass

class FocusError(TUIError):
    """Focus management error."""
    pass


class TUIErrorHandler:
    def __init__(self, app: DndRoguelikeApp):
        self.app = app

    def handle_resize_error(self, error: TerminalResizeError) -> None:
        self.app.push_screen(
            AlertScreen(
                title="Terminal Too Small",
                message="Please resize terminal to at least 80x24",
                severity="warning"
            )
        )

    def handle_render_error(self, error: RenderError) -> None:
        logger.error(f"Render error: {error}", exc_info=True)
        self.app.notify(
            "Display error - some elements may not render correctly",
            severity="error"
        )
```

### 8.11 TUI Performance Targets

| Metric | Target |
|--------|--------|
| Initial render | < 100ms |
| State update latency | < 33ms (30fps) |
| Map redraw | < 5ms |
| Panel refresh | < 2ms |
| Key response time | < 16ms |
| Memory overhead | < 50MB |

### 8.12 LLM Stress Test Scenarios for TUI

| Scenario | Complexity | Tests |
|----------|------------|-------|
| Implement Textual app with reactive state | High | State management, async patterns |
| Custom widget with animated tiles | Medium | Widget lifecycle, animation |
| Modal dialog with form validation | Medium | Input handling, validation |
| Scrollable log with auto-scroll | Medium | Widget internals, scroll sync |
| Theme switching at runtime | Low | Dynamic styling |
| Responsive layout on resize | Medium | Signal handling, layout math |
| Complex binding conflicts | Low | Key binding resolution |
| Action queue with timeout | High | Async patterns, error handling |

## 9. Error Handling & Edge Cases

### 9.1 Custom Exceptions

```python
class GameError(Exception):
    """Base exception for game errors."""

class SaveError(GameError):
    """Save/load related errors."""
    pass

class SaveCorruptionError(SaveError):
    """Save file is corrupted."""
    pass

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
    pass
```

### 9.2 Edge Case Handling Strategy

| Edge Case | Handling Strategy |
|-----------|-------------------|
| Save corruption | Checksum validation, automatic backup recovery |
| Invalid inputs | Input validation, helpful error messages |
| Out of bounds | Coordinate validation, clamp to map edges |
| Inventory overflow | Weight checks, stack merging, selective drop |
| Character death | Death saves, stable/unstable state, resurrection options |
| Enemy spawn fail | Retry with fallback, log warning, continue |
| Database lock | Retry with exponential backoff |
| Memory pressure | Chunked loading, resource cleanup |
| Quicksave during combat | Allow with warning, combat state preserved |
| Load incompatible save | Version migration, graceful degradation |

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/test_combat.py
class TestCombatEngine:
    def test_attack_roll_with_bonus(self):
        engine = CombatEngine(DiceRoller())
        attacker = MockCharacter(strength=16)
        defender = MockCharacter(armor_class=14)

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is True
        assert result.damage >= 1

    def test_critical_hit_on_natural_20(self):
        engine = CombatEngine(FixedDiceRoller([20]))
        attacker = MockCharacter(strength=16)
        defender = MockCharacter(armor_class=14)

        result = engine.resolve_attack(attacker, defender)

        assert result.critical is True
        assert result.hit is True

    def test_automatic_miss_on_natural_1(self):
        engine = CombatEngine(FixedDiceRoller([1]))
        attacker = MockCharacter(strength=16)
        defender = MockCharacter(armor_class=14)

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is False
        assert result.critical is False
```

### 10.2 Integration Tests

- Complete game flow: new game → explore → combat → level up → save → load
- Combat sequences: multiple enemies, status effects, death saves
- Dungeon generation: valid layouts, connectivity, enemy placement
- Persistence: save/load at various game states, corruption handling

### 10.3 LLM Stress Test Scenarios

| Scenario | Tests | Complexity |
|----------|-------|------------|
| Implement full A* algorithm | Pathfinding edge cases | High |
| Handle save handling, recovery | Medium |
| Complex corruption | Error combat with conditions | State management | Medium |
| Procedural dungeon gen | Algorithms, code organization | High |
| Async spawner with events | Concurrency patterns | High |
| Character creation with validation | Input handling, edge cases | Low |
| Complete save/load cycle | Persistence, compression | Medium |

## 11. Dependencies

### 11.1 Python (Recommended Stack with TUI)

```txt
# requirements.txt
# Core game (stdlib only for LLM purity)
# (none required)

# TUI Framework
textual>=0.50.0

# Optional - for compression testing
lz4>=4.0.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
hypothesis>=6.0.0
pytest-textual>=0.1.0

# Type checking
mypy>=1.0.0
types-lz4>=0.1.0

# Linting
ruff>=0.1.0
```

## 12. Implementation Phases

### Phase 1: Core Foundation
- Basic character system
- Simple map generation
- Basic movement
- Save/load without compression

### Phase 2: Combat & Enemies
- Combat engine
- Enemy AI with A* pathfinding
- FOV system
- Status effects

### Phase 3: Content
- Full class system
- Equipment and inventory
- Loot generation
- Dungeon features

### Phase 4: TUI Integration
- Textual app shell
- Map panel with rendering
- Status and log panels
- Command input system

### Phase 5: Polish
- Save compression
- Async spawner
- Error handling
- Theme system

## 13. Open Questions

1. **Auto-save strategy**: Should we auto-save on every floor change, or use a timer-based approach?
2. **Difficulty scaling**: Should difficulty scale with character level, or floor depth?
3. **Permadeath**: Hardcore only, or offer optional checkpoints?
4. **TUI vs CLI**: Support both interfaces (Textual TUI + traditional CLI), or TUI-only?
5. **Multi-backend TUI**: Should we support multiple TUI backends (Textual, curses, blessed)?
6. **Game loop sync**: Should TUI drive the game loop, or run parallel to it?

---

## 14. Appendix A: D&D 5e Mechanics Reference

### Attack Roll
```
d20 roll + ability modifier + proficiency bonus (if proficient)
vs
Target's Armor Class
```

### Critical Hit
- Natural 20 on attack roll
- Roll damage dice twice
- No ability modifier on extra damage

### Ability Modifiers
```
Score | Modifier
------|---------
1     | -5
2-3   | -4
4-5   | -3
6-7   | -2
8-9   | -1
10-11 | +0
12-13 | +1
14-15 | +2
16-17 | +3
18-19 | +4
20    | +5
```

### Proficiency Bonus by Level
```
Level | Bonus
------|------
1-4   | +2
5-8   | +3
9-12  | +4
13-16 | +5
17-20 | +6
```

## 15. Appendix B: ASCII Tile Reference

```
@ - Player
# - Wall
. - Floor
+ - Door (closed)
/ - Door (open)
< - Stairs up
> - Stairs down
$ - Item on ground
! - Potion
? - Scroll
/ - Weapon
[ - Armor
= - Ring
) - Ammunition
```

## 16. Appendix C: Compression Benchmark Targets

| Metric | Target |
|--------|--------|
| Save time (100hr game) | < 500ms |
| Load time (100hr game) | < 500ms |
| Save size (100hr game) | < 10MB |
| Compression ratio | > 5:1 |

## 17. Appendix D: TUI Performance Benchmarks

| Metric | Target |
|--------|--------|
| Initial render | < 100ms |
| State update latency | < 33ms (30fps) |
| Map redraw (80x24) | < 5ms |
| Map redraw (120x50) | < 10ms |
| Panel refresh | < 2ms |
| Key response time | < 16ms |
| Theme switch time | < 50ms |
| Memory overhead | < 50MB |

### TUI Widget Render Times

| Widget | Target |
|--------|--------|
| MapPanel | < 5ms |
| StatusPanel | < 1ms |
| LogPanel (10 lines) | < 1ms |
| InventoryWidget | < 2ms |
| CombatLogWidget | < 1ms |

## 18. Appendix E: Textual CSS Reference
