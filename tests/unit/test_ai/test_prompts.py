"""Tests for AI prompt templates."""

import pytest
from src.ai.prompts import (
    build_scene_enhancement_prompt,
    build_dialogue_prompt,
    build_outcome_prompt,
    build_choices_prompt,
    build_story_summary,
    build_scene_generation_prompt,
    build_ending_enhancement_prompt,
)


class TestSceneEnhancementPrompt:
    def test_build_scene_enhancement_prompt_includes_base_description(self):
        prompt = build_scene_enhancement_prompt("A dark cave awaits.", {"player_class": "fighter", "act": 1})
        assert "A dark cave awaits" in prompt
        assert "fighter" in prompt
        assert "1" in prompt

    def test_build_scene_enhancement_prompt_handles_missing_context(self):
        prompt = build_scene_enhancement_prompt("Base text.", {})
        assert "Base text" in prompt
        assert "unknown" in prompt or "1" in prompt


class TestDialoguePrompt:
    def test_build_dialogue_prompt_includes_npc_and_mood(self):
        prompt = build_dialogue_prompt("Stranger", "enigmatic", "Player approaches.")
        assert "Stranger" in prompt
        assert "enigmatic" in prompt
        assert "Player approaches" in prompt

    def test_build_dialogue_prompt_includes_dialogue_type(self):
        prompt = build_dialogue_prompt("Guard", "hostile", "Context", dialogue_type="greeting")
        assert "greeting" in prompt


class TestOutcomePrompt:
    def test_build_outcome_prompt_includes_action_and_result(self):
        prompt = build_outcome_prompt("Persuasion", 15, 12, success=True)
        assert "Persuasion" in prompt
        assert "15" in prompt
        assert "12" in prompt
        assert "SUCCESS" in prompt

    def test_build_outcome_prompt_includes_failure(self):
        prompt = build_outcome_prompt("Stealth", 5, 10, success=False)
        assert "FAILURE" in prompt


class TestChoicesPrompt:
    def test_build_choices_prompt_includes_scene_and_character(self):
        prompt = build_choices_prompt(
            scene_context="A tavern",
            character_info={"name": "Hero", "race": "human", "class": "fighter"},
            story_flags={"met_stranger": True},
            num_choices=2,
        )
        assert "A tavern" in prompt
        assert "Hero" in prompt or "fighter" in prompt
        assert "2" in prompt


class TestStorySummary:
    def test_build_story_summary_with_history(self):
        summary = build_story_summary(
            {
                "scene_history": ["tavern", "dungeon", "goblins"],
                "choices_made": ["fought", "took_left"],
                "flags": {"met_stranger": True},
            }
        )
        assert "tavern" in summary or "dungeon" in summary
        assert "fought" in summary or "took_left" in summary

    def test_build_story_summary_empty(self):
        summary = build_story_summary({})
        assert "Beginning" in summary or summary


class TestSceneGenerationPrompt:
    def test_build_scene_generation_prompt_includes_context(self):
        prompt = build_scene_generation_prompt(
            "test_scene",
            {
                "char_info": "Player: Hero the human fighter",
                "story_summary": "Path: tavern -> dungeon",
            },
        )
        assert "test_scene" in prompt
        assert "Hero" in prompt or "fighter" in prompt


class TestEndingEnhancementPrompt:
    def test_build_ending_enhancement_prompt_includes_context(self):
        prompt = build_ending_enhancement_prompt(
            "You emerge victorious.",
            {"flags": {"defeated_cultist": True}, "choices_made": ["heroic"]},
        )
        assert "You emerge victorious" in prompt
        assert "defeated_cultist" in prompt or "heroic" in prompt
