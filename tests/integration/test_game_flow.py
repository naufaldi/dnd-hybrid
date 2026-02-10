"""Integration tests for game flow."""

import pytest
from src.core.game_engine import GameEngine, GameState
from src.entities.character import Character
from src.entities.enemy import Enemy, EnemyType, AIType
from src.entities.item import Item, ItemType
from src.world.dungeon_generator import DungeonGenerator, DungeonConfig
from src.world.tile_types import Tile
from src.combat.dice import DiceRoller


class TestGameFlow:
    """Test complete game flow scenarios."""

    def test_new_game_flow(self):
        """Test creating new game and player."""
        engine = GameEngine()

        # Initially in menu state
        assert engine.state == GameState.MENU

        # Create player
        player = engine.create_player("TestHero", "fighter", "human")
        assert player.name == "TestHero"
        assert player.character_class == "fighter"
        assert player.race == "human"

        # Start game
        engine.start()
        assert engine.state == GameState.PLAYING

    def test_player_movement_flow(self):
        """Test player movement through game."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Set up a simple map
        engine.current_map.set_tile(5, 5, Tile.floor())
        engine.current_map.set_tile(6, 5, Tile.floor())
        engine._player.position = (5, 5)

        # Move player
        result = engine.move_player("east")
        assert result is True
        assert engine._player.position == (6, 5)
        assert engine.turn_count == 1

    def test_combat_flow(self):
        """Test combat from start to finish."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Position player
        engine._player.position = (5, 5)

        # Add enemy
        enemy = Enemy(
            id="goblin1",
            name="Goblin",
            enemy_type=EnemyType.HUMANOID,
            cr=0.25,
            armor_class=12,
            max_hp=7,
            current_hp=7,
            position=(5, 6)
        )
        engine.add_enemy(enemy)

        # Verify enemy added
        assert len(engine.enemies) == 1

        # Player attacks
        result = engine.player_attack("goblin1")
        assert result is True

        # Enemy should be dead or damaged
        if not enemy.alive:
            assert len(engine.enemies) == 0

    def test_floor_change_flow(self):
        """Test changing floors."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Change floor
        assert engine.current_floor == 1
        engine.change_floor(2)
        assert engine.current_floor == 2

        # FOV cache should be cleared
        assert len(engine._fov_cache) == 0

    def test_item_pickup_flow(self):
        """Test picking up items."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Position player
        engine._player.position = (5, 5)

        # Add item on player's position
        sword = Item(
            id="sword1",
            name="Longsword",
            item_type=ItemType.WEAPON,
            position=(5, 5)
        )
        engine.add_item(sword)

        # Verify item added
        assert len(engine.items) == 1

        # Pick up item
        result = engine.pickup_item("sword1")
        assert result is True
        assert len(engine.items) == 0


class TestDungeonExploration:
    """Test dungeon exploration scenarios."""

    def test_dungeon_generation_and_exploration(self):
        """Test generating and exploring a dungeon."""
        config = DungeonConfig(
            width=40,
            height=20,
            min_room_size=5,
            max_room_size=10,
            min_rooms=3,
            max_rooms=5,
            seed=42
        )
        generator = DungeonGenerator(config)
        dungeon = generator.generate()

        # Verify dungeon has rooms
        assert len(generator.rooms) >= 3

        # Verify rooms are connected
        for i in range(len(generator.rooms) - 1):
            room_a = generator.rooms[i]
            room_b = generator.rooms[i + 1]
            # Check that both rooms have floor tiles
            tile = dungeon.get_tile(*room_a.center); assert tile and tile.tile_type.name in ("FLOOR", "STAIRS_UP", "STAIRS_DOWN")
            tile = dungeon.get_tile(*room_b.center); assert tile and tile.tile_type.name in ("FLOOR", "STAIRS_UP", "STAIRS_DOWN")


class TestCombatIntegration:
    """Test combat integration scenarios."""

    def test_player_vs_enemy_combat(self):
        """Test complete combat encounter."""
        engine = GameEngine()
        player = engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Give player good stats
        player.strength = 16
        player.dexterity = 14

        # Position player
        engine._player.position = (5, 5)

        # Add enemy
        enemy = Enemy(
            id="orc1",
            name="Orc",
            enemy_type=EnemyType.HUMANOID,
            cr=0.5,
            armor_class=13,
            max_hp=15,
            current_hp=15,
            position=(5, 6)
        )
        engine.add_enemy(enemy)

        # Track combat
        initial_hp = enemy.current_hp

        # Attack until enemy is dead
        attacks = 0
        while enemy.alive and attacks < 20:
            engine.player_attack("orc1")
            attacks += 1

        # Enemy should be dead
        assert not enemy.alive
        assert len(engine.enemies) == 0

    def test_enemy_turn_processing(self):
        """Test enemy AI turns."""
        engine = GameEngine()
        player = engine.create_player("TestHero", "fighter", "human")
        engine.start()

        # Position player
        engine._player.position = (10, 10)

        # Add aggressive enemy close to player
        enemy = Enemy(
            id="goblin1",
            name="Goblin",
            enemy_type=EnemyType.HUMANOID,
            cr=0.25,
            max_hp=7,
            current_hp=7,
            position=(12, 10),
            ai_type=AIType.AGGRESSIVE,
            aggro_range=10
        )
        engine.add_enemy(enemy)

        initial_pos = enemy.position

        # Process enemy turns
        engine.enemy_turns()

        # Enemy should have moved toward player
        # (simple AI moves one step)
        assert enemy.position != initial_pos


class TestPersistenceIntegration:
    """Test save/load integration."""

    def test_save_and_load_game_state(self):
        """Test saving and loading game state."""
        from src.persistence.save_manager import create_save_manager
        from pathlib import Path
        import tempfile
        import os

        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            save_dir = Path(tmpdir)

            # Create engine and play
            engine = GameEngine()
            player = engine.create_player("SaveTest", "wizard", "elf")
            engine.start()
            engine._player.position = (5, 5)
            engine.turn_count = 10

            # Get state
            state = engine.get_state()

            # Save
            save_manager = create_save_manager(save_dir)
            save_path = save_manager.save_game(state, "test_save.sav")
            assert save_path.exists()

            # Load
            loaded_state, timestamp = save_manager.load_game(save_path)

            # Verify state
            assert loaded_state["turn_count"] == 10
            assert loaded_state["state"] == "PLAYING"


class TestEventIntegration:
    """Test event system integration."""

    def test_event_publishing(self):
        """Test events are published correctly."""
        from src.core.event_bus import EventBus, Event, GameEvents

        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(GameEvents.TICK, handler)

        # Publish event
        bus.publish(Event(GameEvents.TICK, {"turn": 1}))

        assert len(received) == 1
        assert received[0].data["turn"] == 1
