# tests/unit/test_world/test_tile_types.py
"""Tests for Tile types and Tile class."""

import pytest
from src.world.tile_types import Tile, TileType


class TestTileType:
    """Tests for TileType enum."""

    def test_tile_type_values(self):
        """Test that all expected tile types exist."""
        expected_types = [
            'FLOOR', 'WALL', 'DOOR_CLOSED', 'DOOR_OPEN',
            'STAIRS_UP', 'STAIRS_DOWN', 'WATER', 'LAVA',
            'TRAP', 'VOID'
        ]
        for type_name in expected_types:
            assert hasattr(TileType, type_name), f"Missing TileType.{type_name}"


class TestTile:
    """Tests for Tile dataclass."""

    def test_tile_floor(self):
        """Test floor tile creation."""
        tile = Tile.floor()
        assert tile.tile_type == TileType.FLOOR
        assert tile.char == "."
        assert tile.blocking is False
        assert tile.walkable is True

    def test_tile_wall(self):
        """Test wall tile creation."""
        tile = Tile.wall()
        assert tile.tile_type == TileType.WALL
        assert tile.char == "#"
        assert tile.blocking is True
        assert tile.walkable is False
        assert tile.opaque is True

    def test_tile_stairs_down(self):
        """Test stairs down tile creation."""
        tile = Tile.stairs_down()
        assert tile.tile_type == TileType.STAIRS_DOWN
        assert tile.char == ">"
        assert tile.blocking is False
        assert tile.walkable is True

    def test_tile_stairs_up(self):
        """Test stairs up tile creation."""
        tile = Tile.stairs_up()
        assert tile.tile_type == TileType.STAIRS_UP
        assert tile.char == "<"
        assert tile.blocking is False
        assert tile.walkable is True

    def test_tile_door_closed(self):
        """Test closed door tile creation."""
        tile = Tile.door_closed()
        assert tile.tile_type == TileType.DOOR_CLOSED
        assert tile.char == "+"
        assert tile.blocking is True
        assert tile.walkable is False

    def test_tile_door_open(self):
        """Test open door tile creation."""
        tile = Tile.door_open()
        assert tile.tile_type == TileType.DOOR_OPEN
        assert tile.char == "/"
        assert tile.blocking is False
        assert tile.walkable is True

    def test_tile_water(self):
        """Test water tile creation."""
        tile = Tile.water()
        assert tile.tile_type == TileType.WATER
        assert tile.char == "~"
        assert tile.walkable is False

    def test_tile_lava(self):
        """Test lava tile creation."""
        tile = Tile.lava()
        assert tile.tile_type == TileType.LAVA
        assert tile.char == "="
        assert tile.walkable is False

    def test_tile_void(self):
        """Test void tile creation."""
        tile = Tile.void()
        assert tile.tile_type == TileType.VOID
        assert tile.char == " "
        assert tile.blocking is True
        assert tile.walkable is False
        assert tile.opaque is True

    def test_tile_custom(self):
        """Test custom tile creation."""
        tile = Tile(
            tile_type=TileType.TRAP,
            char="^",
            color="red",
            blocking=False,
            walkable=True,
            opaque=False
        )
        assert tile.tile_type == TileType.TRAP
        assert tile.char == "^"
        assert tile.color == "red"
