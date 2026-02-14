"""Base entity class."""

import uuid
from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum, auto


class EntityType(Enum):
    """Entity types."""
    PLAYER = auto()
    ENEMY = auto()
    ITEM = auto()
    FEATURE = auto()


@dataclass
class Entity:
    """Base entity class."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed"
    entity_type: EntityType = EntityType.PLAYER
    position: Tuple[int, int] = (0, 0)
    alive: bool = True

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def move_to(self, x: int, y: int) -> None:
        """Move entity to position."""
        self.position = (x, y)
