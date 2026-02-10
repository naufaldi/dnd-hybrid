# src/persistence/migrations.py
"""Database migrations."""

from typing import Callable, List
from .schema import SCHEMA_VERSION


class Migration:
    """Represents a database migration."""

    def __init__(self, from_version: int, to_version: int, upgrade: Callable, downgrade: Callable = None):
        self.from_version = from_version
        self.to_version = to_version
        self.upgrade = upgrade
        self.downgrade = downgrade


# Migration registry
MIGRATIONS: List[Migration] = []


def register_migration(from_version: int, to_version: int):
    """Decorator to register a migration."""
    def decorator(func: Callable):
        MIGRATIONS.append(Migration(from_version, to_version, func))
        return func
    return decorator


class MigrationManager:
    """Manages database migrations."""

    def __init__(self, database):
        self.db = database

    def get_migrations_needed(self, current_version: int, target_version: int) -> List[Migration]:
        """Get list of migrations needed."""
        needed = []
        for migration in MIGRATIONS:
            if current_version <= migration.from_version < target_version:
                needed.append(migration)
        return sorted(needed, key=lambda m: m.from_version)

    def migrate(self, target_version: int) -> None:
        """Apply migrations to reach target version."""
        current = self.db.get_schema_version()
        migrations = self.get_migrations_needed(current, target_version)

        for migration in migrations:
            migration.upgrade(self.db.connection)

        # Update version
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM schema_version")
            cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (target_version,))
