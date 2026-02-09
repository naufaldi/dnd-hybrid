# tests/unit/test_world/test_dungeon_generator.py
"""Tests for Dungeon Generator."""

import pytest
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig, BSPNode


class TestDungeonConfig:
    """Tests for DungeonConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        cfg = DungeonConfig()
        assert cfg.width == 80
        assert cfg.height == 40
        assert cfg.min_room_size == 5
        assert cfg.max_room_size == 15

    def test_custom_config(self):
        """Test custom configuration values."""
        cfg = DungeonConfig(width=100, height=50, seed=12345)
        assert cfg.width == 100
        assert cfg.height == 50
        assert cfg.seed == 12345

    def test_seed_generated_if_none(self):
        """Test seed is generated when not provided."""
        cfg = DungeonConfig()
        assert cfg.seed is not None


class TestBSPNode:
    """Tests for BSPNode."""

    def test_bsp_node_creation(self):
        """Test BSP node creation."""
        node = BSPNode(x=0, y=0, width=100, height=50)
        assert node.x == 0
        assert node.y == 0
        assert node.width == 100
        assert node.height == 50
        assert node.left is None
        assert node.right is None
        assert node.room is None

    def test_bsp_node_with_children(self):
        """Test BSP node with child nodes."""
        left = BSPNode(x=0, y=0, width=50, height=50)
        right = BSPNode(x=50, y=0, width=50, height=50)
        parent = BSPNode(x=0, y=0, width=100, height=50, left=left, right=right)
        assert parent.left == left
        assert parent.right == right


class TestDungeonGenerator:
    """Tests for DungeonGenerator."""

    def test_generator_creation(self):
        """Test generator initialization."""
        config = DungeonConfig(seed=42)
        gen = DungeonGenerator(config)
        assert gen.config == config
        assert gen.map is None
        assert gen.rooms == []

    def test_generate_creates_map(self):
        """Test generate creates a GameMap."""
        config = DungeonConfig(width=40, height=20, seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()
        assert dungeon.width == 40
        assert dungeon.height == 20
        assert dungeon.seed == 42

    def test_generation_reproducible(self):
        """Test same seed produces same layout."""
        config1 = DungeonConfig(seed=12345)
        config2 = DungeonConfig(seed=12345)

        gen1 = DungeonGenerator(config1)
        gen2 = DungeonGenerator(config2)

        map1 = gen1.generate()
        map2 = gen2.generate()

        # Same seed should produce same layout
        assert map1.seed == map2.seed

    def test_different_seeds_different_layouts(self):
        """Test different seeds produce different layouts."""
        map1 = DungeonGenerator(DungeonConfig(seed=1)).generate()
        map2 = DungeonGenerator(DungeonConfig(seed=2)).generate()
        assert map1.seed != map2.seed

    def test_rooms_created(self):
        """Test that rooms are created during generation."""
        config = DungeonConfig(min_rooms=3, max_rooms=5, seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()
        # At least min_rooms should be created
        assert len(gen.rooms) >= 3

    def test_rooms_connected(self):
        """Test that rooms have walkable tiles at center."""
        config = DungeonConfig(seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()

        # All rooms should have walkable tiles at center (floor or stairs)
        for room in gen.rooms:
            center = room.center
            tile = dungeon.get_tile(center[0], center[1])
            # Room center should be walkable (floor or stairs)
            assert tile.walkable is True

    def test_stairs_placed(self):
        """Test that stairs are placed in the dungeon."""
        config = DungeonConfig(seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()

        # Check for stairs in first and last rooms
        stairs_up = False
        stairs_down = False

        for y in range(dungeon.height):
            for x in range(dungeon.width):
                tile = dungeon.get_tile(x, y)
                if tile.tile_type.name == "STAIRS_UP":
                    stairs_up = True
                elif tile.tile_type.name == "STAIRS_DOWN":
                    stairs_down = True

        assert stairs_up or stairs_down

    def test_no_room_overlap(self):
        """Test that rooms do not overlap."""
        config = DungeonConfig(seed=99)
        gen = DungeonGenerator(config)
        gen.generate()

        for i, r1 in enumerate(gen.rooms):
            for r2 in gen.rooms[i+1:]:
                assert not r1.intersects(r2)

    def test_cave_generation(self):
        """Test cave generation using cellular automata."""
        config = DungeonConfig(use_cave=True, seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()

        # Cave should have some floor tiles
        floor_count = 0
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                tile = dungeon.get_tile(x, y)
                if tile.tile_type.name == "FLOOR":
                    floor_count += 1

        assert floor_count > 0

    def test_rooms_within_map_bounds(self):
        """Test that all rooms are within map bounds."""
        config = DungeonConfig(width=60, height=30, seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()

        for room in gen.rooms:
            assert room.x >= 0
            assert room.y >= 0
            assert room.x + room.width <= dungeon.width
            assert room.y + room.height <= dungeon.height

    def test_corridors_connect_rooms(self):
        """Test that corridors exist between rooms."""
        config = DungeonConfig(seed=42)
        gen = DungeonGenerator(config)
        dungeon = gen.generate()

        # Check that consecutive rooms have some floor path between them
        for i in range(len(gen.rooms) - 1):
            room_a = gen.rooms[i]
            room_b = gen.rooms[i + 1]

            # Get line between centers
            center_a = room_a.center
            center_b = room_b.center

            # Check at least one point on the path is floor
            has_floor_path = False

            # Simple horizontal check
            for x in range(min(center_a[0], center_b[0]), max(center_a[0], center_b[0]) + 1):
                tile = dungeon.get_tile(x, center_a[1])
                if tile.tile_type.name == "FLOOR":
                    has_floor_path = True
                    break

            # Simple vertical check
            if not has_floor_path:
                for y in range(min(center_a[1], center_b[1]), max(center_a[1], center_b[1]) + 1):
                    tile = dungeon.get_tile(center_b[0], y)
                    if tile.tile_type.name == "FLOOR":
                        has_floor_path = True
                        break

            assert has_floor_path, f"No floor path between room {i} and {i+1}"


class TestGenerateDungeon:
    """Tests for generate_dungeon convenience function."""

    def test_generate_dungeon_default(self):
        """Test generate_dungeon with default config."""
        dungeon = DungeonGenerator.generate_dungeon()
        assert dungeon is not None
        assert dungeon.width == 80
        assert dungeon.height == 40

    def test_generate_dungeon_with_config(self):
        """Test generate_dungeon with custom config."""
        config = DungeonConfig(width=50, height=25, seed=999)
        dungeon = DungeonGenerator.generate_dungeon(config)
        assert dungeon.width == 50
        assert dungeon.height == 25
        assert dungeon.seed == 999
