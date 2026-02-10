# src/persistence/schema.py
"""SQL schema definitions."""

# Schema version
SCHEMA_VERSION = 1

# Character table
CREATE_CHARACTERS_TABLE = """
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    character_class TEXT NOT NULL,
    race TEXT NOT NULL,
    background TEXT,
    strength INTEGER NOT NULL,
    dexterity INTEGER NOT NULL,
    constitution INTEGER NOT NULL,
    intelligence INTEGER NOT NULL,
    wisdom INTEGER NOT NULL,
    charisma INTEGER NOT NULL,
    hit_points INTEGER NOT NULL,
    temporary_hp INTEGER DEFAULT 0,
    exhaustion_level INTEGER DEFAULT 0,
    alive INTEGER DEFAULT 1,
    death_save_successes INTEGER DEFAULT 0,
    death_save_failures INTEGER DEFAULT 0,
    current_floor INTEGER DEFAULT 1,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    damage_dealt INTEGER DEFAULT 0,
    damage_taken INTEGER DEFAULT 0,
    turns_survived INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# Class resources table
CREATE_CLASS_RESOURCES_TABLE = """
CREATE TABLE IF NOT EXISTS class_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_level INTEGER,
    current_value INTEGER,
    max_value INTEGER,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
"""

# Inventory items table
CREATE_INVENTORY_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS inventory_items (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    name TEXT NOT NULL,
    item_type TEXT NOT NULL,
    rarity TEXT NOT NULL,
    weight REAL DEFAULT 0,
    quantity INTEGER DEFAULT 1,
    stackable INTEGER DEFAULT 0,
    max_stack INTEGER DEFAULT 1,
    magical_bonus INTEGER DEFAULT 0,
    description TEXT,
    equipped INTEGER DEFAULT 0,
    slot TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
"""

# World state table
CREATE_WORLD_STATES_TABLE = """
CREATE TABLE IF NOT EXISTS world_states (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    floor_number INTEGER NOT NULL,
    dungeon_seed INTEGER NOT NULL,
    explored_tiles TEXT NOT NULL,
    room_data TEXT NOT NULL,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
"""

# Kills tracking table
CREATE_KILLS_TABLE = """
CREATE TABLE IF NOT EXISTS kills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    enemy_type TEXT NOT NULL,
    kill_count INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
"""

# Schema version table
CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""

# All tables in order
ALL_TABLES = [
    CREATE_SCHEMA_VERSION_TABLE,
    CREATE_CHARACTERS_TABLE,
    CREATE_CLASS_RESOURCES_TABLE,
    CREATE_INVENTORY_ITEMS_TABLE,
    CREATE_WORLD_STATES_TABLE,
    CREATE_KILLS_TABLE,
]

# Indexes
CREATE_CHARACTER_NAME_INDEX = "CREATE INDEX IF NOT EXISTS idx_character_name ON characters(name);"
CREATE_WORLD_STATE_INDEX = "CREATE INDEX IF NOT EXISTS idx_world_state_character ON world_states(character_id, floor_number);"
CREATE_KILLS_INDEX = "CREATE INDEX IF NOT EXISTS idx_kills_character ON kills(character_id, enemy_type);"

ALL_INDEXES = [
    CREATE_CHARACTER_NAME_INDEX,
    CREATE_WORLD_STATE_INDEX,
    CREATE_KILLS_INDEX,
]
