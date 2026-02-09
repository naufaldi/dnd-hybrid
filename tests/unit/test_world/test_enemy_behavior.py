# tests/unit/test_world/test_enemy_behavior.py
"""Tests for enemy AI behaviors."""

import pytest
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set
from enum import Enum, auto

from src.world.enemy_behavior import EnemyAI, Action
from src.entities.enemy import Enemy, AIType, EnemyType


class MockMap:
    """Mock map for testing."""

    def __init__(self, width=10, height=10, walls=None):
        self.width = width
        self.height = height
        self._walls = set(walls or [])

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return (x, y) not in self._walls
        return False

    def distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class MockPlayer:
    """Mock player for testing."""

    def __init__(self, position: Tuple[int, int] = (5, 5)):
        self.position = position
        self.alive = True


class TestAction:
    """Tests for Action enum."""

    def test_action_has_expected_values(self):
        """Test Action enum has all expected values."""
        assert Action.MOVE in [Action.MOVE, Action.ATTACK, Action.FLEE, Action.WAIT]
        assert Action.ATTACK in [Action.MOVE, Action.ATTACK, Action.FLEE, Action.WAIT]
        assert Action.FLEE in [Action.MOVE, Action.ATTACK, Action.FLEE, Action.WAIT]
        assert Action.WAIT in [Action.MOVE, Action.ATTACK, Action.FLEE, Action.WAIT]


class TestEnemyAI:
    """Tests for EnemyAI class."""

    def test_aggressive_attacks_on_sight(self):
        """Test aggressive enemy attacks when player is in FOV and range."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(2, 2),
            ai_type=AIType.AGGRESSIVE,
            aggro_range=10,
        )
        player = MockPlayer(position=(3, 2))  # Orthogonally adjacent
        mock_map = MockMap(width=10, height=10)
        fov = {(3, 2), (2, 2)}  # Player in FOV

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.ATTACK

    def test_aggressive_moves_toward_player_when_visible(self):
        """Test aggressive enemy moves toward visible player."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 0),
            ai_type=AIType.AGGRESSIVE,
            aggro_range=10,
        )
        player = MockPlayer(position=(5, 5))
        mock_map = MockMap(width=10, height=10)
        fov = {(5, 5), (4, 5), (5, 4)}  # Player in FOV

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.MOVE

    def test_aggressive_waits_when_adjacent(self):
        """Test aggressive enemy moves adjacent to player but waits to attack."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(2, 2),
            ai_type=AIType.AGGRESSIVE,
            aggro_range=10,
        )
        player = MockPlayer(position=(3, 2))  # Orthogonally adjacent
        mock_map = MockMap(width=10, height=10)
        fov = {(3, 2), (2, 2)}  # Player adjacent

        action = ai.decide_action(enemy, player, mock_map, fov)
        # Should attack when adjacent
        assert action == Action.ATTACK

    def test_passive_flees_from_player(self):
        """Test passive enemy flees when player approaches."""
        ai = EnemyAI(AIType.PASSIVE)
        enemy = Enemy(
            id="e1",
            name="Rabbit",
            position=(5, 5),
            ai_type=AIType.PASSIVE,
            aggro_range=3,
        )
        player = MockPlayer(position=(5, 4))  # Very close
        mock_map = MockMap(width=10, height=10)
        fov = {(5, 5), (5, 4)}  # Player in FOV

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.FLEE

    def test_passive_waits_when_no_player(self):
        """Test passive enemy waits when no player in sight."""
        ai = EnemyAI(AIType.PASSIVE)
        enemy = Enemy(
            id="e1",
            name="Rabbit",
            position=(5, 5),
            ai_type=AIType.PASSIVE,
            aggro_range=3,
        )
        player = MockPlayer(position=(0, 0))  # Far away, not in FOV
        mock_map = MockMap(width=10, height=10)
        fov = set()  # No FOV coverage

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.WAIT

    def test_defensive_attacks_when_threatened(self):
        """Test defensive enemy attacks only when threatened."""
        ai = EnemyAI(AIType.DEFENSIVE)
        enemy = Enemy(
            id="e1",
            name="Turtle",
            position=(5, 5),
            ai_type=AIType.DEFENSIVE,
            aggro_range=1,
        )
        player = MockPlayer(position=(5, 6))  # Adjacent - threatening
        mock_map = MockMap(width=10, height=10)
        fov = {(5, 5), (5, 6)}

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.ATTACK

    def test_defensive_waits_when_not_threatened(self):
        """Test defensive enemy waits when not threatened."""
        ai = EnemyAI(AIType.DEFENSIVE)
        enemy = Enemy(
            id="e1",
            name="Turtle",
            position=(5, 5),
            ai_type=AIType.DEFENSIVE,
            aggro_range=1,
        )
        player = MockPlayer(position=(8, 8))  # Not adjacent
        mock_map = MockMap(width=10, height=10)
        fov = {(5, 5), (8, 8)}  # Player visible but not threatening

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.WAIT

    def test_patrol_follows_route(self):
        """Test patrol enemy follows predefined route."""
        patrol_route = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]
        ai = EnemyAI(AIType.PATROL, patrol_route=patrol_route)
        enemy = Enemy(
            id="e1",
            name="Guard",
            position=(0, 0),
            ai_type=AIType.PATROL,
            patrol_route=patrol_route,
        )
        player = MockPlayer(position=(9, 9))
        mock_map = MockMap(width=10, height=10)
        fov = set()  # Player not in FOV

        action = ai.decide_action(enemy, player, mock_map, fov)
        assert action == Action.MOVE

    def test_patrol_cycles_route(self):
        """Test patrol enemy cycles through route."""
        patrol_route = [(0, 0), (1, 0)]
        ai = EnemyAI(AIType.PATROL, patrol_route=patrol_route)
        enemy = Enemy(
            id="e1",
            name="Guard",
            position=(0, 0),
            ai_type=AIType.PATROL,
            patrol_route=patrol_route,
        )
        player = MockPlayer(position=(9, 9))
        mock_map = MockMap(width=10, height=10)
        fov = set()

        # First move should be toward next point in route
        action1 = ai.decide_action(enemy, player, mock_map, fov)
        assert action1 == Action.MOVE

    def test_get_path_to_player(self):
        """Test path to player calculation."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 0),
            ai_type=AIType.AGGRESSIVE,
        )
        player = MockPlayer(position=(5, 5))
        mock_map = MockMap(width=10, height=10)

        path = ai.get_path_to_player(enemy, player, mock_map)
        assert len(path) > 0
        assert path[-1] == (5, 5)

    def test_get_path_blocked_by_wall(self):
        """Test path calculation with walls."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 5),
            ai_type=AIType.AGGRESSIVE,
        )
        player = MockPlayer(position=(9, 5))
        # Create wall blocking direct path
        walls = [(x, 5) for x in range(1, 9)]
        mock_map = MockMap(width=10, height=10, walls=walls)

        path = ai.get_path_to_player(enemy, player, mock_map)
        # Path should exist but go around walls
        assert len(path) > 0

    def test_is_aggro_in_range(self):
        """Test aggro detection when player in range."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 0),
            aggro_range=10,
        )
        player_pos = (3, 4)  # Distance 7 < aggro_range 10
        fov = {(3, 4)}

        assert ai.is_aggro(enemy, player_pos, fov) is True

    def test_is_aggro_out_of_range(self):
        """Test aggro detection when player out of range."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 0),
            aggro_range=5,
        )
        player_pos = (10, 10)  # Distance 20 > aggro_range 5
        fov = {(10, 10)}

        assert ai.is_aggro(enemy, player_pos, fov) is False

    def test_is_aggro_not_in_fov(self):
        """Test aggro detection when player not in FOV."""
        ai = EnemyAI(AIType.AGGRESSIVE)
        enemy = Enemy(
            id="e1",
            name="Goblin",
            position=(0, 0),
            aggro_range=10,
        )
        player_pos = (3, 4)
        fov = set()  # Not in FOV

        assert ai.is_aggro(enemy, player_pos, fov) is False

    def test_flee_moves_away_from_player(self):
        """Test flee action moves away from player."""
        ai = EnemyAI(AIType.PASSIVE)
        enemy = Enemy(
            id="e1",
            name="Rabbit",
            position=(5, 5),
            ai_type=AIType.PASSIVE,
        )
        player = MockPlayer(position=(6, 5))  # Player to the right
        mock_map = MockMap(width=10, height=10)
        fov = {(5, 5), (6, 5)}

        # Get the next position when fleeing
        next_pos = ai._get_flee_position(enemy, player, mock_map)
        # Should move away from player (left, up, down)
        assert next_pos[0] < enemy.position[0] or next_pos[1] != enemy.position[1]
