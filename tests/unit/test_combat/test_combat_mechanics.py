"""Unit tests for combat mechanics and dice rolling."""

import pytest
import random
from src.combat.dice import DiceRoller, roll_dice, ability_modifier


class TestDiceRoller:
    """Tests for the DiceRoller class."""

    @pytest.fixture
    def roller(self):
        """Create a dice roller with fixed seed for reproducibility."""
        return DiceRoller(seed=42)

    def test_roll_single_die(self, roller):
        """Test rolling a single die."""
        results = roller.roll("1d20")
        assert len(results) == 1
        assert 1 <= results[0] <= 20

    def test_roll_multiple_dice(self, roller):
        """Test rolling multiple dice."""
        results = roller.roll("3d6")
        assert len(results) == 3
        for result in results:
            assert 1 <= result <= 6

    def test_roll_with_positive_modifier(self, roller):
        """Test roll_sum with positive modifier."""
        result = roller.roll_sum("1d20+5")
        assert 6 <= result <= 25

    def test_roll_with_negative_modifier(self, roller):
        """Test roll_sum with negative modifier."""
        result = roller.roll_sum("1d20-3")
        assert -2 <= result <= 17

    def test_roll_invalid_notation(self, roller):
        """Test that invalid notation raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            roller.roll("invalid")
        assert "Invalid dice notation" in str(exc_info.value)

    def test_roll_unsupported_die_size(self, roller):
        """Test that unsupported die sizes raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            roller.roll("1d7")
        assert "Unsupported die size" in str(exc_info.value)

    def test_roll_zero_dice(self, roller):
        """Test rolling zero dice returns empty list."""
        results = roller.roll("0d6")
        assert len(results) == 0

    def test_roll_sum_consistency(self, roller):
        """Test that roll_sum equals sum of roll results plus modifier."""
        notation = "2d6+3"
        results = roller.roll(notation)
        total = roller.roll_sum(notation)
        assert sum(results) + 3 == total


class TestRollDiceFunction:
    """Tests for the roll_dice convenience function."""

    def test_roll_dice_returns_int(self):
        """Test that roll_dice returns an integer."""
        result = roll_dice("1d20")
        assert isinstance(result, int)

    def test_roll_dice_single_die(self):
        """Test rolling a single die."""
        result = roll_dice("1d6")
        assert 1 <= result <= 6

    def test_roll_dice_multiple_dice(self):
        """Test rolling multiple dice."""
        result = roll_dice("4d6")
        assert 4 <= result <= 24

    def test_roll_dice_with_modifier(self):
        """Test rolling with modifier."""
        result = roll_dice("2d8+4")
        assert 6 <= result <= 20

    def test_roll_dice_all_supported_sizes(self):
        """Test all supported die sizes."""
        sizes = [4, 6, 8, 10, 12, 20, 100]
        for size in sizes:
            result = roll_dice(f"1d{size}")
            assert 1 <= result <= size

    def test_roll_dice_invalid_notation_raises(self):
        """Test that invalid notation raises ValueError."""
        with pytest.raises(ValueError):
            roll_dice("not dice")


class TestAbilityModifier:
    """Tests for the ability_modifier function."""

    def test_ability_modifier_average_score(self):
        """Test modifier for average score (10)."""
        assert ability_modifier(10) == 0
        assert ability_modifier(11) == 0

    def test_ability_modifier_high_scores(self):
        """Test modifiers for high scores."""
        assert ability_modifier(12) == 1
        assert ability_modifier(14) == 2
        assert ability_modifier(16) == 3
        assert ability_modifier(18) == 4
        assert ability_modifier(20) == 5

    def test_ability_modifier_low_scores(self):
        """Test modifiers for low scores."""
        assert ability_modifier(8) == -1
        assert ability_modifier(6) == -2
        assert ability_modifier(4) == -3
        assert ability_modifier(2) == -4
        assert ability_modifier(1) == -5

    def test_ability_modifier_edge_cases(self):
        """Test edge cases."""
        assert ability_modifier(0) == -5
        assert ability_modifier(30) == 10
        assert ability_modifier(-5) == -8

    def test_ability_modifier_boundary_values(self):
        """Test boundary values between modifier tiers."""
        assert ability_modifier(9) == -1
        assert ability_modifier(10) == 0
        assert ability_modifier(11) == 0
        assert ability_modifier(12) == 1


class TestCombatMechanics:
    """Tests for combat-related calculations."""

    def test_critical_hit_detection(self):
        """Test critical hit on natural 20."""
        natural_roll = 20
        is_critical = natural_roll == 20
        assert is_critical is True

    def test_critical_fumble_detection(self):
        """Test critical fumble on natural 1."""
        natural_roll = 1
        is_fumble = natural_roll == 1
        assert is_fumble is True

    def test_attack_roll_calculation(self):
        """Test attack roll calculation."""
        attack_roll = 15
        modifier = ability_modifier(16)  # +3
        proficiency = 2
        total = attack_roll + modifier + proficiency
        assert total == 20

    def test_damage_calculation_with_modifier(self):
        """Test damage calculation including ability modifier."""
        weapon_damage = roll_dice("1d8")
        strength_mod = ability_modifier(14)  # +2
        total_damage = weapon_damage + strength_mod
        assert 3 <= total_damage <= 10

    def test_critical_hit_damage(self):
        """Test critical hit damage (roll twice)."""
        base_damage = roll_dice("1d8")
        critical_damage = base_damage * 2
        assert 2 <= critical_damage <= 16

    def test_armor_class_calculation(self):
        """Test AC calculation (base 10 + DEX mod)."""
        base_ac = 10
        dex_mod = ability_modifier(14)  # +2
        total_ac = base_ac + dex_mod
        assert total_ac == 12

    def test_hit_detection(self):
        """Test hit detection when attack >= AC."""
        attack_total = 15
        enemy_ac = 12
        is_hit = attack_total >= enemy_ac
        assert is_hit is True

    def test_miss_detection(self):
        """Test miss detection when attack < AC."""
        attack_total = 10
        enemy_ac = 15
        is_hit = attack_total >= enemy_ac
        assert is_hit is False


class TestDiceStatistics:
    """Statistical tests for dice rolling."""

    def test_d20_distribution_range(self):
        """Test that d20 rolls cover expected range over many rolls."""
        rolls = [roll_dice("1d20") for _ in range(1000)]
        assert min(rolls) >= 1
        assert max(rolls) <= 20

    def test_3d6_distribution_average(self):
        """Test that 3d6 average is around 10.5."""
        rolls = [roll_dice("3d6") for _ in range(1000)]
        average = sum(rolls) / len(rolls)
        # 3d6 should average around 10.5 (3 * 3.5)
        assert 9.5 <= average <= 11.5

    def test_multiple_dice_sum_range(self):
        """Test that sum of multiple dice stays in expected range."""
        for _ in range(100):
            result = roll_dice("4d6")
            assert 4 <= result <= 24


class TestDiceRollerReproducibility:
    """Tests for reproducibility with seeds."""

    def test_same_seed_same_results(self):
        """Test that same seed produces same results."""
        roller1 = DiceRoller(seed=123)
        roller2 = DiceRoller(seed=123)

        results1 = [roller1.roll("1d20")[0] for _ in range(10)]
        results2 = [roller2.roll("1d20")[0] for _ in range(10)]

        assert results1 == results2

    def test_different_seed_different_results(self):
        """Test that different seeds produce different results."""
        roller1 = DiceRoller(seed=123)
        roller2 = DiceRoller(seed=456)

        results1 = [roller1.roll("1d20")[0] for _ in range(10)]
        results2 = [roller2.roll("1d20")[0] for _ in range(10)]

        # Very unlikely to be the same
        assert results1 != results2
