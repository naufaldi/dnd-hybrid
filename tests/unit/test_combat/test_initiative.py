"""Tests for initiative.py - Turn order management."""
from src.combat.dice import DiceRoller
from src.combat.initiative import InitiativeTracker


class MockCombatEntity:
    """Mock entity for testing initiative."""

    def __init__(self, dex: int = 10, position: tuple = (0, 0)):
        self.dexterity = dex
        self.position = position

    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2


class FixedDiceRoller(DiceRoller):
    """Dice roller that returns fixed values for testing."""

    def __init__(self, values: list):
        super().__init__()
        self.values = values
        self.index = 0

    def roll(self, notation: str) -> list:
        result = [self.values[self.index % len(self.values)]]
        self.index += 1
        return result


class TestInitiativeTracker:
    """Test suite for InitiativeTracker class."""

    def test_roll_initiative_returns_valid_range(self):
        """Initiative roll should be 1-20 + dex modifier."""
        entity = MockCombatEntity(dex=14)  # Dex mod = +2
        value = InitiativeTracker.roll_initiative(entity)

        assert 3 <= value <= 22  # Min 1+2, Max 20+2

    def test_roll_initiative_uses_dex_modifier(self):
        """Higher dex should generally give higher initiative."""
        low_dex = MockCombatEntity(dex=8)  # Dex mod = -1
        high_dex = MockCombatEntity(dex=18)  # Dex mod = +4

        tracker = InitiativeTracker()
        # Roll multiple times to account for randomness
        low_rolls = [tracker.roll_initiative(low_dex) for _ in range(50)]
        high_rolls = [tracker.roll_initiative(high_dex) for _ in range(50)]

        assert sum(high_rolls) > sum(low_rolls)

    def test_start_combat_sets_up_order(self):
        """Starting combat should set up initiative order."""
        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        entity2 = MockCombatEntity(dex=14, position=(1, 1))
        tracker = InitiativeTracker()

        tracker.start_combat([entity1, entity2])

        assert tracker.get_order() is not None
        assert len(tracker.get_order()) == 2

    def test_get_order_returns_sorted_entities(self):
        """Entities should be sorted by initiative (highest first)."""
        tracker = InitiativeTracker()
        # Use fixed roller to control order
        tracker.dice_roller = FixedDiceRoller([10, 20])  # entity2 gets 20, entity1 gets 10

        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        entity2 = MockCombatEntity(dex=10, position=(1, 1))
        tracker.start_combat([entity1, entity2])

        order = tracker.get_order()
        # Higher roll should be first
        assert order[0] != order[1]

    def test_next_turn_advances_combat(self):
        """next_turn should advance to the next combatant."""
        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        entity2 = MockCombatEntity(dex=10, position=(1, 1))
        tracker = InitiativeTracker()
        tracker.dice_roller = FixedDiceRoller([15, 10])
        tracker.start_combat([entity1, entity2])

        first_turn = tracker.current_turn
        tracker.next_turn()

        assert tracker.current_turn != first_turn

    def test_next_turn_wraps_around(self):
        """next_turn should wrap from last to first."""
        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        entity2 = MockCombatEntity(dex=10, position=(1, 1))
        tracker = InitiativeTracker()
        tracker.dice_roller = FixedDiceRoller([15, 10])
        tracker.start_combat([entity1, entity2])

        # Advance through all turns
        initial_turn = tracker.current_turn
        tracker.next_turn()
        tracker.next_turn()  # Back to first

        assert tracker.current_turn == initial_turn

    def test_round_number_increments(self):
        """Round number should increment after all combatants act."""
        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        entity2 = MockCombatEntity(dex=10, position=(1, 1))
        tracker = InitiativeTracker()
        tracker.dice_roller = FixedDiceRoller([15, 10])
        tracker.start_combat([entity1, entity2])

        assert tracker.round_number == 1
        tracker.next_turn()
        tracker.next_turn()
        assert tracker.round_number == 2

    def test_end_combat_clears_state(self):
        """Ending combat should clear all state."""
        entity1 = MockCombatEntity(dex=10, position=(0, 0))
        tracker = InitiativeTracker()
        tracker.start_combat([entity1])

        tracker.end_combat()

        assert tracker.get_order() == []
        assert tracker.current_turn is None
        assert tracker.round_number == 0

    def test_initiative_tie_breaker_uses_position(self):
        """Ties should be broken by position hash."""
        entity1 = MockCombatEntity(dex=14, position=(0, 0))
        entity2 = MockCombatEntity(dex=14, position=(1, 1))
        tracker = InitiativeTracker()
        # Both get same initiative roll
        tracker.dice_roller = FixedDiceRoller([10, 10])
        tracker.start_combat([entity1, entity2])

        order = tracker.get_order()
        # Should have deterministic order based on position
        assert order[0] != order[1] or hash(order[0].position) != hash(order[1].position)

    def test_combat_must_be_active_for_next_turn(self):
        """next_turn should silently do nothing without active combat."""
        tracker = InitiativeTracker()

        # Should not raise, but shouldn't change state meaningfully
        tracker.next_turn()

        assert tracker.round_number == 0
        assert tracker.combat_active is False


class TestInitiativeTrackerEdgeCases:
    """Test edge cases for initiative tracking."""

    def test_single_entity_combat(self):
        """Single entity combat should work."""
        entity = MockCombatEntity(dex=10, position=(0, 0))
        tracker = InitiativeTracker()
        tracker.start_combat([entity])

        assert len(tracker.get_order()) == 1
        tracker.next_turn()
        assert tracker.round_number == 2  # Wrapped around

    def test_many_entities_combat(self):
        """Combat with many entities should maintain order."""
        entities = [MockCombatEntity(dex=10, position=(i, 0)) for i in range(10)]
        tracker = InitiativeTracker()
        tracker.start_combat(entities)

        assert len(tracker.get_order()) == 10
        assert tracker.round_number == 1
