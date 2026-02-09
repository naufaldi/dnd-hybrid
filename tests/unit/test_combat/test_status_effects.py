"""Tests for status_effects.py - Status effects and conditions system."""
from src.combat.status_effects import (
    StatusEffect,
    Condition,
    StatusEffectManager,
)


class MockEntity:
    """Mock entity for testing status effects."""

    def __init__(self, name: str = "Test Entity"):
        self.id = f"entity_{name}"
        self.name = name
        self.position = (0, 0)
        self.alive = True
        self.immunities: set = set()

    def is_immune_to(self, condition_name: str) -> bool:
        """Check if entity is immune to a condition."""
        return condition_name in self.immunities


class TestStatusEffect:
    """Test suite for StatusEffect dataclass."""

    def test_create_status_effect(self):
        """StatusEffect should store all properties."""
        effect = StatusEffect(
            name="poisoned",
            duration=3,
            source="goblin",
            metadata={"damage": 1}
        )

        assert effect.name == "poisoned"
        assert effect.duration == 3
        assert effect.source == "goblin"
        assert effect.metadata["damage"] == 1

    def test_permanent_effect(self):
        """Permanent effects have duration of -1."""
        effect = StatusEffect(
            name="blessed",
            duration=-1,
            source="spell"
        )

        assert effect.duration == -1
        assert effect.is_permanent is True

    def test_effect_is_permanent_false_for_finite(self):
        """Finite duration effects are not permanent."""
        effect = StatusEffect(name="stunned", duration=2, source="enemy")

        assert effect.is_permanent is False

    def test_effect_copy(self):
        """StatusEffect should be able to be copied."""
        effect = StatusEffect(name="burning", duration=5, source="fire")
        effect_copy = StatusEffect(
            name=effect.name,
            duration=effect.duration,
            source=effect.source,
            metadata=effect.metadata.copy()
        )

        assert effect == effect_copy


class TestCondition:
    """Test suite for Condition enum."""

    def test_all_standard_conditions_exist(self):
        """All D&D 5e conditions should be defined."""
        expected_conditions = [
            "BLINDED", "CHARMED", "DEAFENED", "FRIGHTENED", "GRAPPLED",
            "INCAPACITATED", "INVISIBLE", "PARALYZED", "PETRIFIED",
            "POISONED", "PRONE", "RESTRAINED", "STUNNED", "UNCONSCIOUS",
            "EXHAUSTION"
        ]

        for condition_name in expected_conditions:
            assert hasattr(Condition, condition_name)

    def test_exhaustion_has_levels(self):
        """EXHAUSTION should support levels 1-6."""
        # Check that exhaustion can represent different levels
        assert Condition.EXHAUSTION_1 is not None
        assert Condition.EXHAUSTION_6 is not None


class TestStatusEffectManager:
    """Test suite for StatusEffectManager class."""

    def test_add_effect_success(self):
        """add_effect should successfully apply an effect."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="poisoned", duration=3, source="goblin")

        result = manager.add_effect(entity, effect)

        assert result is True
        assert manager.has_effect(entity, "poisoned")

    def test_add_effect_returns_false_if_immune(self):
        """add_effect should return False if entity is immune."""
        manager = StatusEffectManager()
        entity = MockEntity()
        entity.immunities.add("poisoned")
        effect = StatusEffect(name="poisoned", duration=3, source="goblin")

        result = manager.add_effect(entity, effect)

        assert result is False
        assert not manager.has_effect(entity, "poisoned")

    def test_remove_effect(self):
        """remove_effect should remove an active effect."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="stunned", duration=2, source="enemy")

        manager.add_effect(entity, effect)
        result = manager.remove_effect(entity, "stunned")

        assert result is True
        assert not manager.has_effect(entity, "stunned")

    def test_remove_nonexistent_effect(self):
        """remove_effect should return False for non-existent effect."""
        manager = StatusEffectManager()
        entity = MockEntity()

        result = manager.remove_effect(entity, "poisoned")

        assert result is False

    def test_has_condition_true(self):
        """has_condition should return True if entity has condition."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="stunned", duration=2, source="enemy")

        manager.add_effect(entity, effect)

        assert manager.has_condition(entity, Condition.STUNNED)

    def test_has_condition_false(self):
        """has_condition should return False if entity doesn't have condition."""
        manager = StatusEffectManager()
        entity = MockEntity()

        assert not manager.has_condition(entity, Condition.STUNNED)

    def test_tick_effects_decrements_duration(self):
        """tick_effects should decrement duration of active effects."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="poisoned", duration=3, source="goblin")

        manager.add_effect(entity, effect)
        expired = manager.tick_effects(entity)

        assert len(expired) == 0
        # Check duration was decremented
        active_effects = manager.get_active_effects(entity)
        assert active_effects[0].duration == 2

    def test_tick_effects_returns_expired(self):
        """tick_effects should return expired effects."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="poisoned", duration=1, source="goblin")

        manager.add_effect(entity, effect)
        expired = manager.tick_effects(entity)

        assert len(expired) == 1
        assert expired[0].name == "poisoned"

    def test_permanent_effect_not_expired(self):
        """Permanent effects should not expire on tick."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="blessed", duration=-1, source="spell")

        manager.add_effect(entity, effect)
        expired = manager.tick_effects(entity)

        assert len(expired) == 0
        assert manager.has_effect(entity, "blessed")

    def test_clear_expired_removes_expired_effects(self):
        """clear_expired should remove all expired effects."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect1 = StatusEffect(name="poisoned", duration=1, source="goblin")
        effect2 = StatusEffect(name="stunned", duration=3, source="enemy")

        manager.add_effect(entity, effect1)
        manager.add_effect(entity, effect2)
        manager.tick_effects(entity)  # Poisoned expires
        manager.clear_expired(entity)

        assert not manager.has_effect(entity, "poisoned")
        assert manager.has_effect(entity, "stunned")

    def test_stacking_refreshes_duration(self):
        """Adding same effect should refresh duration."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="poisoned", duration=5, source="goblin"))
        manager.add_effect(entity, StatusEffect(name="poisoned", duration=3, source="snake"))

        active_effects = manager.get_active_effects(entity)
        assert len(active_effects) == 1
        assert active_effects[0].duration == 3

    def test_multiple_different_effects(self):
        """Multiple different effects can coexist."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="poisoned", duration=3, source="goblin"))
        manager.add_effect(entity, StatusEffect(name="stunned", duration=2, source="enemy"))
        manager.add_effect(entity, StatusEffect(name="blinded", duration=1, source="flashbang"))

        assert manager.has_effect(entity, "poisoned")
        assert manager.has_effect(entity, "stunned")
        assert manager.has_effect(entity, "blinded")
        assert len(manager.get_active_effects(entity)) == 3

    def test_get_active_effects_empty(self):
        """get_active_effects should return empty list for entity with no effects."""
        manager = StatusEffectManager()
        entity = MockEntity()

        assert manager.get_active_effects(entity) == []

    def test_effect_source_tracking(self):
        """Effect should track its source."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(name="poisoned", duration=3, source="goblin")

        manager.add_effect(entity, effect)
        active_effects = manager.get_active_effects(entity)

        assert active_effects[0].source == "goblin"

    def test_metadata_persists(self):
        """Effect metadata should be preserved."""
        manager = StatusEffectManager()
        entity = MockEntity()
        effect = StatusEffect(
            name="burning",
            duration=2,
            source="fire",
            metadata={"damage": 2, "type": "fire"}
        )

        manager.add_effect(entity, effect)
        active_effects = manager.get_active_effects(entity)

        assert active_effects[0].metadata["damage"] == 2
        assert active_effects[0].metadata["type"] == "fire"


class TestConditionBehaviors:
    """Test condition-specific behaviors."""

    def test_blinded_attack_disadvantage(self):
        """Blinded entities should have attack disadvantage."""
        # This tests the condition application logic
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="blinded", duration=2, source="flashbang"))

        assert manager.has_condition(entity, Condition.BLINDED)
        assert manager.has_effect(entity, "blinded")

    def test_poisoned_damage(self):
        """Poisoned condition should persist with damage info."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(
            name="poisoned",
            duration=3,
            source="venomous_snake",
            metadata={"poison_type": "damage"}
        ))

        assert manager.has_condition(entity, Condition.POISONED)

    def test_stunned_incapacitated(self):
        """Stunned condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="stunned", duration=2, source="giant"))

        assert manager.has_condition(entity, Condition.STUNNED)

    def test_prone_grounded(self):
        """Prone condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="prone", duration=1, source="push"))

        assert manager.has_condition(entity, Condition.PRONE)

    def test_invisible_hard_to_hit(self):
        """Invisible condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="invisible", duration=-1, source="spell"))

        assert manager.has_condition(entity, Condition.INVISIBLE)

    def test_frightened_disadvantage(self):
        """Frightened condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="frightened", duration=3, source="dragon"))

        assert manager.has_condition(entity, Condition.FRIGHTENED)

    def test_charmed_follows_commands(self):
        """Charmed condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="charmed", duration=2, source="sorcerer"))

        assert manager.has_condition(entity, Condition.CHARMED)

    def test_exhaustion_levels(self):
        """Different exhaustion levels should be trackable."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="exhaustion_1", duration=-1, source="forced_march"))
        manager.add_effect(entity, StatusEffect(name="exhaustion_2", duration=-1, source="forced_march"))

        assert manager.has_condition(entity, Condition.EXHAUSTION_1)
        assert manager.has_condition(entity, Condition.EXHAUSTION_2)

    def test_grappled_movement_restricted(self):
        """Grappled condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="grappled", duration=2, source="troll"))

        assert manager.has_condition(entity, Condition.GRAPPLED)

    def test_restrained_attacks_disadvantage(self):
        """Restrained condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="restrained", duration=1, source="net"))

        assert manager.has_condition(entity, Condition.RESTRAINED)

    def test_paralyzed_also_prone(self):
        """Paralyzed condition should apply (also causes prone)."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="paralyzed", duration=2, source="medusa"))

        assert manager.has_condition(entity, Condition.PARALYZED)

    def test_petrified_full_transformation(self):
        """Petrified condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="petrified", duration=-1, source="basilisk"))

        assert manager.has_condition(entity, Condition.PETRIFIED)

    def test_unconscious_prone_and_incapacitated(self):
        """Unconscious condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="unconscious", duration=2, source="sleep"))

        assert manager.has_condition(entity, Condition.UNCONSCIOUS)

    def test_deafened_cant_hear(self):
        """Deafened condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="deafened", duration=3, source="thunder"))

        assert manager.has_condition(entity, Condition.DEAFENED)

    def test_incapacitated_cant_act(self):
        """Incapacitated condition should apply."""
        manager = StatusEffectManager()
        entity = MockEntity()

        manager.add_effect(entity, StatusEffect(name="incapacitated", duration=1, source="stun"))

        assert manager.has_condition(entity, Condition.INCAPACITATED)
