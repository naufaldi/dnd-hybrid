# src/world/dungeon_generator.py
"""Procedural dungeon generation using BSP and Cellular Automata."""

import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from .map import GameMap, Room
from .tile_types import Tile
from .fov import FieldOfView


@dataclass
class DungeonConfig:
    """Configuration for dungeon generation."""

    width: int = 80
    height: int = 40
    min_room_size: int = 5
    max_room_size: int = 15
    min_rooms: int = 5
    max_rooms: int = 10
    seed: Optional[int] = None
    use_cave: bool = False
    cave_density: float = 0.45

    def __post_init__(self):
        if self.seed is None:
            self.seed = random.randint(0, 999999999)


@dataclass
class BSPNode:
    """Binary Space Partitioning node."""

    x: int
    y: int
    width: int
    height: int
    left: Optional["BSPNode"] = None
    right: Optional["BSPNode"] = None
    room: Optional[Room] = None


class DungeonGenerator:
    """Dungeon generator using BSP and Cellular Automata."""

    def __init__(self, config: DungeonConfig):
        self.config = config
        self.map: Optional[GameMap] = None
        self.rooms: List[Room] = []

        if config.seed is not None:
            random.seed(config.seed)

    def generate(self) -> GameMap:
        """Generate a complete dungeon."""
        self.map = GameMap(
            width=self.config.width,
            height=self.config.height,
            seed=self.config.seed
        )

        # Fill with walls (overriding default floors)
        for y in range(self.map.height):
            for x in range(self.map.width):
                self.map.set_tile(x, y, Tile.wall())

        if self.config.use_cave:
            self._generate_caves()
        else:
            self._generate_bsp_rooms()
            self._connect_rooms()

        # Place stairs
        self._place_stairs()

        return self.map

    @classmethod
    def generate_dungeon(cls, config: Optional[DungeonConfig] = None) -> GameMap:
        """Convenience class method to generate a dungeon."""
        if config is None:
            config = DungeonConfig()
        generator = cls(config)
        return generator.generate()

    def _generate_bsp_rooms(self) -> None:
        """Generate rooms using BSP."""
        # Build BSP tree
        root = BSPNode(1, 1, self.config.width - 2, self.config.height - 2)
        self._build_bsp(root, depth=0)

        # Extract rooms from leaf nodes
        self._extract_bsp_rooms(root)

        # Carve rooms
        for room in self.rooms:
            self._carve_room(room)

    def _build_bsp(self, node: BSPNode, depth: int) -> None:
        """Recursively build BSP tree."""
        max_depth = 5

        # Determine if we should split
        can_split_horizontally = node.width > self.config.max_room_size * 2
        can_split_vertically = node.height > self.config.max_room_size * 2

        if depth < max_depth and (can_split_horizontally or can_split_vertically):
            # Decide split direction
            if can_split_horizontally and can_split_vertically:
                split_horizontal = random.choice([True, False])
            elif can_split_horizontally:
                split_horizontal = True
            else:
                split_horizontal = False

            if split_horizontal:
                # Horizontal split (top/bottom)
                min_split = self.config.min_room_size
                max_split = node.height - self.config.min_room_size
                if min_split >= max_split:
                    return  # Cannot split
                split_point = random.randint(min_split, max_split)
                node.left = BSPNode(node.x, node.y, node.width, split_point)
                node.right = BSPNode(node.x, node.y + split_point, node.width, node.height - split_point)
            else:
                # Vertical split (left/right)
                min_split = self.config.min_room_size
                max_split = node.width - self.config.min_room_size
                if min_split >= max_split:
                    return  # Cannot split
                split_point = random.randint(min_split, max_split)
                node.left = BSPNode(node.x, node.y, split_point, node.height)
                node.right = BSPNode(node.x + split_point, node.y, node.width - split_point, node.height)

            self._build_bsp(node.left, depth + 1)
            self._build_bsp(node.right, depth + 1)

    def _extract_bsp_rooms(self, node: BSPNode) -> None:
        """Extract rooms from BSP leaf nodes."""
        if node.left is None and node.right is None:
            # This is a leaf - create a room
            room_width = random.randint(self.config.min_room_size, min(self.config.max_room_size, node.width))
            room_height = random.randint(self.config.min_room_size, min(self.config.max_room_size, node.height))

            # Center room in partition
            room_x = node.x + (node.width - room_width) // 2
            room_y = node.y + (node.height - room_height) // 2

            room = Room(
                id=f"room_{len(self.rooms)}",
                x=room_x,
                y=room_y,
                width=room_width,
                height=room_height
            )
            node.room = room
            self.rooms.append(room)
        else:
            # Recurse into children
            if node.left:
                self._extract_bsp_rooms(node.left)
            if node.right:
                self._extract_bsp_rooms(node.right)

    def _carve_room(self, room: Room) -> None:
        """Carve a room into the map."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.map.width and 0 <= y < self.map.height:
                    self.map.set_tile(x, y, Tile.floor())

        # Add walls around room edges (ensure edges are walls)
        for y in range(room.y - 1, room.y + room.height + 1):
            for x in range(room.x - 1, room.x + room.width + 1):
                if 0 <= x < self.map.width and 0 <= y < self.map.height:
                    tile = self.map.get_tile(x, y)
                    if tile and tile.tile_type.name == "WALL":
                        # Only set wall if not part of a room
                        is_in_room = any(
                            room.x <= x < room.x + room.width and
                            room.y <= y < room.y + room.height
                            for room in self.rooms
                        )
                        if not is_in_room:
                            self.map.set_tile(x, y, Tile.wall())

    def _connect_rooms(self) -> None:
        """Connect rooms with corridors."""
        if len(self.rooms) < 2:
            return

        # Connect rooms in sequence
        for i in range(len(self.rooms) - 1):
            room_a = self.rooms[i]
            room_b = self.rooms[i + 1]
            self._connect_two_rooms(room_a, room_b)

    def _connect_two_rooms(self, room_a: Room, room_b: Room) -> None:
        """Connect two rooms with L-shaped corridor."""
        center_a = room_a.center
        center_b = room_b.center

        # Randomly choose horizontal or vertical first
        if random.choice([True, False]):
            # Horizontal then vertical
            self._carve_horizontal_corridor(center_a[0], center_b[0], center_a[1])
            self._carve_vertical_corridor(center_a[1], center_b[1], center_b[0])
        else:
            # Vertical then horizontal
            self._carve_vertical_corridor(center_a[1], center_b[1], center_a[0])
            self._carve_horizontal_corridor(center_a[0], center_b[0], center_b[1])

    def _carve_horizontal_corridor(self, x1: int, x2: int, y: int) -> None:
        """Carve horizontal corridor."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.map.width and 0 <= y < self.map.height:
                tile = self.map.get_tile(x, y)
                if tile and tile.tile_type.name == "WALL":
                    self.map.set_tile(x, y, Tile.floor())

    def _carve_vertical_corridor(self, y1: int, y2: int, x: int) -> None:
        """Carve vertical corridor."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.map.width and 0 <= y < self.map.height:
                tile = self.map.get_tile(x, y)
                if tile and tile.tile_type.name == "WALL":
                    self.map.set_tile(x, y, Tile.floor())

    def _generate_caves(self) -> None:
        """Generate cave system using cellular automata."""
        # Initialize with random noise
        for y in range(self.map.height):
            for x in range(self.map.width):
                if random.random() < self.config.cave_density:
                    self.map.set_tile(x, y, Tile.floor())
                else:
                    self.map.set_tile(x, y, Tile.wall())

        # Apply cellular automata rules
        for _ in range(5):
            self._apply_cellular_automata()

        # Ensure connectivity
        self._ensure_cave_connectivity()

    def _apply_cellular_automata(self) -> None:
        """Apply cellular automata smoothing."""
        new_tiles = [[self.map.get_tile(x, y) for x in range(self.map.width)]
                     for y in range(self.map.height)]

        for y in range(self.map.height):
            for x in range(self.map.width):
                neighbors = self._count_floor_neighbors(x, y)

                if neighbors > 4:
                    new_tiles[y][x] = Tile.floor()
                elif neighbors < 4:
                    new_tiles[y][x] = Tile.wall()

        for y in range(self.map.height):
            for x in range(self.map.width):
                self.map.set_tile(x, y, new_tiles[y][x])

    def _count_floor_neighbors(self, x: int, y: int) -> int:
        """Count floor neighbors."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.map.width and 0 <= ny < self.map.height:
                    tile = self.map.get_tile(nx, ny)
                    if tile and tile.tile_type.name == "FLOOR":
                        count += 1
        return count

    def _ensure_cave_connectivity(self) -> None:
        """Ensure cave is connected (flood fill and fill disconnected)."""
        # Find largest connected floor area
        visited = set()
        largest_area = []

        for y in range(self.map.height):
            for x in range(self.map.width):
                if (x, y) not in visited:
                    tile = self.map.get_tile(x, y)
                    if tile and tile.tile_type.name == "FLOOR":
                        area = self._flood_fill(x, y, visited)
                        if len(area) > len(largest_area):
                            largest_area = area

        # Fill all but largest area with walls
        for y in range(self.map.height):
            for x in range(self.map.width):
                if (x, y) not in largest_area:
                    tile = self.map.get_tile(x, y)
                    if tile and tile.tile_type.name == "FLOOR":
                        self.map.set_tile(x, y, Tile.wall())

    def _flood_fill(self, start_x: int, start_y: int, visited: set) -> List[Tuple[int, int]]:
        """Flood fill from starting point."""
        area = []
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if x < 0 or x >= self.map.width or y < 0 or y >= self.map.height:
                continue

            tile = self.map.get_tile(x, y)
            if not tile or tile.tile_type.name != "FLOOR":
                continue

            visited.add((x, y))
            area.append((x, y))

            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

        return area

    def _place_stairs(self) -> None:
        """Place stairs in the dungeon."""
        if not self.rooms:
            return

        # Place stairs down in last room
        last_room = self.rooms[-1]
        center = last_room.center
        self.map.set_tile(center[0], center[1], Tile.stairs_down())

        # Place stairs up in first room
        first_room = self.rooms[0]
        center = first_room.center
        self.map.set_tile(center[0], center[1], Tile.stairs_up())


def generate_dungeon(config: Optional[DungeonConfig] = None) -> GameMap:
    """Convenience function to generate a dungeon."""
    if config is None:
        config = DungeonConfig()
    generator = DungeonGenerator(config)
    return generator.generate()
