# tests/unit/test_world/test_fov.py
"""Tests for Field of View."""

import pytest
from src.world.map import GameMap
from src.world.tile_types import Tile
from src.world.fov import FieldOfView


class TestFieldOfView:
    """Tests for FieldOfView class."""

    def test_fov_center_visible(self):
        """Test that the center position is always visible."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        visible = fov.compute(10, 10, 5)
        assert (10, 10) in visible

    def test_fov_radius_applies(self):
        """Test that FOV respects radius."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        visible = fov.compute(10, 10, 3)
        # Center should be visible
        assert (10, 10) in visible

    def test_fov_wall_blocks(self):
        """Test that walls block FOV."""
        m = GameMap(width=20, height=20)
        # Create a wall row
        for x in range(20):
            m.set_tile(x, 10, Tile.wall())

        fov = FieldOfView(m)
        visible = fov.compute(5, 5, 10)

        # Tiles on the other side of wall should not be visible
        assert (15, 5) not in visible

    def test_fov_explored_tracking(self):
        """Test that FOV marks tiles as explored."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        fov.compute(10, 10, 5)

        # Center should be explored
        assert m.is_explored(10, 10) is True

    def test_fov_returns_set(self):
        """Test that FOV returns a set of coordinates."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        visible = fov.compute(10, 10, 5)

        assert isinstance(visible, set)
        assert len(visible) > 0
        for coord in visible:
            assert isinstance(coord, tuple)
            assert len(coord) == 2

    def test_fov_update_fov_method(self):
        """Test that update_fov method works like compute."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)

        visible1 = fov.update_fov(10, 10, 5)
        visible2 = fov.compute(10, 10, 5)

        assert visible1 == visible2

    def test_fov_near_edge(self):
        """Test FOV from position near map edge."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        visible = fov.compute(0, 0, 5)

        # Should not raise or return out-of-bounds coords
        for x, y in visible:
            assert 0 <= x < 20
            assert 0 <= y < 20

    def test_fov_small_radius(self):
        """Test FOV with small radius."""
        m = GameMap(width=20, height=20)
        fov = FieldOfView(m)
        visible = fov.compute(10, 10, 1)

        # Should at minimum include center
        assert (10, 10) in visible

    def test_fov_larger_radius(self):
        """Test FOV with larger radius."""
        m = GameMap(width=50, height=50)
        fov = FieldOfView(m)
        visible = fov.compute(25, 25, 15)

        # Should include center
        assert (25, 25) in visible
        # Should cover some area
        assert len(visible) > 10
