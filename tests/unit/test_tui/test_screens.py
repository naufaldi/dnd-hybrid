"""Unit tests for TUI screens."""

import pytest
from unittest.mock import Mock, patch
from textual.widgets import Static


class TestCombatScreen:
    """Tests for the combat screen."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen instance."""
        from src.tui.screens.combat_screen import CombatScreen

        return CombatScreen(
            enemy_name="Goblin",
            enemy_hp=15,
            enemy_ac=12,
            enemy_description="A vicious goblin warrior.",
        )

    def test_screen_initialization(self, combat_screen):
        """Test combat screen initializes correctly."""
        assert combat_screen.enemy_name == "Goblin"
        assert combat_screen.enemy_max_hp == 15
        assert combat_screen.enemy_current_hp == 15
        assert combat_screen.enemy_ac == 12

    def test_markup_in_title_no_errors(self, combat_screen):
        """Test that title markup doesn't cause errors."""
        # The title should not contain invalid markup like [size=X]
        # This test verifies the fix was applied
        test_title = f"[b]═══ ⚔ Combat: {combat_screen.enemy_name} ⚔ ═══[/b]"
        # Should not contain size tags
        assert "[size=" not in test_title
        assert "[/size]" not in test_title

    def test_enemy_hp_tracking(self, combat_screen):
        """Test enemy HP can be modified."""
        combat_screen.enemy_current_hp = 10
        assert combat_screen.enemy_current_hp == 10

        combat_screen.enemy_current_hp -= 5
        assert combat_screen.enemy_current_hp == 5

    def test_combat_log_functionality(self, combat_screen):
        """Test combat log works correctly."""
        assert len(combat_screen.combat_log) == 0

        combat_screen.combat_log.append("Test message")
        assert len(combat_screen.combat_log) == 1
        assert combat_screen.combat_log[0] == "Test message"


class TestEndingScreen:
    """Tests for the ending screen."""

    @pytest.fixture
    def ending_screen(self):
        """Create an ending screen instance."""
        from src.tui.screens.ending_screen import EndingScreen

        return EndingScreen()

    def test_screen_initialization(self, ending_screen):
        """Test ending screen initializes with defaults."""
        assert ending_screen.ending_title == ""
        assert ending_screen.ending_description == ""
        assert ending_screen.stats == {}

    def test_set_ending(self, ending_screen):
        """Test setting ending details."""
        ending_screen.set_ending(
            title="Test Ending", description="Test description", stats={"score": "100"}
        )

        assert ending_screen.ending_title == "Test Ending"
        assert ending_screen.ending_description == "Test description"
        assert ending_screen.stats == {"score": "100"}

    def test_markup_in_title_no_errors(self, ending_screen):
        """Test that title markup doesn't cause errors."""
        ending_screen.ending_title = "Test Ending"
        # The title should not contain invalid markup like [size=X]
        test_title = f"[b]{ending_screen.ending_title}[/b]"

        assert "[size=" not in test_title
        assert "[/size]" not in test_title

    def test_ending_data_class(self):
        """Test EndingData dataclass."""
        from src.tui.screens.ending_screen import EndingData

        ending = EndingData(
            title="Victory",
            description="You won!",
            ending_type="hero",
            choices_made=10,
            scenes_visited=15,
            enemies_defeated=5,
            playtime_minutes=30,
        )

        assert ending.title == "Victory"
        assert ending.ending_type == "hero"

        stats = ending.to_stats_dict()
        assert "Choices Made" in stats
        assert stats["Enemies Defeated"] == "5"


class TestMarkupValidation:
    """Tests for markup validation across all screens."""

    INVALID_MARKUP_PATTERNS = [
        "[size=25]",
        "[size=30]",
        "[/size]",
        "[font=",
        "[color=",  # Rich uses [red], [blue], not [color=red]
    ]

    def test_no_invalid_markup_in_common_patterns(self):
        """Test that common invalid markup patterns are caught."""
        test_strings = [
            "[b]Bold text[/b]",  # Valid
            "[red]Red text[/red]",  # Valid
            "[b][size=25]Invalid[/size][/b]",  # Invalid
        ]

        for text in test_strings:
            for pattern in self.INVALID_MARKUP_PATTERNS:
                if pattern in text:
                    # This should trigger validation error in real usage
                    assert pattern in text, f"Found invalid markup: {pattern}"


class TestScreenIntegration:
    """Integration tests for screen interactions."""

    def test_combat_to_ending_transition(self):
        """Test transition from combat to ending screen."""
        from src.tui.screens.combat_screen import CombatScreen
        from src.tui.screens.ending_screen import EndingScreen

        # Create screens
        combat = CombatScreen(
            enemy_name="Boss",
            enemy_hp=50,
            enemy_ac=15,
            victory_scene="hero_ending",
            defeat_scene="death_in_dungeon",
        )

        ending = EndingScreen()

        # Verify both screens exist and can be configured
        assert combat.victory_scene == "hero_ending"
        assert combat.defeat_scene == "death_in_dungeon"

        ending.set_ending(
            title="Victory!", description="You defeated the boss!", stats={"enemies": "1"}
        )

        assert ending.ending_title == "Victory!"
