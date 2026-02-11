"""Tests for narrative data models."""

import pytest
from dataclasses import asdict
from src.narrative.models import (
    Scene,
    Choice,
    Consequence,
    SkillCheck,
    GameState,
    DiceRollResult,
    Ending,
)


class TestSceneModel:
    """Test Scene data model."""

    def test_scene_creation(self):
        scene = Scene(
            id="test_scene",
            act=1,
            title="Test Scene",
            description="A test description.",
            choices=[],
        )
        assert scene.id == "test_scene"
        assert scene.act == 1
        assert scene.is_combat == False
        assert scene.is_ending == False

    def test_scene_to_dict(self):
        scene = Scene(id="test", act=1, title="Test", description="Desc", choices=[])
        data = asdict(scene)
        assert data["id"] == "test"
        assert data["act"] == 1

    def test_scene_ending(self):
        scene = Scene(
            id="ending",
            act=3,
            title="The End",
            description="Conclusion",
            choices=[],
            is_ending=True,
            ending_type="hero",
        )
        assert scene.is_ending == True
        assert scene.ending_type == "hero"

    def test_scene_with_flags(self):
        scene = Scene(
            id="test",
            act=1,
            title="Test",
            description="Test",
            flags_required={"has_key": True},
            flags_set={"door_unlocked": True},
            choices=[],
        )
        assert scene.flags_required["has_key"] == True
        assert scene.flags_set["door_unlocked"] == True


class TestChoiceModel:
    """Test Choice data model."""

    def test_choice_creation(self):
        choice = Choice(id="test_choice", text="Test choice", shortcut="A", next_scene="next_scene")
        assert choice.id == "test_choice"
        assert choice.shortcut == "A"
        assert choice.next_scene == "next_scene"

    def test_choice_with_consequence(self):
        consequence = Consequence(type="flag", target="met_npc", value=True)
        choice = Choice(
            id="test", text="Test", shortcut="A", next_scene="next", consequences=[consequence]
        )
        assert len(choice.consequences) == 1
        assert choice.consequences[0].type == "flag"
        assert choice.consequences[0].target == "met_npc"

    def test_choice_with_skill_check(self):
        skill_check = SkillCheck(
            ability="dex",
            dc=15,
            success_next_scene="success_scene",
            failure_next_scene="fail_scene",
        )
        choice = Choice(
            id="test", text="Test", shortcut="A", next_scene="next", skill_check=skill_check
        )
        assert choice.skill_check is not None
        assert choice.skill_check.ability == "dex"
        assert choice.skill_check.dc == 15


class TestConsequenceModel:
    """Test Consequence data model."""

    def test_consequence_flag(self):
        c = Consequence(type="flag", target="has_sword", value=True)
        assert c.type == "flag"
        assert c.target == "has_sword"
        assert c.value == True

    def test_consequence_gold(self):
        c = Consequence(type="gold", target="player", value=-5)
        assert c.type == "gold"
        assert c.value == -5

    def test_consequence_relationship(self):
        c = Consequence(type="relationship", target="npc_name", value=2)
        assert c.type == "relationship"


class TestSkillCheckModel:
    """Test SkillCheck data model."""

    def test_skill_check_creation(self):
        sk = SkillCheck(
            ability="wis", dc=12, success_next_scene="passed", failure_next_scene="failed"
        )
        assert sk.ability == "wis"
        assert sk.dc == 12
        assert sk.success_next_scene == "passed"


class TestGameStateModel:
    """Test GameState data model."""

    def test_gamestate_defaults(self):
        state = GameState(character=None, current_scene="start")
        assert state.current_scene == "start"
        assert state.flags == {}
        assert state.choices_made == []
        assert state.scene_history == []
        assert state.relationships == {}
        assert state.inventory == []
        assert state.current_act == 1
        assert state.is_combat == False
        assert state.turns_spent == 0

    def test_gamestate_with_data(self):
        state = GameState(
            character=None,
            current_scene="scene_2",
            scene_history=["scene_1", "scene_2"],
            choices_made=["choice_a", "choice_b"],
            flags={"has_key": True},
            relationships={"goblin": -5},
            inventory=["sword", "potion"],
            current_act=2,
        )
        assert len(state.scene_history) == 2
        assert state.flags["has_key"] == True
        assert state.relationships["goblin"] == -5
        assert "sword" in state.inventory
        assert state.current_act == 2


class TestDiceRollResultModel:
    """Test DiceRollResult data model."""

    def test_dice_roll_normal(self):
        result = DiceRollResult(dice_type="d20", rolls=[15], modifier=3, total=18, natural=15)
        assert result.dice_type == "d20"
        assert result.rolls == [15]
        assert result.total == 18
        assert result.is_critical == False
        assert result.is_fumble == False

    def test_dice_roll_critical(self):
        result = DiceRollResult(
            dice_type="d20", rolls=[20], modifier=5, total=25, natural=20, is_critical=True
        )
        assert result.is_critical == True
        assert result.natural == 20

    def test_dice_roll_fumble(self):
        result = DiceRollResult(
            dice_type="d20", rolls=[1], modifier=3, total=4, natural=1, is_fumble=True
        )
        assert result.is_fumble == True

    def test_dice_roll_damage(self):
        result = DiceRollResult(dice_type="d8", rolls=[6], modifier=3, total=9)
        assert result.dice_type == "d8"
        assert result.total == 9


class TestEndingModel:
    """Test Ending data model."""

    def test_ending_creation(self):
        ending = Ending(id="hero", title="Hero Ending", description="You saved the day!")
        assert ending.id == "hero"
        assert ending.title == "Hero Ending"

    def test_ending_with_requirements(self):
        ending = Ending(
            id="tragic",
            title="Tragic Ending",
            description="You sacrificed yourself.",
            requirements={"flags_required": {"sacrifice": True}, "min_gold": 0},
        )
        assert ending.requirements["flags_required"]["sacrifice"] == True
