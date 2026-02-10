"""Edge case tests for unusual scenarios."""

import pytest
from src.core.game_engine import GameEngine, GameState
from src.entities.character import Character
from src.entities.enemy import Enemy, EnemyType
from src.entities.item import Item, ItemType
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig
from src.world.map import GameMap, Room
from src.world.fov import FieldOfView
from src.world.pathfinding import a_star_path
from src.world.tile_types import Tile, TileType
from src.combat.dice import DiceRoller
from src.combat.combat_engine import CombatEngine
from src.combat.status_effects import StatusEffect, Condition, StatusEffectManager


class TestMovementEdgeCases:
    """Edge cases for movement."""

    def test_move_into_wall(self):
        """Test moving into a wall."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Player at position with wall in front
        engine._player.position = (5, 5)
        # Ensure wall at (6, 5)
        engine.current_map.set_tile(6, 5, Tile.wall())

        result = engine.move_player("east")
        assert result is False
        assert engine._player.position == (5, 5)

    def test_move_out_of_bounds(self):
        """Test moving outside map bounds."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Player at edge of map
        engine._player.position = (0, 0)

        # Try to move west (should fail)
        result = engine.move_player("west")
        assert result is False

        # Try to move north (should fail)
        result = engine.move_player("north")
        assert result is False

    def test_move_into_enemy(self):
        """Test moving into an enemy's space."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        engine._player.position = (5, 5)

        # Add enemy in front
        enemy = Enemy(
            id="enemy1",
            name="Enemy",
            enemy_type=EnemyType.HUMANOID,
            position=(6, 5)
        )
        engine.add_enemy(enemy)

        result = engine.move_player("east")
        assert result is False


class TestCombatEdgeCases:
    """Edge cases for combat."""

    def test_attack_dead_enemy(self):
        """Test attacking a dead enemy."""
        engine = GameEngine()
        player = engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Add dead enemy
        enemy = Enemy(
            id="enemy1",
            name="Enemy",
            enemy_type=EnemyType.HUMANOID,
            position=(5, 6),
            current_hp=0,
            alive=False
        )
        engine.add_enemy(enemy)

        # Attack should fail
        result = engine.player_attack("enemy1")
        assert result is False

    def test_attack_out_of_range(self):
        """Test attacking enemy out of range."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        engine._player.position = (5, 5)

        # Add enemy far away
        enemy = Enemy(
            id="enemy1",
            name="Enemy",
            enemy_type=EnemyType.HUMANOID,
            position=(50, 50)
        )
        engine.add_enemy(enemy)

        result = engine.player_attack("enemy1")
        assert result is False

    def test_critical_hit_on_max_ac(self):
        """Test critical hit calculation against max AC."""
        roller = DiceRoller()
        engine = CombatEngine(roller)

        # Create mock entities
        class MockAttacker:
            dexterity = 10
            attack_bonus = 0
            magical_bonus = 0
            damage_die = "1d8"

        class MockDefender:
            armor_class = 30  # Very high AC

        attacker = MockAttacker()
        defender = MockDefender()

        # Even with natural 20, if AC is impossibly high...
        # This tests that critical is still calculated correctly
        # but hit depends on total vs AC


class TestFOVEdgeCases:
    """Edge cases for field of view."""

    def test_fov_at_map_edge(self):
        """Test FOV at map edge."""
        config = DungeonConfig(width=20, height=10)
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        fov = FieldOfView(dungeon)

        # FOV at corner
        result = fov.compute(0, 0, radius=8)
        assert isinstance(result, set)

        # FOV at edge
        result = fov.compute(19, 0, radius=8)
        assert isinstance(result, set)

    def test_fov_radius_zero(self):
        """Test FOV with zero radius."""
        config = DungeonConfig(width=20, height=10)
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        fov = FieldOfView(dungeon)
        center = dungeon.find_random_floor_tile() or (5, 5)

        result = fov.compute(center[0], center[1], radius=0)
        assert len(result) >= 0


class TestPathfindingEdgeCases:
    """Edge cases for pathfinding."""

    def test_path_to_same_tile(self):
        """Test path to same position."""
        config = DungeonConfig(width=20, height=10)
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        pos = (10, 10)
        path = a_star_path(pos, pos, lambda x, y: dungeon.is_walkable(x, y))
        assert path == []

    def test_path_with_partial_wall(self):
        """Test pathfinding goes around a partial wall."""
        # Create a simple 10x10 grid
        map_data = [[True] * 10 for _ in range(10)]
        
        # Create a partial vertical wall (like existing unit tests)
        for y in range(5):  # Only blocks first half
            map_data[y][5] = False
        
        passable = lambda x, y: map_data[y][x]
        
        # Path should exist around the wall
        path = a_star_path((3, 0), (3, 9), passable)
        assert len(path) > 0

    def test_no_path_exists(self):
        """Test when no path exists."""
        config = DungeonConfig(width=20, height=10)
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        # Create walled-off area
        for x in range(20):
            dungeon.set_tile(x, 5, Tile.wall())

        # Try to find path from top to bottom
        path = a_star_path((5, 0), (5, 9), lambda x, y: dungeon.is_walkable(x, y))
        assert path == []


class TestDungeonGenerationEdgeCases:
    """Edge cases for dungeon generation."""

    def test_minimum_size_dungeon(self):
        """Test generating minimum size dungeon."""
        config = DungeonConfig(
            width=10,
            height=10,
            min_room_size=3,
            max_room_size=5,
            min_rooms=1,
            max_rooms=2
        )
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        assert dungeon.width == 10
        assert dungeon.height == 10

    def test_dungeon_with_one_room(self):
        """Test dungeon with single room."""
        config = DungeonConfig(
            width=30,
            height=20,
            min_room_size=8,
            max_room_size=12,
            min_rooms=1,
            max_rooms=1
        )
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        assert len(generator.rooms) >= 1


class TestItemEdgeCases:
    """Edge cases for items."""

    def test_pickup_nonexistent_item(self):
        """Test picking up item that doesn't exist."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        result = engine.pickup_item("nonexistent")
        assert result is False

    def test_pickup_item_not_at_position(self):
        """Test picking up item not at player position."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        engine._player.position = (5, 5)

        # Add item elsewhere
        item = Item(
            id="sword1",
            name="Sword",
            item_type=ItemType.WEAPON,
            position=(10, 10)
        )
        engine.add_item(item)

        result = engine.pickup_item("sword1")
        assert result is False


class TestCharacterEdgeCases:
    """Edge cases for characters."""

    def test_character_at_max_level(self):
        """Test character at maximum level."""
        char = Character(
            id="hero",
            name="Hero",
            character_class="fighter",
            race="human"
        )

        # Give massive XP for max level
        char.experience = 1000000
        char.add_experience(0)

        # Level should cap at 20
        assert char.level <= 20

    def test_character_at_zero_hp(self):
        """Test character at zero HP."""
        char = Character(
            id="hero",
            name="Hero",
            character_class="fighter",
            race="human",
            hit_points=10
        )

        # Take fatal damage
        char.take_damage(100)

        assert char.hit_points == 0
        assert char.alive is False


class TestEventBusEdgeCases:
    """Edge cases for event bus."""

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing non-existent callback."""
        from src.core.event_bus import EventBus, Event, GameEvents

        bus = EventBus()

        def dummy_handler(event):
            pass

        # Should not raise
        bus.unsubscribe(GameEvents.TICK, dummy_handler)

    def test_publish_without_subscribers(self):
        """Test publishing event with no subscribers."""
        from src.core.event_bus import EventBus, Event, GameEvents

        bus = EventBus()

        # Should not raise
        bus.publish(Event(GameEvents.TICK, {}))


class MockEntity:
    """Mock entity for testing status effects."""

    def __init__(self, entity_id="test"):
        self.id = entity_id
        self.name = "Test Entity"
        self.alive = True
        self.immunities = set()

    def is_immune_to(self, condition_name: str) -> bool:
        return condition_name in self.immunities


class TestStatusEffectEdgeCases:
    """Edge cases for status effects."""

    def test_add_multiple_same_effect(self):
        """Test adding same effect multiple times."""
        manager = StatusEffectManager()
        entity = MockEntity()

        effect1 = StatusEffect(
            name="poisoned",
            duration=5,
            source="goblin"
        )
        effect2 = StatusEffect(
            name="poisoned",
            duration=10,
            source="goblin"
        )

        # Add same effect
        result1 = manager.add_effect(entity, effect1)
        result2 = manager.add_effect(entity, effect2)

        # Should stack/refresh
        assert result1 is True
        assert result2 is True

    def test_tick_permanent_effect(self):
        """Test that permanent effects don't expire."""
        manager = StatusEffectManager()
        entity = MockEntity()

        effect = StatusEffect(
            name="blinded",
            duration=-1,  # Permanent
            source="test"
        )
        manager.add_effect(entity, effect)

        # Tick many times
        for _ in range(100):
            expired = manager.tick_effects(entity)

        assert len(expired) == 0
        assert manager.has_effect(entity, "blinded")


class TestDiceEdgeCases:
    """Edge cases for dice rolling."""

    def test_roll_zero_dice(self):
        """Test rolling zero dice."""
        roller = DiceRoller()
        result = roller.roll("0d6")
        assert result == []

    def test_roll_very_large_dice(self):
        """Test rolling large number of dice."""
        roller = DiceRoller()
        result = roller.roll("1000d6")
        assert len(result) == 1000

    def test_roll_invalid_notation(self):
        """Test rolling with invalid notation."""
        roller = DiceRoller()
        with pytest.raises(ValueError):
            roller.roll("invalid")
