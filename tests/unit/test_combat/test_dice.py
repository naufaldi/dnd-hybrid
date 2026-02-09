"""Tests for dice.py - D&D dice mechanics."""
from src.combat.dice import DiceRoller


class TestDiceRoller:
    """Test suite for DiceRoller class."""

    def test_roll_d4_returns_1_to_4(self):
        """d4 should return values between 1 and 4."""
        results = [DiceRoller().roll("1d4")[0] for _ in range(100)]
        assert all(1 <= r <= 4 for r in results)

    def test_roll_d6_returns_1_to_6(self):
        """d6 should return values between 1 and 6."""
        results = [DiceRoller().roll("1d6")[0] for _ in range(100)]
        assert all(1 <= r <= 6 for r in results)

    def test_roll_d8_returns_1_to_8(self):
        """d8 should return values between 1 and 8."""
        results = [DiceRoller().roll("1d8")[0] for _ in range(100)]
        assert all(1 <= r <= 8 for r in results)

    def test_roll_d10_returns_1_to_10(self):
        """d10 should return values between 1 and 10."""
        results = [DiceRoller().roll("1d10")[0] for _ in range(100)]
        assert all(1 <= r <= 10 for r in results)

    def test_roll_d12_returns_1_to_12(self):
        """d12 should return values between 1 and 12."""
        results = [DiceRoller().roll("1d12")[0] for _ in range(100)]
        assert all(1 <= r <= 12 for r in results)

    def test_roll_d20_returns_1_to_20(self):
        """d20 should return values between 1 and 20."""
        results = [DiceRoller().roll("1d20")[0] for _ in range(100)]
        assert all(1 <= r <= 20 for r in results)

    def test_roll_d100_returns_1_to_100(self):
        """d100 should return values between 1 and 100."""
        results = [DiceRoller().roll("1d100")[0] for _ in range(100)]
        assert all(1 <= r <= 100 for r in results)

    def test_roll_multiple_dice(self):
        """Rolling multiple dice should return that many results."""
        result = DiceRoller().roll("4d6")
        assert len(result) == 4

    def test_roll_with_positive_modifier(self):
        """Positive modifier should add to the dice values."""
        result = DiceRoller().roll("2d6+3")
        assert len(result) == 2  # Returns individual dice
        dice_sum = sum(result) + 3
        assert 5 <= dice_sum <= 15  # Min 2+3=5, Max 12+3=15

    def test_roll_with_negative_modifier(self):
        """Negative modifier should subtract from dice values."""
        result = DiceRoller().roll("2d6-2")
        assert len(result) == 2  # Returns individual dice
        dice_sum = sum(result) - 2
        assert 0 <= dice_sum <= 10  # Min 2-2=0, Max 12-2=10

    def test_roll_with_seed_reproducibility(self):
        """Same seed should produce same results."""
        roller1 = DiceRoller(seed=42)
        roller2 = DiceRoller(seed=42)
        assert roller1.roll("1d20") == roller2.roll("1d20")

    def test_roll_single_die_no_modifier(self):
        """Single die without modifier should work."""
        result = DiceRoller().roll("1d20")
        assert len(result) == 1
        assert 1 <= result[0] <= 20


class TestDiceRollerEdgeCases:
    """Test edge cases for dice rolling."""

    def test_roll_zero_dice_returns_empty(self):
        """Rolling 0 dice should return empty list."""
        result = DiceRoller().roll("0d6")
        assert result == []

    def test_roll_large_number_of_dice(self):
        """Rolling many dice should work."""
        result = DiceRoller().roll("100d6")
        assert len(result) == 100
        assert all(1 <= r <= 6 for r in result)

    def test_roll_large_modifier(self):
        """Large modifier should work."""
        result = DiceRoller().roll("1d20+100")
        assert len(result) == 1
        assert 101 <= result[0] + 100 <= 120
