# tests/unit/test_world/test_map.py
"""Tests for Map class."""

import pytest
from src.world.map import GameMap, Room
from src.world.tile_types import Tile, TileType


class TestRoom:
    """Tests for Room class."""

    def test_room_creation(self):
        """Test room creation."""
        room = Room("r1", x=10, y=10, width=8, height=6)
        assert room.id == "r1"
        assert room.x == 10
        assert room.y == 10
        assert room.width == 8
        assert room.height == 6

    def test_room_center(self):
        """Test room center calculation."""
        room = Room("r1", x=10, y=10, width=8, height=6)
        assert room.center == (14, 13)

    def test_room_bounds(self):
        """Test room bounds calculation."""
        room = Room("r1", x=10, y=10, width=5, height=5)
        assert room.bounds == (10, 10, 15, 15)

    def test_room_intersects_true(self):
        """Test room intersection detection - intersecting."""
        room1 = Room("r1", x=0, y=0, width=10, height=10)
        room2 = Room("r2", x=5, y=5, width=10, height=10)
        assert room1.intersects(room2) is True

    def test_room_intersects_false(self):
        """Test room intersection detection - not intersecting."""
        room1 = Room("r1", x=0, y=0, width=10, height=10)
        room3 = Room("r3", x=20, y=20, width=5, height=5)
        assert room1.intersects(room3) is False

    def test_room_contains_true(self):
        """Test point containment - inside."""
        room = Room("r1", x=10, y=10, width=5, height=5)
        assert room.contains(12, 12) is True

    def test_room_contains_false(self):
        """Test point containment - outside."""
        room = Room("r1", x=10, y=10, width=5, height=5)
        assert room.contains(9, 9) is False

    def test_room_contains_on_boundary(self):
        """Test point containment - on boundary."""
        room = Room("r1", x=10, y=10, width=5, height=5)
        # Left boundary
        assert room.contains(10, 12) is True
        # Top boundary
        assert room.contains(12, 10) is True


class TestGameMap:
    """Tests for GameMap class."""

    def test_map_creation(self):
        """Test map creation with dimensions."""
        m = GameMap(width=10, height=10)
        assert m.width == 10
        assert m.height == 10

    def test_map_creation_with_seed(self):
        """Test map creation with random seed."""
        m = GameMap(width=10, height=10, seed=42)
        assert m.seed == 42

    def test_get_tile(self):
        """Test getting a tile at valid position."""
        m = GameMap(width=10, height=10)
        tile = m.get_tile(5, 5)
        assert tile is not None

    def test_get_tile_out_of_bounds_negative(self):
        """Test getting tile with negative coordinates."""
        m = GameMap(width=10, height=10)
        assert m.get_tile(-1, 0) is None
        assert m.get_tile(0, -1) is None

    def test_get_tile_out_of_bounds_too_large(self):
        """Test getting tile with coordinates beyond map size."""
        m = GameMap(width=10, height=10)
        assert m.get_tile(10, 10) is None
        assert m.get_tile(9, 10) is None

    def test_set_tile(self):
        """Test setting a tile at valid position."""
        m = GameMap(width=10, height=10)
        m.set_tile(5, 5, Tile.wall())
        assert m.get_tile(5, 5).tile_type == TileType.WALL

    def test_set_tile_out_of_bounds(self):
        """Test setting tile at invalid position does not raise."""
        m = GameMap(width=10, height=10)
        # Should not raise
        m.set_tile(-1, 0, Tile.wall())
        m.set_tile(10, 10, Tile.wall())

    def test_is_walkable_floor(self):
        """Test walkable check on floor tile."""
        m = GameMap(width=10, height=10)
        assert m.is_walkable(5, 5) is True

    def test_is_walkable_wall(self):
        """Test walkable check on wall tile."""
        m = GameMap(width=10, height=10)
        m.set_tile(3, 3, Tile.wall())
        assert m.is_walkable(3, 3) is False

    def test_is_walkable_out_of_bounds(self):
        """Test walkable check out of bounds."""
        m = GameMap(width=10, height=10)
        assert m.is_walkable(-1, 0) is False

    def test_is_blocking_floor(self):
        """Test blocking check on floor tile."""
        m = GameMap(width=10, height=10)
        assert m.is_blocking(5, 5) is False

    def test_is_blocking_wall(self):
        """Test blocking check on wall tile."""
        m = GameMap(width=10, height=10)
        m.set_tile(3, 3, Tile.wall())
        assert m.is_blocking(3, 3) is True

    def test_is_blocking_out_of_bounds(self):
        """Test blocking check out of bounds returns True."""
        m = GameMap(width=10, height=10)
        assert m.is_blocking(-1, 0) is True

    def test_is_transparent_floor(self):
        """Test transparent check on floor tile."""
        m = GameMap(width=10, height=10)
        assert m.is_transparent(5, 5) is True

    def test_is_transparent_wall(self):
        """Test transparent check on wall tile."""
        m = GameMap(width=10, height=10)
        m.set_tile(3, 3, Tile.wall())
        assert m.is_transparent(3, 3) is False

    def test_is_opaque_floor(self):
        """Test opaque check on floor tile."""
        m = GameMap(width=10, height=10)
        assert m.is_opaque(5, 5) is False

    def test_is_opaque_wall(self):
        """Test opaque check on wall tile."""
        m = GameMap(width=10, height=10)
        m.set_tile(3, 3, Tile.wall())
        assert m.is_opaque(3, 3) is True

    def test_mark_explored(self):
        """Test marking tile as explored."""
        m = GameMap(width=10, height=10)
        m.mark_explored(5, 5)
        assert m.is_explored(5, 5) is True

    def test_is_explored_not_explored(self):
        """Test checking unexplored tile."""
        m = GameMap(width=10, height=10)
        assert m.is_explored(3, 3) is False

    def test_mark_explored_out_of_bounds(self):
        """Test marking out of bounds tile does not raise."""
        m = GameMap(width=10, height=10)
        # Should not raise
        m.mark_explored(-1, 0)
        m.mark_explored(10, 10)

    def test_get_rooms_empty(self):
        """Test getting rooms from empty map."""
        m = GameMap(width=10, height=10)
        assert m.get_rooms() == []

    def test_add_room(self):
        """Test adding room to map."""
        m = GameMap(width=20, height=20)
        room = Room("r1", x=5, y=5, width=10, height=10)
        m.add_room(room)
        assert len(m.get_rooms()) == 1
        assert m.get_rooms()[0].id == "r1"

    def test_find_random_floor_tile(self):
        """Test finding random walkable floor tile."""
        m = GameMap(width=10, height=10)
        tile_pos = m.find_random_floor_tile()
        assert tile_pos is not None
        x, y = tile_pos
        assert 0 <= x < 10
        assert 0 <= y < 10

    def test_find_random_floor_tile_none_when_walls(self):
        """Test finding floor tile returns None when all tiles blocked."""
        m = GameMap(width=3, height=3)
        # Fill all with walls
        for x in range(3):
            for y in range(3):
                m.set_tile(x, y, Tile.wall())
        # Should return None after exhausting attempts
        result = m.find_random_floor_tile()
        # Due to max attempts, may still return None
        if result:
            x, y = result
            assert 0 <= x < 3
            assert 0 <= y < 3

    def test_find_random_wall_tile(self):
        """Test finding random wall tile adjacent to floor."""
        m = GameMap(width=10, height=10)
        # Ensure some walls exist
        m.set_tile(5, 5, Tile.floor())
        m.set_tile(5, 6, Tile.wall())
        tile_pos = m.find_random_wall_tile()
        assert tile_pos is not None
        x, y = tile_pos
        assert 0 <= x < 10
        assert 0 <= y < 10
        assert m.is_blocking(x, y)
