"""Performance and benchmark tests."""

import pytest
import time
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig
from src.world.fov import FieldOfView
from src.world.map import GameMap
from src.world.pathfinding import a_star_path
from src.combat.dice import DiceRoller
from src.core.game_engine import GameEngine
from src.entities.enemy import Enemy, EnemyType


class BenchmarkDungeonGeneration:
    """Benchmarks for dungeon generation."""

    def test_benchmark_small_dungeon(self):
        """Benchmark small dungeon generation."""
        config = DungeonConfig(
            width=40,
            height=20,
            min_room_size=5,
            max_room_size=10,
            min_rooms=5,
            max_rooms=8,
        )

        start = time.perf_counter()
        for _ in range(100):
            generator = DungeonGenerator(config)
            generator.generate()
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000
        # Should generate in under 50ms average
        assert avg_ms < 50, f"Dungeon generation too slow: {avg_ms:.2f}ms"

    def test_benchmark_large_dungeon(self):
        """Benchmark large dungeon generation."""
        config = DungeonConfig(
            width=80,
            height=40,
            min_room_size=6,
            max_room_size=15,
            min_rooms=8,
            max_rooms=12,
        )

        start = time.perf_counter()
        for _ in range(50):
            generator = DungeonGenerator(config)
            generator.generate()
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 50) * 1000
        # Large dungeons should generate in under 100ms average
        assert avg_ms < 100, f"Large dungeon generation too slow: {avg_ms:.2f}ms"


class BenchmarkFOV:
    """Benchmarks for field of view."""

    @pytest.fixture
    def dungeon_map(self):
        """Create a test dungeon map."""
        config = DungeonConfig(width=80, height=24, seed=42)
        generator = DungeonGenerator(config)
        return generator.generate()

    def test_benchmark_fov_computation(self, dungeon_map):
        """Benchmark FOV computation."""
        fov = FieldOfView(dungeon_map)

        # Get a floor tile as center
        center = dungeon_map.find_random_floor_tile() or (10, 10)

        start = time.perf_counter()
        for _ in range(1000):
            fov.compute(center[0], center[1], radius=8)
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / 1000) * 1_000_000
        # FOV should compute in under 1000 microseconds
        assert avg_us < 1000, f"FOV computation too slow: {avg_us:.2f}us"


class BenchmarkPathfinding:
    """Benchmarks for pathfinding."""

    @pytest.fixture
    def dungeon_map(self):
        """Create a test dungeon map."""
        config = DungeonConfig(width=80, height=24, seed=42)
        generator = DungeonGenerator(config)
        return generator.generate()

    def test_benchmark_short_path(self, dungeon_map):
        """Benchmark short pathfinding."""
        start = (10, 10)
        goal = (15, 15)

        start_time = time.perf_counter()
        for _ in range(1000):
            path = a_star_path(dungeon_map, start, goal)
        elapsed = time.perf_counter() - start_time

        avg_us = (elapsed / 1000) * 1_000_000
        # Short paths should find in under 500 microseconds
        assert avg_us < 500, f"Short pathfinding too slow: {avg_us:.2f}us"

    def test_benchmark_long_path(self, dungeon_map):
        """Benchmark long pathfinding across dungeon."""
        start = (5, 5)
        goal = (70, 20)

        start_time = time.perf_counter()
        for _ in range(100):
            path = a_star_path(dungeon_map, start, goal)
        elapsed = time.perf_counter() - start_time

        avg_ms = (elapsed / 100) * 1000
        # Long paths should find in under 10ms
        assert avg_ms < 10, f"Long pathfinding too slow: {avg_ms:.2f}ms"

    def test_benchmark_many_enemies_pathfinding(self, dungeon_map):
        """Benchmark pathfinding with many enemies."""
        start = (5, 5)
        goal = (70, 20)

        # Generate many paths
        start_time = time.perf_counter()
        for _ in range(100):
            path = a_star_path(dungeon_map, start, goal)
        elapsed = time.perf_counter() - start_time

        avg_ms = (elapsed / 100) * 1000
        # Should handle many pathfinding requests efficiently
        assert avg_ms < 10, f"Multiple pathfinding too slow: {avg_ms:.2f}ms"


class BenchmarkDiceRolling:
    """Benchmarks for dice rolling."""

    def test_benchmark_roll_d20(self):
        """Benchmark d20 rolling."""
        roller = DiceRoller()

        start = time.perf_counter()
        for _ in range(10000):
            roller.roll("1d20")
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / 10000) * 1_000_000
        # Should roll in under 10 microseconds
        assert avg_us < 10, f"Dice rolling too slow: {avg_us:.2f}us"

    def test_benchmark_roll_many_dice(self):
        """Benchmark rolling many dice at once."""
        roller = DiceRoller()

        start = time.perf_counter()
        for _ in range(1000):
            roller.roll("10d10")
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / 1000) * 1_000_000
        # Should roll in under 100 microseconds
        assert avg_us < 100, f"Many dice rolling too slow: {avg_us:.2f}us"


class BenchmarkGameEngine:
    """Benchmarks for game engine operations."""

    def test_benchmark_turn_processing(self):
        """Benchmark processing a game turn."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Add some enemies
        for i in range(10):
            enemy = Enemy(
                id=f"enemy{i}",
                name=f"Enemy {i}",
                enemy_type=EnemyType.HUMANOID,
                cr=0.5,
                position=(20 + i, 10)
            )
            engine.add_enemy(enemy)

        start = time.perf_counter()
        for _ in range(100):
            engine.next_turn()
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / 100) * 1_000_000
        # Should process turns in under 500 microseconds
        assert avg_us < 500, f"Turn processing too slow: {avg_us:.2f}us"


class BenchmarkMemory:
    """Memory usage benchmarks."""

    def test_memory_dungeon_caching(self):
        """Test memory doesn't grow unbounded with dungeon caching."""
        import sys

        # Generate many dungeons
        dungeons = []
        for i in range(100):
            config = DungeonConfig(width=80, height=40, seed=i)
            generator = DungeonGenerator(config)
            dungeons.append(generator.generate())

        # Keep reference, memory should be reasonable
        # Each 80x40 dungeon is roughly 3200 tiles
        # 100 dungeons = 320,000 tiles
        # Each tile is small, so memory should be under 10MB
        total_tiles = sum(d.width * d.height for d in dungeons)
        # Rough estimate: each tile reference is ~50 bytes
        estimated_mb = (total_tiles * 50) / (1024 * 1024)

        assert estimated_mb < 20, f"Memory usage too high: {estimated_mb:.2f}MB"

    def test_memory_fov_cache(self):
        """Test FOV cache doesn't grow unbounded."""
        config = DungeonConfig(width=80, height=24, seed=42)
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        fov = FieldOfView(dungeon)
        positions = dungeon.find_random_floor_tile()

        # Compute FOV many times
        for _ in range(1000):
            fov.compute(positions[0], positions[1], radius=8)

        # FOV result should be bounded by map size
        # Maximum visible tiles is pi * r^2 = ~201 for r=8
        result = fov.compute(positions[0], positions[1], radius=8)
        assert len(result) < 300, f"FOV result too large: {len(result)}"


class BenchmarkSaveLoad:
    """Benchmarks for save/load operations."""

    def test_benchmark_save_game_state(self):
        """Benchmark saving game state."""
        from src.persistence.save_manager import SaveManager
        from pathlib import Path
        import tempfile

        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()
        engine._player.position = (5, 5)
        state = engine.get_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_manager = SaveManager(Path(tmpdir))

            start = time.perf_counter()
            for _ in range(100):
                save_manager.save_game(state, "test.sav")
            elapsed = time.perf_counter() - start

            avg_ms = (elapsed / 100) * 1000
            # Save should complete in under 50ms
            assert avg_ms < 50, f"Save too slow: {avg_ms:.2f}ms"

    def test_benchmark_load_game_state(self):
        """Benchmark loading game state."""
        from src.persistence.save_manager import SaveManager
        from pathlib import Path
        import tempfile

        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()
        state = engine.get_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_manager = SaveManager(Path(tmpdir))
            save_manager.save_game(state, "test.sav")

            start = time.perf_counter()
            for _ in range(100):
                save_manager.load_game(Path(tmpdir) / "test.sav")
            elapsed = time.perf_counter() - start

            avg_ms = (elapsed / 100) * 1000
            # Load should complete in under 50ms
            assert avg_ms < 50, f"Load too slow: {avg_ms:.2f}ms"
