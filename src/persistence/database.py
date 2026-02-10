# src/persistence/database.py
"""SQLite database wrapper."""

import sqlite3
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .schema import ALL_TABLES, ALL_INDEXES, SCHEMA_VERSION


class Database:
    """SQLite database wrapper."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @contextmanager
    def transaction(self):
        """Context manager for transactions."""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def initialize(self) -> None:
        """Initialize database schema."""
        with self.transaction() as cursor:
            # Create tables
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)

            # Create indexes
            for index_sql in ALL_INDEXES:
                cursor.execute(index_sql)

            # Set schema version
            cursor.execute("DELETE FROM schema_version")
            cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_schema_version(self) -> int:
        """Get current schema version."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0

    def save_character(self, character: Dict[str, Any]) -> None:
        """Save character to database."""
        with self.transaction() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO characters (
                    id, name, level, experience, character_class, race, background,
                    strength, dexterity, constitution, intelligence, wisdom, charisma,
                    hit_points, temporary_hp, exhaustion_level, alive,
                    death_save_successes, death_save_failures, current_floor,
                    position_x, position_y, damage_dealt, damage_taken, turns_survived,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                character["id"], character["name"], character["level"], character["experience"],
                character["character_class"], character["race"], character.get("background", ""),
                character["strength"], character["dexterity"], character["constitution"],
                character["intelligence"], character["wisdom"], character["charisma"],
                character["hit_points"], character.get("temporary_hp", 0),
                character.get("exhaustion_level", 0), 1 if character.get("alive", True) else 0,
                character.get("death_save_successes", 0), character.get("death_save_failures", 0),
                character.get("current_floor", 1),
                character.get("position_x", 0), character.get("position_y", 0),
                character.get("damage_dealt", 0), character.get("damage_taken", 0),
                character.get("turns_survived", 0),
            ))

    def load_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load character from database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def delete_character(self, character_id: str) -> None:
        """Delete character from database."""
        with self.transaction() as cursor:
            cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))

    def list_characters(self) -> List[Dict[str, Any]]:
        """List all characters."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, level, character_class, race FROM characters ORDER BY updated_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def save_world_state(self, character_id: str, floor: int, seed: int, explored: str, rooms: str) -> None:
        """Save world state for a floor."""
        with self.transaction() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO world_states (id, character_id, floor_number, dungeon_seed, explored_tiles, room_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), character_id, floor, seed, explored, rooms))

    def load_world_state(self, character_id: str, floor: int) -> Optional[Dict[str, Any]]:
        """Load world state for a floor."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM world_states WHERE character_id = ? AND floor_number = ?
        """, (character_id, floor))
        row = cursor.fetchone()
        return dict(row) if row else None

    def save_kill(self, character_id: str, enemy_type: str) -> None:
        """Record a kill."""
        with self.transaction() as cursor:
            # Try to update existing kill count first
            cursor.execute("""
                UPDATE kills SET kill_count = kill_count + 1
                WHERE character_id = ? AND enemy_type = ?
            """, (character_id, enemy_type))
            # If no rows updated, insert new kill
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO kills (character_id, enemy_type, kill_count)
                    VALUES (?, ?, 1)
                """, (character_id, enemy_type))

    def get_kills(self, character_id: str) -> List[Dict[str, Any]]:
        """Get kill counts for character."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT enemy_type, kill_count FROM kills WHERE character_id = ?", (character_id,))
        return [dict(row) for row in cursor.fetchall()]
