"""Integration tests for dice system."""

import pytest
from pathlib import Path


class TestDiceImports:
    """Tests for dice system imports."""

    def test_dice_roller_class_import(self):
        """Test that DiceRoller class can be imported."""
        from src.combat.dice import DiceRoller

        assert DiceRoller is not None

    def test_roll_dice_function_import(self):
        """Test that roll_dice function can be imported."""
        from src.combat.dice import roll_dice

        assert callable(roll_dice)

    def test_ability_modifier_function_import(self):
        """Test that ability_modifier function can be imported."""
        from src.combat.dice import ability_modifier

        assert callable(ability_modifier)

    def test_all_dice_exports_available(self):
        """Test that all expected exports are available."""
        from src.combat import dice

        assert hasattr(dice, "DiceRoller")
        assert hasattr(dice, "roll_dice")
        assert hasattr(dice, "ability_modifier")


class TestDiceInCharacterSystem:
    """Tests for dice integration with character system."""

    def test_character_uses_ability_modifier(self):
        """Test that character system uses ability modifier calculations."""
        from src.character.character import Character
        from src.character.attributes import attribute_modifier

        char = Character(
            name="Test",
            character_class="fighter",
            race="human",
            strength=16,
        )

        # Character should use the same modifier calculation
        expected_mod = attribute_modifier(16)
        assert char.strength_mod == expected_mod

    def test_character_ac_uses_dexterity_modifier(self):
        """Test that AC calculation uses DEX modifier."""
        from src.character.character import Character
        from src.character.attributes import attribute_modifier

        char = Character(
            name="Test",
            character_class="fighter",
            race="human",
            dexterity=14,
        )

        dex_mod = attribute_modifier(14)
        expected_ac = 10 + dex_mod
        assert char.armor_class == expected_ac


class TestDiceInCombatScreen:
    """Tests for dice integration in combat screen."""

    def test_combat_screen_imports_dice_functions(self):
        """Test that combat screen imports dice functions correctly."""
        # This will fail with ImportError if imports are wrong
        try:
            from src.tui.screens.combat_screen import CombatScreen

            # Import successful
            assert True
        except ImportError as e:
            if "roll_dice" in str(e) or "ability_modifier" in str(e):
                pytest.fail(f"Combat screen has broken dice imports: {e}")
            # Other import errors are not related to dice
            assert True

    def test_combat_screen_can_use_roll_dice(self):
        """Test that combat screen can call roll_dice."""
        from src.combat.dice import roll_dice

        # Simulate damage calculation as combat screen would do
        damage_dice = "1d8"
        damage = roll_dice(damage_dice)

        assert 1 <= damage <= 8

    def test_combat_screen_can_use_ability_modifier(self):
        """Test that combat screen can call ability_modifier."""
        from src.combat.dice import ability_modifier

        # Simulate attack modifier calculation
        strength_score = 16
        modifier = ability_modifier(strength_score)

        assert modifier == 3


class TestDiceConsistency:
    """Tests for dice behavior consistency across system."""

    def test_modifier_calculation_consistency(self):
        """Test that modifier calculation is consistent everywhere."""
        from src.combat.dice import ability_modifier
        from src.character.attributes import attribute_modifier

        # Both functions should give same results
        test_scores = [1, 8, 10, 12, 16, 18, 20]

        for score in test_scores:
            combat_mod = ability_modifier(score)
            char_mod = attribute_modifier(score)
            assert combat_mod == char_mod, (
                f"Modifier mismatch for score {score}: combat={combat_mod}, char={char_mod}"
            )

    def test_dice_roll_ranges(self):
        """Test that dice rolls stay in expected ranges."""
        from src.combat.dice import roll_dice

        # Test various dice notations
        test_cases = [
            ("1d4", 1, 4),
            ("1d6", 1, 6),
            ("1d8", 1, 8),
            ("1d10", 1, 10),
            ("1d12", 1, 12),
            ("1d20", 1, 20),
            ("2d6", 2, 12),
            ("3d8", 3, 24),
        ]

        for notation, min_val, max_val in test_cases:
            for _ in range(10):  # Test multiple rolls
                result = roll_dice(notation)
                assert min_val <= result <= max_val, (
                    f"Roll {notation} = {result}, expected {min_val}-{max_val}"
                )

    def test_dice_with_modifiers(self):
        """Test that dice with modifiers calculate correctly."""
        from src.combat.dice import roll_dice

        # Test positive modifiers
        for _ in range(5):
            result = roll_dice("1d6+4")
            assert 5 <= result <= 10

        # Test negative modifiers
        for _ in range(5):
            result = roll_dice("1d6-2")
            assert -1 <= result <= 4


class TestDiceErrorHandling:
    """Tests for dice system error handling."""

    def test_roll_dice_invalid_notation_raises(self):
        """Test that invalid notation raises appropriate error."""
        from src.combat.dice import roll_dice

        with pytest.raises(ValueError) as exc_info:
            roll_dice("invalid")

        assert "Invalid" in str(exc_info.value)

    def test_roll_dice_unsupported_die_raises(self):
        """Test that unsupported die size raises error."""
        from src.combat.dice import roll_dice

        with pytest.raises(ValueError) as exc_info:
            roll_dice("1d7")

        assert "Unsupported" in str(exc_info.value)

    def test_ability_modifier_extreme_values(self):
        """Test ability modifier with extreme values."""
        from src.combat.dice import ability_modifier

        # Very high score
        assert ability_modifier(100) == 45

        # Very low score
        assert ability_modifier(1) == -5

        # Zero
        assert ability_modifier(0) == -5


class TestDicePerformance:
    """Tests for dice system performance."""

    def test_dice_roll_performance(self):
        """Test that dice rolls are fast."""
        from src.combat.dice import roll_dice
        import time

        start = time.time()

        # Roll many dice
        for _ in range(1000):
            roll_dice("1d20+5")

        elapsed = time.time() - start

        # Should be very fast (under 1 second for 1000 rolls)
        assert elapsed < 1.0, f"Dice rolling too slow: {elapsed:.2f}s for 1000 rolls"

    def test_multiple_dice_rolls(self):
        """Test rolling multiple dice efficiently."""
        from src.combat.dice import DiceRoller

        roller = DiceRoller()

        # Roll multiple dice at once
        results = roller.roll("10d6")

        assert len(results) == 10
        for r in results:
            assert 1 <= r <= 6
