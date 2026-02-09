"""Status effects and conditions system for D&D Roguelike.

Provides StatusEffect dataclass, Condition enum, and StatusEffectManager
for applying, tracking, and removing status effects from entities.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


class Condition(Enum):
    """D&D 5e conditions as defined in the SRD.

    Each condition defines a state that modifies an entity's capabilities.
    """

    # Core conditions
    BLINDED = auto()
    CHARMED = auto()
    DEAFENED = auto()
    FRIGHTENED = auto()
    GRAPPLED = auto()
    INCAPACITATED = auto()
    INVISIBLE = auto()
    PARALYZED = auto()
    PETRIFIED = auto()
    POISONED = auto()
    PRONE = auto()
    RESTRAINED = auto()
    STUNNED = auto()
    UNCONSCIOUS = auto()

    # Exhaustion (generic) and levels (1-6)
    EXHAUSTION = auto()
    EXHAUSTION_1 = auto()
    EXHAUSTION_2 = auto()
    EXHAUSTION_3 = auto()
    EXHAUSTION_4 = auto()
    EXHAUSTION_5 = auto()
    EXHAUSTION_6 = auto()


# Map condition names to their Condition enum values
CONDITION_MAP: Dict[str, Condition] = {
    "blinded": Condition.BLINDED,
    "charmed": Condition.CHARMED,
    "deafened": Condition.DEAFENED,
    "frightened": Condition.FRIGHTENED,
    "grappled": Condition.GRAPPLED,
    "incapacitated": Condition.INCAPACITATED,
    "invisible": Condition.INVISIBLE,
    "paralyzed": Condition.PARALYZED,
    "petrified": Condition.PETRIFIED,
    "poisoned": Condition.POISONED,
    "prone": Condition.PRONE,
    "restrained": Condition.RESTRAINED,
    "stunned": Condition.STUNNED,
    "unconscious": Condition.UNCONSCIOUS,
    "exhaustion": Condition.EXHAUSTION,
    "exhaustion_1": Condition.EXHAUSTION_1,
    "exhaustion_2": Condition.EXHAUSTION_2,
    "exhaustion_3": Condition.EXHAUSTION_3,
    "exhaustion_4": Condition.EXHAUSTION_4,
    "exhaustion_5": Condition.EXHAUSTION_5,
    "exhaustion_6": Condition.EXHAUSTION_6,
}


@dataclass
class StatusEffect:
    """Represents a status effect applied to an entity.

    Attributes:
        name: The name/identifier of the effect (e.g., "poisoned", "stunned").
        duration: Number of turns remaining. -1 indicates permanent.
        source: What caused the effect (e.g., "goblin", "spell", "acid").
        metadata: Additional data for the effect (e.g., damage amount, type).
    """

    name: str
    duration: int
    source: str
    metadata: Dict = field(default_factory=dict)

    @property
    def is_permanent(self) -> bool:
        """Check if this effect is permanent (duration = -1)."""
        return self.duration == -1


class EntityLike:
    """Interface for entities that can have status effects applied.

    Entities must implement this interface to work with StatusEffectManager.
    """

    id: str
    name: str
    alive: bool
    immunities: set

    def is_immune_to(self, condition_name: str) -> bool:
        """Check if the entity is immune to a condition."""
        return condition_name in self.immunities


class StatusEffectManager:
    """Manages status effects for all entities in the game.

    Tracks active effects, handles duration countdown, and manages
    effect stacking and expiration.
    """

    def __init__(self):
        """Initialize the status effect manager."""
        # Maps entity id -> list of active status effects
        self._effects: Dict[str, List[StatusEffect]] = {}

    def add_effect(self, entity: EntityLike, effect: StatusEffect) -> bool:
        """Apply a status effect to an entity.

        Args:
            entity: The entity to apply the effect to.
            effect: The status effect to apply.

        Returns:
            True if the effect was applied, False if entity is immune.
        """
        # Check immunity
        if entity.is_immune_to(effect.name):
            return False

        entity_id = entity.id

        # Initialize effects list if needed
        if entity_id not in self._effects:
            self._effects[entity_id] = []

        # Check for existing effect of same type (stacking = refresh duration)
        existing_index = self._find_effect_index(entity_id, effect.name)
        if existing_index is not None:
            # Refresh duration
            self._effects[entity_id][existing_index].duration = effect.duration
        else:
            # Add new effect
            self._effects[entity_id].append(effect)

        return True

    def remove_effect(self, entity: EntityLike, effect_name: str) -> bool:
        """Remove a status effect from an entity.

        Args:
            entity: The entity to remove the effect from.
            effect_name: The name of the effect to remove.

        Returns:
            True if the effect was removed, False if it wasn't active.
        """
        entity_id = entity.id

        if entity_id not in self._effects:
            return False

        index = self._find_effect_index(entity_id, effect_name)
        if index is not None:
            del self._effects[entity_id][index]
            return True

        return False

    def has_effect(self, entity: EntityLike, effect_name: str) -> bool:
        """Check if an entity has a specific effect active.

        Args:
            entity: The entity to check.
            effect_name: The name of the effect to check for.

        Returns:
            True if the effect is active, False otherwise.
        """
        entity_id = entity.id

        if entity_id not in self._effects:
            return False

        return self._find_effect_index(entity_id, effect_name) is not None

    def has_condition(self, entity: EntityLike, condition: Condition) -> bool:
        """Check if an entity has a specific condition.

        Args:
            entity: The entity to check.
            condition: The Condition enum value to check for.

        Returns:
            True if the condition is active, False otherwise.
        """
        # Convert condition enum to name string for lookup
        condition_name = condition.name.lower()

        # Handle exhaustion levels (exhaustion_1 -> "exhaustion_1")
        if condition_name.startswith("exhaustion_"):
            return self.has_effect(entity, condition_name)

        # Map condition name to effect name
        effect_name = condition_name

        return self.has_effect(entity, effect_name)

    def tick_effects(self, entity: EntityLike) -> List[StatusEffect]:
        """Tick down duration of all effects on an entity.

        Decrements duration of all non-permanent effects by 1.
        Returns a list of effects that have expired.

        Args:
            entity: The entity whose effects should be ticked.

        Returns:
            List of StatusEffect objects that have expired.
        """
        entity_id = entity.id
        expired: List[StatusEffect] = []

        if entity_id not in self._effects:
            return expired

        # Iterate backwards to safely remove expired effects
        for i in range(len(self._effects[entity_id]) - 1, -1, -1):
            effect = self._effects[entity_id][i]

            if effect.is_permanent:
                continue

            effect.duration -= 1

            if effect.duration <= 0:
                expired.append(effect)
                del self._effects[entity_id][i]

        return expired

    def clear_expired(self, entity: EntityLike) -> None:
        """Remove all expired effects from an entity.

        This is typically called after tick_effects() to clean up
        any effects that reached duration 0.

        Args:
            entity: The entity to clear expired effects from.
        """
        entity_id = entity.id

        if entity_id not in self._effects:
            return

        # Keep only effects that are permanent or have positive duration
        self._effects[entity_id] = [
            e for e in self._effects[entity_id]
            if e.is_permanent or e.duration > 0
        ]

    def get_active_effects(self, entity: EntityLike) -> List[StatusEffect]:
        """Get all active effects on an entity.

        Args:
            entity: The entity to get effects for.

        Returns:
            List of active StatusEffect objects.
        """
        entity_id = entity.id

        if entity_id not in self._effects:
            return []

        return list(self._effects[entity_id])

    def _find_effect_index(self, entity_id: str, effect_name: str) -> Optional[int]:
        """Find the index of an effect by name for a given entity.

        Args:
            entity_id: The entity's unique identifier.
            effect_name: The name of the effect to find.

        Returns:
            The index of the effect, or None if not found.
        """
        if entity_id not in self._effects:
            return None

        for i, effect in enumerate(self._effects[entity_id]):
            if effect.name.lower() == effect_name.lower():
                return i

        return None

    def clear_all_effects(self, entity: EntityLike) -> None:
        """Clear all effects from an entity.

        Args:
            entity: The entity to clear all effects from.
        """
        entity_id = entity.id

        if entity_id in self._effects:
            self._effects[entity_id] = []

    def has_any_condition(self, entity: EntityLike, conditions: List[Condition]) -> bool:
        """Check if an entity has any of the specified conditions.

        Args:
            entity: The entity to check.
            conditions: List of Condition enum values to check for.

        Returns:
            True if the entity has any of the conditions.
        """
        for condition in conditions:
            if self.has_condition(entity, condition):
                return True
        return False
