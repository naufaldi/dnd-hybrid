"""Game configuration."""

from dataclasses import dataclass, field
from pathlib import Path
import os

AI_CONFIG = {
    "enabled": True,
    "provider": "openrouter",
    "api_key_env": "OPENROUTER_API_KEY",
    "default_model": "openrouter/free",
    "fallback_models": [
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-7b-instruct",
    ],
    "max_tokens": 500,
    "temperature": 0.7,
    "timeout_seconds": 10,
}


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
