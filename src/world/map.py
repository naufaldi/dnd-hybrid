# src/world/map.py
"""Map implementation."""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set
from .tile_types import Tile, TileType


@dataclass
class Room:
    """A room in the dungeon."""

    id: str
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def intersects(self, other: "Room") -> bool:
        """Check if this room intersects with another."""
        ax1, ay1, ax2, ay2 = self.bounds
        bx1, by1, bx2, by2 = other.bounds
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    def contains(self, x: int, y: int) -> bool:
        """Check if point is inside room."""
        ax1, ay1, ax2, ay2 = self.bounds
        return ax1 <= x < ax2 and ay1 <= y < ay2


@dataclass
class GameMap:
    """The game map."""

    width: int
    height: int
    tiles: List[List[Tile]] = field(default_factory=list)
    rooms: List[Room] = field(default_factory=list)
    explored_tiles: Set[Tuple[int, int]] = field(default_factory=set)
    seed: Optional[int] = None

    def __post_init__(self):
        if not self.tiles:
            self.tiles = [[Tile.floor() for _ in range(self.width)] for _ in range(self.height)]

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position, returns None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        """Set tile at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable."""
        tile = self.get_tile(x, y)
        return tile is not None and tile.walkable

    def is_transparent(self, x: int, y: int) -> bool:
        """Check if position is transparent (blocks sight)."""
        tile = self.get_tile(x, y)
        return tile is not None and tile.transparent

    def is_blocking(self, x: int, y: int) -> bool:
        """Check if position blocks movement."""
        tile = self.get_tile(x, y)
        return tile is None or tile.blocking

    def is_opaque(self, x: int, y: int) -> bool:
        """Check if position is opaque (blocks FOV)."""
        tile = self.get_tile(x, y)
        return tile is None or tile.opaque

    def mark_explored(self, x: int, y: int) -> None:
        """Mark tile as explored."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.explored_tiles.add((x, y))

    def is_explored(self, x: int, y: int) -> bool:
        """Check if tile has been explored."""
        return (x, y) in self.explored_tiles

    def get_rooms(self) -> List[Room]:
        """Get all rooms."""
        return self.rooms

    def add_room(self, room: Room) -> None:
        """Add a room to the map."""
        self.rooms.append(room)

    def find_random_floor_tile(self) -> Optional[Tuple[int, int]]:
        """Find a random walkable floor tile."""
        attempts = 0
        while attempts < 1000:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.is_walkable(x, y):
                return (x, y)
            attempts += 1
        return None

    def find_random_wall_tile(self) -> Optional[Tuple[int, int]]:
        """Find a random wall tile adjacent to a floor."""
        for _ in range(1000):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_blocking(x, y):
                # Check if adjacent to walkable
                if (self.is_walkable(x + 1, y) or self.is_walkable(x - 1, y) or
                    self.is_walkable(x, y + 1) or self.is_walkable(x, y - 1)):
                    return (x, y)
        return None
