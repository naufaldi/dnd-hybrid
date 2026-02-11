"""Tests for ASCII dice display."""

import pytest
from src.combat.dice_display import DiceDisplay
from src.narrative.models import DiceRollResult


class TestDiceDisplay:
    """Test ASCII dice visualization."""

    def test_display_d20_critical(self):
        result = DiceRollResult(
            dice_type="d20", rolls=[20], modifier=5, total=25, natural=20, is_critical=True
        )
        display = DiceDisplay.display_d20(result)
        assert "20" in display
        assert "CRITICAL" in display.upper()

    def test_display_d20_fumble(self):
        result = DiceRollResult(
            dice_type="d20", rolls=[1], modifier=3, total=4, natural=1, is_fumble=True
        )
        display = DiceDisplay.display_d20(result)
        assert "1" in display

    def test_display_d20_normal_hit(self):
        result = DiceRollResult(
            dice_type="d20",
            rolls=[15],
            modifier=3,
            total=18,
            natural=15,
            is_critical=False,
            is_fumble=False,
        )
        display = DiceDisplay.display_d20(result)
        assert "15" in display
        assert "18" in display

    def test_display_damage(self):
        display = DiceDisplay.display_damage("2d6+3", [4, 2], 9)
        assert "2d6+3" in display
        assert "9" in display
        assert "4" in display
        assert "2" in display

    def test_display_skill_check_success(self):
        result = DiceRollResult(dice_type="d20", rolls=[17], modifier=3, total=20, natural=17)
        display = DiceDisplay.display_skill_check("Perception", result, 15, True)
        assert "SUCCESS" in display.upper() or "✓" in display
        assert "PERCEPTION" in display.upper()

    def test_display_skill_check_failure(self):
        result = DiceRollResult(dice_type="d20", rolls=[8], modifier=2, total=10, natural=8)
        display = DiceDisplay.display_skill_check("Athletics", result, 15, False)
        assert "FAIL" in display.upper() or "✗" in display

    def test_display_full_attack_hit(self):
        attack_result = DiceRollResult(
            dice_type="d20", rolls=[15], modifier=5, total=20, natural=15
        )
        damage_result = DiceRollResult(dice_type="d8", rolls=[6], modifier=3, total=9)
        display = DiceDisplay.display_full_attack(
            "You", "Goblin", attack_result, damage_result, True
        )
        assert "Goblin" in display
        assert "9" in display
        assert "HIT" in display

    def test_display_full_attack_miss(self):
        attack_result = DiceRollResult(
            dice_type="d20", rolls=[5], modifier=3, total=8, natural=5, is_fumble=False
        )
        display = DiceDisplay.display_full_attack("You", "Goblin", attack_result, None, False)
        assert "Goblin" in display
        # Total is 8, so display shows "MISS..." (not >= 10)
        assert "MISS" in display or "8" in display
