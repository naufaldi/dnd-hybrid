# src/world/tile_types.py
"""Tile type definitions."""

from dataclasses import dataclass
from enum import Enum, auto


class TileType(Enum):
    """Tile types."""
    FLOOR = auto()
    WALL = auto()
    DOOR_CLOSED = auto()
    DOOR_OPEN = auto()
    STAIRS_UP = auto()
    STAIRS_DOWN = auto()
    WATER = auto()
    LAVA = auto()
    TRAP = auto()
    VOID = auto()


@dataclass
class Tile:
    """Represents a single tile on the map."""

    tile_type: TileType
    char: str = "."
    color: str = "white"
    blocking: bool = False
    transparent: bool = True
    walkable: bool = True
    opaque: bool = False

    @classmethod
    def floor(cls) -> "Tile":
        # blocking, transparent, walkable, opaque
        return cls(TileType.FLOOR, ".", "white", False, True, True, False)

    @classmethod
    def wall(cls) -> "Tile":
        return cls(TileType.WALL, "#", "gray", True, False, False, True)

    @classmethod
    def stairs_down(cls) -> "Tile":
        return cls(TileType.STAIRS_DOWN, ">", "yellow", False, True, True, False)

    @classmethod
    def stairs_up(cls) -> "Tile":
        return cls(TileType.STAIRS_UP, "<", "yellow", False, True, True, False)

    @classmethod
    def door_closed(cls) -> "Tile":
        return cls(TileType.DOOR_CLOSED, "+", "brown", True, False, False, True)

    @classmethod
    def door_open(cls) -> "Tile":
        return cls(TileType.DOOR_OPEN, "/", "brown", False, True, True, False)

    @classmethod
    def water(cls) -> "Tile":
        return cls(TileType.WATER, "~", "blue", False, True, False, False)

    @classmethod
    def lava(cls) -> "Tile":
        return cls(TileType.LAVA, "=", "red", False, True, False, False)

    @classmethod
    def void(cls) -> "Tile":
        return cls(TileType.VOID, " ", "black", True, False, False, True)
