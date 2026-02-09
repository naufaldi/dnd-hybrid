# src/world/enemy_behavior.py
"""Enemy AI behaviors and decision making."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Set, Tuple, Union

from src.entities.enemy import AIType, Enemy
from src.world.pathfinding import a_star_path, manhattan_distance


class Action(Enum):
    """Possible enemy actions."""

    MOVE = auto()
    ATTACK = auto()
    FLEE = auto()
    WAIT = auto()


@dataclass
class Decision:
    """Result of an AI decision."""

    action: Action
    target: Optional[Tuple[int, int]] = None
    message: str = ""


# Type for anything with a position attribute or a position tuple
PositionLike = Union[Tuple[int, int], object]


def _extract_position(pos: PositionLike) -> Tuple[int, int]:
    """Extract position tuple from either a tuple or an object with position attribute.

    Args:
        pos: Either a tuple (x, y) or an object with a .position attribute

    Returns:
        A tuple (x, y)
    """
    if isinstance(pos, tuple):
        return pos
    return pos.position


class EnemyAI:
    """Enemy AI behavior controller.

    Supports different behavior types:
    - PASSIVE: Never attacks, flees from combat
    - AGGRESSIVE: Always attacks player on sight
    - DEFENSIVE: Attacks only when threatened
    - PATROL: Follows predefined route
    """

    def __init__(
        self,
        ai_type: AIType = AIType.AGGRESSIVE,
        patrol_route: Optional[List[Tuple[int, int]]] = None,
    ):
        """Initialize EnemyAI.

        Args:
            ai_type: The type of AI behavior
            patrol_route: List of positions for PATROL behavior
        """
        self.ai_type = ai_type
        self.patrol_route = patrol_route or []
        self._patrol_index = 0

    def is_aggro(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        fov: Set[Tuple[int, int]],
    ) -> bool:
        """Check if enemy is aggro (should engage player).

        Args:
            enemy: The enemy entity
            player_position: Current player position
            fov: Set of visible positions (field of view)

        Returns:
            True if enemy should engage player
        """
        # Check if player is in FOV
        if player_position not in fov:
            return False

        # Check if player is within aggro range
        distance = manhattan_distance(enemy.position, player_position)
        return distance <= enemy.aggro_range

    def get_path_to_player(
        self,
        enemy: Enemy,
        player: PositionLike,
        map_data,
    ) -> List[Tuple[int, int]]:
        """Get path to player position.

        Args:
            enemy: The enemy entity
            player: Target position (player object or tuple)
            map_data: Map object with is_walkable method

        Returns:
            List of positions forming path to player
        """
        player_position = _extract_position(player)

        def passable(x: int, y: int) -> bool:
            return map_data.is_walkable(x, y)

        return a_star_path(enemy.position, player_position, passable)

    def _get_flee_position(
        self,
        enemy: Enemy,
        player: PositionLike,
        map_data,
    ) -> Tuple[int, int]:
        """Get position to flee to (away from player).

        Args:
            enemy: The enemy entity
            player: Player object or position tuple to flee from
            map_data: Map object with is_walkable method

        Returns:
            Best position to flee to
        """
        player_position = _extract_position(player)
        # Get all valid adjacent positions
        directions = [
            (0, -1),  # N
            (1, 0),   # E
            (0, 1),   # S
            (-1, 0),  # W
        ]

        current_pos = enemy.position
        best_pos = current_pos
        best_distance = -1  # We want to maximize distance

        for dx, dy in directions:
            nx, ny = current_pos[0] + dx, current_pos[1] + dy

            if map_data.is_walkable(nx, ny):
                dist = manhattan_distance((nx, ny), player_position)
                if dist > best_distance:
                    best_distance = dist
                    best_pos = (nx, ny)

        return best_pos

    def _get_patrol_target(
        self,
        enemy: Enemy,
        map_data,
    ) -> Optional[Tuple[int, int]]:
        """Get next target in patrol route.

        Args:
            enemy: The enemy entity
            map_data: Map object with is_walkable method

        Returns:
            Next target position or None if no route
        """
        if not self.patrol_route:
            return None

        # Get current target in patrol
        target = self.patrol_route[self._patrol_index]

        # If reached target, move to next
        if enemy.position == target:
            self._patrol_index = (self._patrol_index + 1) % len(self.patrol_route)
            target = self.patrol_route[self._patrol_index]

        return target

    def _get_adjacent_attack_position(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        map_data,
    ) -> bool:
        """Check if enemy is adjacent to player (can attack).

        Args:
            enemy: The enemy entity
            player_position: Player position
            map_data: Map object

        Returns:
            True if enemy can attack (adjacent to player)
        """
        distance = manhattan_distance(enemy.position, player_position)
        return distance == 1

    def decide_action(
        self,
        enemy: Enemy,
        player,
        map_data,
        fov: Set[Tuple[int, int]],
    ) -> Action:
        """Decide what action the enemy should take.

        Args:
            enemy: The enemy entity
            player: The player entity (must have position attribute)
            map_data: Map object with is_walkable method
            fov: Set of visible positions

        Returns:
            The chosen action
        """
        player_position = player.position

        # Handle different AI types
        if self.ai_type == AIType.PASSIVE:
            return self._decide_passive(enemy, player_position, map_data, fov)
        elif self.ai_type == AIType.AGGRESSIVE:
            return self._decide_aggressive(enemy, player_position, map_data, fov)
        elif self.ai_type == AIType.DEFENSIVE:
            return self._decide_defensive(enemy, player_position, map_data, fov)
        elif self.ai_type == AIType.PATROL:
            return self._decide_patrol(enemy, player_position, map_data, fov)

        return Action.WAIT

    def _decide_passive(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        map_data,
        fov: Set[Tuple[int, int]],
    ) -> Action:
        """Passive AI: Flees from player if too close, otherwise waits."""
        # Check if player is visible and close
        if player_position in fov:
            distance = manhattan_distance(enemy.position, player_position)
            if distance <= enemy.aggro_range:
                return Action.FLEE

        return Action.WAIT

    def _decide_aggressive(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        map_data,
        fov: Set[Tuple[int, int]],
    ) -> Action:
        """Aggressive AI: Always attacks if visible, otherwise chases."""
        # Check if player is visible
        if player_position in fov:
            # If adjacent, attack
            if self._get_adjacent_attack_position(enemy, player_position, map_data):
                return Action.ATTACK
            # Otherwise move toward player
            return Action.MOVE

        # Player not visible - could chase or wait
        # For now, wait (could be enhanced to remember last known position)
        return Action.WAIT

    def _decide_defensive(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        map_data,
        fov: Set[Tuple[int, int]],
    ) -> Action:
        """Defensive AI: Attacks only if threatened (adjacent), otherwise waits."""
        # Check if player is adjacent (threatening)
        if player_position in fov:
            if self._get_adjacent_attack_position(enemy, player_position, map_data):
                return Action.ATTACK

        return Action.WAIT

    def _decide_patrol(
        self,
        enemy: Enemy,
        player_position: Tuple[int, int],
        map_data,
        fov: Set[Tuple[int, int]],
    ) -> Action:
        """Patrol AI: Follows predefined route, ignores player unless attacked."""
        # If player is very close and visible, become aggressive temporarily
        if player_position in fov:
            distance = manhattan_distance(enemy.position, player_position)
            if distance <= 1:
                return Action.ATTACK

        # Otherwise follow patrol route
        target = self._get_patrol_target(enemy, map_data)
        if target and enemy.position != target:
            return Action.MOVE

        return Action.WAIT
