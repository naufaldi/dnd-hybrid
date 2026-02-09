# tests/unit/test_world/test_pathfinding.py
"""Tests for A* pathfinding algorithm."""

import pytest
from src.world.pathfinding import a_star_path, manhattan_distance, chebyshev_distance


class TestHeuristics:
    """Tests for pathfinding heuristic functions."""

    def test_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        assert manhattan_distance((0, 0), (3, 4)) == 7
        assert manhattan_distance((0, 0), (0, 0)) == 0
        assert manhattan_distance((5, 5), (2, 2)) == 6

    def test_chebyshev_distance(self):
        """Test Chebyshev distance calculation."""
        assert chebyshev_distance((0, 0), (3, 4)) == 4
        assert chebyshev_distance((0, 0), (0, 0)) == 0
        assert chebyshev_distance((5, 5), (2, 2)) == 3


class TestAStar:
    """Tests for A* pathfinding algorithm."""

    def test_straight_line_horizontal_path(self):
        """Test simple horizontal path."""
        # Create a 10x10 grid of passable tiles
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (5, 0), passable)
        assert len(path) > 0
        # Path should be straight line
        assert all(y == 0 for x, y in path)

    def test_straight_line_vertical_path(self):
        """Test simple vertical path."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (0, 5), passable)
        assert len(path) > 0
        # Path should be straight line
        assert all(x == 0 for x, y in path)

    def test_diagonal_path(self):
        """Test diagonal movement is allowed."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (3, 3), passable)
        assert len(path) > 0
        # Should be able to move diagonally
        assert len(path) < 7  # Manhattan would be 6, diagonal should be ~4

    def test_path_not_through_walls(self):
        """Test path goes around walls."""
        map_data = [[True] * 10 for _ in range(10)]
        # Create horizontal wall blocking direct path (not including start/end)
        for x in range(1, 9):
            map_data[5][x] = False
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 5), (9, 5), passable)
        assert len(path) > 0
        # Path should not go through walls
        for x, y in path:
            assert map_data[y][x] is True

    def test_path_around_vertical_wall(self):
        """Test path goes around vertical wall."""
        map_data = [[True] * 10 for _ in range(10)]
        # Create vertical wall blocking direct path
        for y in range(5):
            map_data[y][5] = False
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((3, 0), (3, 9), passable)
        assert len(path) > 0
        # Path should not go through walls
        for x, y in path:
            assert map_data[y][x] is True

    def test_no_path_returns_empty(self):
        """Test returns empty list when no path exists."""
        # Create a completely walled map
        map_data = [[False] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (5, 5), passable)
        assert path == []

    def test_no_path_with_island(self):
        """Test returns empty when goal is surrounded by walls."""
        map_data = [[True] * 7 for _ in range(7)]
        # Create walls around center (3, 3)
        for i in range(7):
            map_data[3][i] = False  # Horizontal
            map_data[i][3] = False  # Vertical
        passable = lambda x, y: map_data[y][x]
        # Goal is at center (surrounded)
        path = a_star_path((0, 0), (3, 3), passable)
        assert path == []

    def test_start_equals_goal(self):
        """Test path when start equals goal."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((5, 5), (5, 5), passable)
        # Should return empty or single step path
        assert len(path) == 0

    def test_path_includes_goal(self):
        """Test path includes the goal position."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (2, 0), passable)
        assert len(path) > 0
        # The last position should be the goal
        assert path[-1] == (2, 0)

    def test_out_of_bounds_goal(self):
        """Test handling of out of bounds goal."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: 0 <= x < 10 and 0 <= y < 10 and map_data[y][x]
        path = a_star_path((0, 0), (15, 15), passable)
        assert path == []

    def test_out_of_bounds_start(self):
        """Test handling of out of bounds start."""
        map_data = [[True] * 10 for _ in range(10)]
        passable = lambda x, y: 0 <= x < 10 and 0 <= y < 10 and map_data[y][x]
        path = a_star_path((-1, 0), (5, 5), passable)
        assert path == []

    def test_path_with_obstacles(self):
        """Test path finding with multiple obstacles."""
        map_data = [[True] * 10 for _ in range(10)]
        # Add some scattered walls
        walls = [(2, 2), (2, 3), (2, 4), (5, 5), (5, 6), (7, 3)]
        for x, y in walls:
            map_data[y][x] = False
        passable = lambda x, y: map_data[y][x]
        path = a_star_path((0, 0), (9, 9), passable)
        assert len(path) > 0
        # Path should not go through walls
        for x, y in path:
            assert map_data[y][x] is True

    def test_complex_maze_path(self):
        """Test path through a maze-like structure."""
        # Create a simple maze that is solvable
        map_data = [
            [True, True, True, True, True, True, True],
            [False, False, False, False, False, False, True],
            [True, True, True, True, True, True, True],
            [True, False, False, False, False, False, False],
            [True, True, True, True, True, True, True],
        ]
        passable = lambda x, y: map_data[y][x]
        # Start on the left, need to go down and around
        path = a_star_path((0, 0), (6, 2), passable)
        assert len(path) > 0
        # Path should not go through walls
        for x, y in path:
            assert map_data[y][x] is True
        # Path should end at goal
        assert path[-1] == (6, 2)
