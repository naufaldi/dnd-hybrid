# src/world/pathfinding.py
"""A* pathfinding algorithm and utilities."""

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass(frozen=True)
class Node:
    """A node for A* pathfinding."""

    position: Tuple[int, int]
    g_cost: float  # Cost from start
    h_cost: float  # Heuristic cost to goal
    parent: Optional["Node"] = None

    @property
    def f_cost(self) -> float:
        """Total cost (g + h)."""
        return self.g_cost + self.h_cost

    def __lt__(self, other: "Node") -> bool:
        """Compare nodes by f_cost for priority queue."""
        return self.f_cost < other.f_cost


def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two points.

    Args:
        a: First position (x, y)
        b: Second position (x, y)

    Returns:
        Manhattan distance (|dx| + |dy|)
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def chebyshev_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Calculate Chebyshev distance between two points.

    This is the maximum of the absolute differences in each dimension,
    representing the minimum number of moves with diagonal movement.

    Args:
        a: First position (x, y)
        b: Second position (x, y)

    Returns:
        Chebyshev distance (max(|dx|, |dy|))
    """
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def a_star_path(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    passable: Callable[[int, int], bool],
) -> List[Tuple[int, int]]:
    """Find a path using A* algorithm.

    Implements A* pathfinding with 8-directional movement (including diagonals).
    Uses Manhattan distance as the heuristic.

    Args:
        start: Starting position (x, y)
        goal: Goal position (x, y)
        passable: Callable that takes (x, y) and returns True if passable.
                  Should return False for out-of-bounds positions.

    Returns:
        List of positions forming the path from start to goal.
        Returns empty list if no path exists.
        The path includes the goal but not the start position.
    """
    # Handle edge cases
    if start == goal:
        return []

    # Validate start position
    try:
        if not passable(start[0], start[1]):
            return []
    except (IndexError, ValueError):
        return []

    # Validate goal position
    try:
        if not passable(goal[0], goal[1]):
            return []
    except (IndexError, ValueError):
        return []

    # 8-directional movement (including diagonals)
    # Directions: N, NE, E, SE, S, SW, W, NW
    directions = [
        (0, -1),   # N
        (1, -1),   # NE
        (1, 0),    # E
        (1, 1),    # SE
        (0, 1),    # S
        (-1, 1),   # SW
        (-1, 0),   # W
        (-1, -1),  # NW
    ]

    # Diagonal movements cost sqrt(2), orthogonal cost 1
    # For simplicity, we use 1 for orthogonal, 1.5 for diagonal
    diagonal_cost = 1.5
    orthogonal_cost = 1

    # Priority queue: list of (f_cost, counter, node) to break ties
    # Using a simple list with manual priority queue implementation
    open_set: List[Node] = []

    # Create start node
    start_node = Node(
        position=start,
        g_cost=0,
        h_cost=manhattan_distance(start, goal),
    )
    open_set.append(start_node)

    # Track visited positions with their best g_cost
    closed_set: dict[Tuple[int, int], float] = {}

    while open_set:
        # Get node with lowest f_cost
        open_set.sort(key=lambda n: (n.f_cost, n.g_cost))
        current = open_set.pop(0)

        # Check if we reached the goal
        if current.position == goal:
            # Reconstruct path
            path = []
            node: Optional[Node] = current
            while node is not None:
                path.append(node.position)
                node = node.parent
            path.reverse()
            # Remove start position from path (caller will be at start)
            return path[1:] if len(path) > 1 else []

        # Skip if we've already found a better path to this position
        pos = current.position
        if pos in closed_set and closed_set[pos] <= current.g_cost:
            continue
        closed_set[pos] = current.g_cost

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy

            # Skip non-passable tiles (handle out of bounds gracefully)
            try:
                if not passable(nx, ny):
                    continue
            except (IndexError, ValueError):
                continue

            # Calculate movement cost (diagonal vs orthogonal)
            is_diagonal = dx != 0 and dy != 0
            move_cost = diagonal_cost if is_diagonal else orthogonal_cost

            # Calculate new costs
            new_g_cost = current.g_cost + move_cost
            new_h_cost = manhattan_distance((nx, ny), goal)

            # Skip if we've already found a better path to neighbor
            if (nx, ny) in closed_set and closed_set[(nx, ny)] <= new_g_cost:
                continue

            # Create neighbor node
            neighbor = Node(
                position=(nx, ny),
                g_cost=new_g_cost,
                h_cost=new_h_cost,
                parent=current,
            )

            open_set.append(neighbor)

    # No path found
    return []
