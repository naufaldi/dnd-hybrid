"""Initiative tracking and turn order management for combat."""
from typing import List, Optional

from .dice import DiceRoller


class InitiativeEntity:
    """Protocol for entities in initiative tracking."""

    position: tuple
    dexterity: int

    @property
    def dexterity_modifier(self) -> int:
        """Return the dexterity modifier."""
        ...


class InitiativeTracker:
    """Manages combat turn order and round tracking.

    Implements initiative-based turn ordering:
    - Entities roll d20 + dex modifier for initiative
    - Higher initiative goes first
    - Ties are broken by position hash
    - Tracks current turn, round number
    """

    def __init__(self, dice_roller: DiceRoller = None):
        """Initialize initiative tracker.

        Args:
            dice_roller: DiceRoller instance. Creates new one if None.
        """
        self.dice_roller = dice_roller or DiceRoller()
        self._order: List[InitiativeEntity] = []
        self._current_index: Optional[int] = None
        self._round_number: int = 0
        self._combat_active: bool = False

    @staticmethod
    def roll_initiative(entity: InitiativeEntity) -> int:
        """Roll initiative for an entity.

        Args:
            entity: The entity to roll initiative for

        Returns:
            Initiative value (d20 + dex modifier)
        """
        dex_mod = (entity.dexterity - 10) // 2
        roller = DiceRoller()
        roll = roller.roll("1d20")[0]
        return roll + dex_mod

    def start_combat(self, entities: List[InitiativeEntity]) -> None:
        """Initialize combat with a list of entities.

        Args:
            entities: List of entities participating in combat
        """
        if not entities:
            self._order = []
            return

        # Calculate initiative for each entity
        initiative_values = []
        for entity in entities:
            init_value = self.roll_initiative(entity)
            # Use position hash as tiebreaker
            tiebreaker = hash(entity.position)
            initiative_values.append((init_value, tiebreaker, entity))

        # Sort by initiative (descending), then by tiebreaker (ascending)
        initiative_values.sort(key=lambda x: (-x[0], x[1]))

        # Store ordered entities
        self._order = [item[2] for item in initiative_values]
        self._current_index = 0
        self._round_number = 1
        self._combat_active = True

    def next_turn(self) -> None:
        """Advance to the next turn in combat.

        Does nothing if combat is not active.
        """
        if not self._combat_active or not self._order:
            return

        self._current_index += 1

        # Check if we've gone through all combatants
        if self._current_index >= len(self._order):
            self._current_index = 0
            self._round_number += 1

    def end_combat(self) -> None:
        """End combat and clear all state."""
        self._order = []
        self._current_index = None
        self._round_number = 0
        self._combat_active = False

    def get_order(self) -> List[InitiativeEntity]:
        """Get the current initiative order.

        Returns:
            List of entities in initiative order
        """
        return self._order.copy()

    @property
    def current_turn(self) -> Optional[InitiativeEntity]:
        """Get the entity whose turn it currently is.

        Returns:
            Current entity or None if combat not active
        """
        if not self._combat_active or self._current_index is None:
            return None
        return self._order[self._current_index]

    @property
    def round_number(self) -> int:
        """Get the current round number.

        Returns:
            Round number (1-based, 0 if no active combat)
        """
        return self._round_number

    @property
    def combat_active(self) -> bool:
        """Check if combat is currently active.

        Returns:
            True if combat is active
        """
        return self._combat_active
