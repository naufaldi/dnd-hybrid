"""Tests for choice system."""

import pytest
from src.narrative.choice_system import ChoiceSystem
from src.narrative.models import Choice, Consequence, GameState


class TestChoiceSystem:
    """Test choice selection and application."""

    @pytest.fixture
    def choice_system(self):
        return ChoiceSystem()

    @pytest.fixture
    def sample_choices(self):
        return [
            Choice(id="c1", text="First choice", shortcut="A", next_scene="scene1"),
            Choice(id="c2", text="Second choice", shortcut="B", next_scene="scene2"),
            Choice(id="c3", text="Third choice", shortcut="C", next_scene="scene3"),
        ]

    def test_select_by_index(self, choice_system, sample_choices):
        choice = choice_system.select_by_index(sample_choices, 1)
        assert choice.id == "c2"

    def test_select_by_index_out_of_bounds(self, choice_system, sample_choices):
        choice = choice_system.select_by_index(sample_choices, 10)
        assert choice is None

    def test_select_by_index_negative(self, choice_system, sample_choices):
        choice = choice_system.select_by_index(sample_choices, -1)
        assert choice is None

    def test_select_by_shortcut(self, choice_system, sample_choices):
        choice = choice_system.select_by_shortcut(sample_choices, "B")
        assert choice.id == "c2"

    def test_select_by_shortcut_case_insensitive(self, choice_system, sample_choices):
        choice = choice_system.select_by_shortcut(sample_choices, "b")
        assert choice.id == "c2"

    def test_select_by_shortcut_not_found(self, choice_system, sample_choices):
        choice = choice_system.select_by_shortcut(sample_choices, "X")
        assert choice is None

    def test_format_choices_display(self, choice_system, sample_choices):
        display = choice_system.format_choices_display(sample_choices, selected_index=1)
        assert "[A]" in display
        assert "[B]" in display
        assert "[C]" in display
        assert "▶" in display  # Selected indicator

    def test_format_choices_no_selection(self, choice_system, sample_choices):
        display = choice_system.format_choices_display(sample_choices)
        assert "[A]" in display
        # No ▶ when no selection
        assert display.count("▶") == 0

    def test_get_available_choices_all_available(self, choice_system, sample_choices):
        state = GameState(character=None, current_scene="test")
        available = choice_system.get_available_choices(sample_choices, state)
        assert len(available) == 3

    def test_get_available_choices_with_requirements(self, choice_system):
        choices = [
            Choice(id="c1", text="Choice 1", shortcut="A", next_scene="s1"),
            Choice(
                id="c2",
                text="Choice 2",
                shortcut="B",
                next_scene="s2",
                required_flags={"has_key": True},
            ),
        ]
        state = GameState(character=None, current_scene="test", flags={"has_key": True})
        available = choice_system.get_available_choices(choices, state)
        assert len(available) == 2

    def test_get_available_choices_filtered(self, choice_system):
        choices = [
            Choice(id="c1", text="Choice 1", shortcut="A", next_scene="s1"),
            Choice(
                id="c2",
                text="Choice 2",
                shortcut="B",
                next_scene="s2",
                required_flags={"has_key": True},
            ),
        ]
        state = GameState(character=None, current_scene="test", flags={})
        available = choice_system.get_available_choices(choices, state)
        assert len(available) == 1
        assert available[0].id == "c1"
