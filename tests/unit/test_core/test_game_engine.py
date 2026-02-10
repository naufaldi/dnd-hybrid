"""Tests for the game engine."""

import pytest
from src.core.game_engine import GameEngine, GameState
from src.entities.character import Character
from src.entities.enemy import Enemy, EnemyType
from src.entities.item import Item, ItemType
from src.world.map import GameMap, Room


class TestGameEngine:
    """Test suite for GameEngine."""

    def test_initial_state(self):
        """Test engine starts in MENU state."""
        engine = GameEngine()
        assert engine.state == GameState.MENU

    def test_player_creation(self):
        """Test player can be created."""
        engine = GameEngine()
        engine.create_player("TestHero", "fighter", "human")
        assert engine.player is not None
        assert engine.player.name == "TestHero"
        assert engine.player.character_class == "fighter"
        assert engine.player.race == "human"

    def test_player_movement(self):
        """Test player movement on map."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        # Set explicit position in middle of map
        engine.player.position = (5, 5)
        result = engine.move_player("north")
        assert result is True
        assert engine.player.position == (5, 4)

    def test_player_movement_blocked(self):
        """Test player cannot move through walls."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        # Position player at edge
        engine.player.position = (5, 0)
        result = engine.move_player("north")
        assert result is False

    def test_enemy_spawn(self):
        """Test enemies can be spawned."""
        engine = GameEngine()
        enemy = Enemy(id="goblin", name="Goblin", position=(10, 10))
        engine.add_enemy(enemy)
        assert len(engine.enemies) == 1
        assert engine.enemies[0].name == "Goblin"

    def test_enemy_removal(self):
        """Test enemies can be removed."""
        engine = GameEngine()
        enemy = Enemy(id="goblin", name="Goblin", position=(10, 10))
        engine.add_enemy(enemy)
        assert len(engine.enemies) == 1
        engine.remove_enemy("goblin")
        assert len(engine.enemies) == 0

    def test_turn_counter(self):
        """Test turn counter increments."""
        engine = GameEngine()
        initial_turns = engine.turn_count
        engine.next_turn()
        assert engine.turn_count == initial_turns + 1

    def test_combat_start_end(self):
        """Test combat state transitions."""
        engine = GameEngine()
        engine.start_combat()
        assert engine.state == GameState.COMBAT
        engine.end_combat()
        assert engine.state == GameState.PLAYING

    def test_player_turn(self):
        """Test player turn processing."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        engine.start()  # Start the game to enable player actions
        # Set explicit position
        engine.player.position = (5, 5)
        initial_turns = engine.turn_count
        result = engine.player_turn({"action": "move", "direction": "north"})
        assert result is True
        assert engine.turn_count == initial_turns + 1

    def test_enemy_turns(self):
        """Test enemy turn processing."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        engine.player.position = (5, 5)
        # Place enemy away from player but in aggro range
        enemy = Enemy(id="goblin", name="Goblin", position=(10, 5), aggro_range=10)
        engine.add_enemy(enemy)
        initial_enemy_pos = enemy.position
        engine.enemy_turns()
        # Enemy should move toward player (from 10,5 to closer x position)
        assert enemy.position != initial_enemy_pos

    def test_get_entities_at_position(self):
        """Test getting entities at a position."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        engine.player.position = (5, 5)
        enemy = Enemy(id="goblin", name="Goblin", position=(5, 5))
        engine.add_enemy(enemy)
        item = Item(id="sword", name="Sword", position=(5, 5))
        engine.add_item(item)
        entities = engine.get_entities_at(5, 5)
        assert len(entities) == 3  # player, enemy, and item

    def test_get_state_for_serialization(self):
        """Test state serialization."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        state = engine.get_state()
        assert "state" in state
        assert "current_floor" in state
        assert "turn_count" in state
        assert state["state"] == "MENU"  # Not yet playing

    def test_set_state_from_dict(self):
        """Test loading state from dict."""
        engine = GameEngine()
        state_dict = {
            "state": "PLAYING",
            "current_floor": 3,
            "turn_count": 42,
        }
        engine.set_state(state_dict)
        assert engine.state == GameState.PLAYING
        assert engine.current_floor == 3
        assert engine.turn_count == 42

    def test_can_move_to(self):
        """Test movement validation."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        # By default map is all floors, so should be able to move
        assert engine.can_move_to(5, 5) is True

    def test_is_blocked(self):
        """Test blocking check."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        # Player should block their own position
        assert engine.is_blocked(*engine.player.position) is True
        # Enemy at position should block
        enemy = Enemy(id="goblin", name="Goblin", position=(10, 10))
        engine.add_enemy(enemy)
        assert engine.is_blocked(10, 10) is True

    def test_change_floor(self):
        """Test floor changing."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        engine.current_floor = 1
        engine.change_floor(2)
        assert engine.current_floor == 2

    def test_item_spawn(self):
        """Test items can be spawned."""
        engine = GameEngine()
        item = Item(id="potion", name="Health Potion", position=(3, 4))
        engine.add_item(item)
        assert len(engine.items) == 1
        assert engine.items[0].name == "Health Potion"

    def test_item_removal(self):
        """Test items can be removed."""
        engine = GameEngine()
        item = Item(id="potion", name="Health Potion", position=(3, 4))
        engine.add_item(item)
        assert len(engine.items) == 1
        engine.remove_item("potion")
        assert len(engine.items) == 0

    def test_resolve_attack(self):
        """Test attack resolution."""
        engine = GameEngine()
        engine.create_player("Hero", "fighter", "human")
        enemy = Enemy(id="goblin", name="Goblin", position=(5, 6))
        engine.add_enemy(enemy)
        result = engine.resolve_attack(engine.player, enemy)
        # Result should have hit/damage info
        assert hasattr(result, "hit")
        assert hasattr(result, "damage")
        assert hasattr(result, "critical")

    def test_start_and_stop_game(self):
        """Test game start/stop."""
        engine = GameEngine()
        engine.start()
        assert engine.state == GameState.PLAYING
        engine.stop()
        assert engine.state == GameState.GAMEOVER

    def test_pause_and_resume(self):
        """Test pause/resume."""
        engine = GameEngine()
        engine.start()
        engine.pause()
        assert engine.state == GameState.PAUSED
        engine.resume()
        assert engine.state == GameState.PLAYING

    def test_player_property_none_initially(self):
        """Test player is None before creation."""
        engine = GameEngine()
        assert engine.player is None

    def test_enemies_list_empty_initially(self):
        """Test enemies list is empty initially."""
        engine = GameEngine()
        assert engine.enemies == []

    def test_items_list_empty_initially(self):
        """Test items list is empty initially."""
        engine = GameEngine()
        assert engine.items == []
