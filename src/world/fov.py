# src/world/fov.py
"""Field of View using Shadow Casting."""

from typing import Set, Tuple
from .map import GameMap


class FieldOfView:
    """Field of View calculator using Shadow Casting algorithm."""

    def __init__(self, game_map: GameMap):
        self.game_map = game_map

    def compute(self, x: int, y: int, radius: int) -> Set[Tuple[int, int]]:
        """Compute visible tiles from position with given radius."""
        visible = {(x, y)}
        self.game_map.mark_explored(x, y)

        # Cast light in all 8 octants
        for octant in range(8):
            visible |= self._cast_light(x, y, radius, 1, 1.0, 0.0, octant)

        return visible

    def _cast_light(self, cx: int, cy: int, radius: int, row: int,
                    start: float, end: float, octant: int) -> Set[Tuple[int, int]]:
        """Recursively cast light in an octant."""
        visible = set()

        if start < end:
            return visible

        radius_sq = radius * radius

        for j in range(row, radius + 1):
            dx = -j - 1
            dy = -j
            blocked = False
            tan_angle_start = start

            while dx <= 0:
                dx += 1
                X, Y = self._transform(dx, dy, octant, cx, cy)
                if X < 0 or X >= self.game_map.width or Y < 0 or Y >= self.game_map.height:
                    break

                l_slope = (dx - 0.5) / (dy + 0.5)
                r_slope = (dx + 0.5) / (dy - 0.5)

                if start < r_slope:
                    continue
                if end > l_slope:
                    break

                dist_sq = dx * dx + dy * dy
                if dist_sq <= radius_sq:
                    visible.add((X, Y))
                    self.game_map.mark_explored(X, Y)

                if blocked:
                    if l_slope < end:
                        break
                    continue

                if self.game_map.is_opaque(X, Y):
                    blocked = True
                    tan_angle_start = l_slope

            if blocked:
                break

        return visible

    def _transform(self, dx: int, dy: int, octant: int, cx: int, cy: int) -> Tuple[int, int]:
        """Transform coordinates based on octant."""
        # Octant mapping
        transformations = [
            (lambda dx, dy: (cx + dx, cy - dy)),  # N
            (lambda dx, dy: (cx + dy, cy + dx)),  # E
            (lambda dx, dy: (cx - dx, cy + dy)),  # S
            (lambda dx, dy: (cx - dy, cy - dx)),  # W
            (lambda dx, dy: (cx - dx, cy - dy)),  # NW
            (lambda dx, dy: (cx - dy, cy + dx)),  # SW
            (lambda dx, dy: (cx + dx, cy + dy)),  # SE
            (lambda dx, dy: (cx + dy, cy - dx)),  # NE
        ]
        return transformations[octant](dx, dy)

    def update_fov(self, x: int, y: int, radius: int) -> Set[Tuple[int, int]]:
        """Compute FOV and return newly visible tiles."""
        return self.compute(x, y, radius)
