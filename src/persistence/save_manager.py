# src/persistence/save_manager.py
"""Save/load manager with compression."""

import json
import hashlib
import zlib
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone


SAVE_FORMAT_VERSION = 1


class SaveManager:
    """Manages game saves with compression and validation."""

    def __init__(self, save_dir: Path, db_path: Optional[Path] = None):
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
        # Import here to avoid circular imports
        from .database import Database
        self.db = Database(db_path or save_dir / "game.db")

    def save_game(self, game_state: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Save game with compression."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            character_id = game_state.get("character", {}).get("id", "game")
            filename = f"{character_id}_{timestamp}.sav"

        # Calculate checksum on game_state before adding metadata
        game_state_json = json.dumps(game_state, sort_keys=True, default=str)
        game_state_bytes = game_state_json.encode("utf-8")
        checksum = hashlib.sha256(game_state_bytes).hexdigest()

        save_data = {
            "version": SAVE_FORMAT_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_state": game_state,
            "checksum": checksum,
        }

        # Serialize to JSON and compress
        json_data = json.dumps(save_data, indent=2, default=str)
        compressed = zlib.compress(json_data.encode("utf-8"), level=6)

        # Write to file
        save_path = self.save_dir / filename
        with open(save_path, "wb") as f:
            f.write(compressed)

        return save_path

    def load_game(self, save_path: Path) -> Tuple[Dict[str, Any], str]:
        """Load and decompress game."""
        from src.utils.exceptions import SaveCorruptionError

        with open(save_path, "rb") as f:
            compressed = f.read()

        # Decompress
        try:
            decompressed = zlib.decompress(compressed)
        except (zlib.error, OSError):
            raise SaveCorruptionError(str(save_path))

        # Parse JSON
        try:
            save_data = json.loads(decompressed)
        except json.JSONDecodeError:
            raise SaveCorruptionError(str(save_path))

        # Verify checksum
        json_bytes = json.dumps(save_data["game_state"], sort_keys=True, default=str).encode("utf-8")
        calculated_checksum = hashlib.sha256(json_bytes).hexdigest()

        if calculated_checksum != save_data.get("checksum"):
            raise SaveCorruptionError(str(save_path))

        # Check version
        if save_data.get("version", 0) < SAVE_FORMAT_VERSION:
            save_data = self._migrate_save(save_data)

        return save_data["game_state"], save_data.get("timestamp", "")

    def _migrate_save(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate save to current version."""
        # Handle version migrations here
        return save_data

    def list_saves(self) -> list:
        """List all save files."""
        saves = []
        for f in self.save_dir.glob("*.sav"):
            stat = f.stat()
            saves.append({
                "filename": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
            })
        return sorted(saves, key=lambda x: x["modified"], reverse=True)

    def delete_save(self, filename: str) -> None:
        """Delete a save file."""
        (self.save_dir / filename).unlink(missing_ok=True)

    def get_latest_save(self) -> Optional[Path]:
        """Get the most recent save file."""
        saves = self.list_saves()
        if not saves:
            return None
        return self.save_dir / saves[0]["filename"]


def create_save_manager(save_dir: Optional[Path] = None) -> SaveManager:
    """Convenience function to create a save manager."""
    if save_dir is None:
        save_dir = Path.home() / ".dnd_roguelike" / "saves"
    return SaveManager(save_dir)
