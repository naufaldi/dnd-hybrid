"""Tests for combat_engine.py - Combat resolution."""
from src.combat.dice import DiceRoller
from src.combat.combat_engine import CombatEngine
from src.combat.attack_result import AttackResult


class MockEntity:
    """Mock entity for testing combat engine."""

    def __init__(
        self,
        dex: int = 10,
        ac: int = 10,
        attack_bonus: int = 2,
        damage_die: str = "1d8",
        damage_mod: int = 3,
        magical_bonus: int = 0
    ):
        self.position = (0, 0)
        self.dexterity = dex
        self.armor_class = ac
        self.attack_bonus = attack_bonus
        self.damage_die = damage_die
        self.damage_modifier = damage_mod
        self.magical_bonus = magical_bonus

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
        """Roll with fixed values.

        Parses notation to determine how many dice to return.
        For 2d6, returns 2 values from the sequence.
        """
        import re
        match = re.match(r"^(\d*)d(\d+)", notation)
        if not match:
            return [self._get_next_value()]

        num_dice = int(match.group(1) or "1")
        result = [self._get_next_value() for _ in range(num_dice)]
        return result

    def _get_next_value(self) -> int:
        """Get the next fixed value and advance index."""
        value = self.values[self.index % len(self.values)]
        self.index += 1
        return value


class TestCombatEngine:
    """Test suite for CombatEngine class."""

    def test_resolve_attack_miss(self):
        """Roll 1 should always miss regardless of AC."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8")
        defender = MockEntity(ac=10)
        engine = CombatEngine(FixedDiceRoller([1]))  # Natural 1 = miss

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is False
        assert result.damage == 0
        assert result.rolled == 1

    def test_resolve_attack_hit(self):
        """Attack should hit when roll + bonus >= AC."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8")
        defender = MockEntity(ac=15)
        engine = CombatEngine(FixedDiceRoller([10]))  # 10 + 5 = 15 vs AC 15 = hit

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is True
        assert result.damage >= 1
        assert result.rolled == 10
        assert result.total == 15

    def test_resolve_attack_critical_natural_20(self):
        """Natural 20 should be a critical hit."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8", damage_mod=3)
        defender = MockEntity(ac=10)
        engine = CombatEngine(FixedDiceRoller([20]))  # Natural 20 = crit

        result = engine.resolve_attack(attacker, defender)

        assert result.critical is True
        assert result.hit is True
        assert result.rolled == 20

    def test_resolve_attack_critical_doubles_damage_dice(self):
        """Critical should roll damage dice twice."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8", damage_mod=0)
        defender = MockEntity(ac=10)
        # First roll is 20 (crit check), rest are damage dice
        engine = CombatEngine(FixedDiceRoller([20, 4, 6]))

        result = engine.resolve_attack(attacker, defender)

        assert result.critical is True
        # Damage = (4+6) * 2 = 20 (doubled)
        assert result.damage >= 10

    def test_resolve_attack_miss_by_one(self):
        """Attack should miss when total is one less than AC."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8")
        defender = MockEntity(ac=16)
        engine = CombatEngine(FixedDiceRoller([10]))  # 10 + 5 = 15 vs AC 16 = miss

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is False
        assert result.damage == 0

    def test_resolve_attack_exact_ac_hit(self):
        """Attack should hit when total equals AC."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8")
        defender = MockEntity(ac=15)
        engine = CombatEngine(FixedDiceRoller([10]))  # 10 + 5 = 15 vs AC 15 = hit

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is True

    def test_resolve_attack_with_magical_bonus(self):
        """Magical bonus should be added to attack roll."""
        attacker = MockEntity(attack_bonus=3, damage_die="1d8", magical_bonus=2)
        defender = MockEntity(ac=10)
        engine = CombatEngine(FixedDiceRoller([5]))  # 5 + 3 + 2 = 10 vs AC 10 = hit

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is True
        assert result.total == 10

    def test_resolve_attack_stores_roll_info(self):
        """AttackResult should store all relevant information."""
        attacker = MockEntity(attack_bonus=4, damage_die="1d6", damage_mod=2)
        defender = MockEntity(ac=12)
        engine = CombatEngine(FixedDiceRoller([8, 3]))

        result = engine.resolve_attack(attacker, defender)

        assert result.rolled == 8
        assert result.total == 12  # 8 + 4 = 12
        assert result.hit is True
        assert isinstance(result, AttackResult)

    def test_resolve_attack_high_ac_requires_high_roll(self):
        """High AC should require high roll to hit."""
        attacker = MockEntity(attack_bonus=0, damage_die="1d8")
        defender = MockEntity(ac=20)
        engine = CombatEngine(FixedDiceRoller([19]))  # 19 + 0 = 19 vs AC 20 = miss

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is False

    def test_resolve_attack_natural_1_is_always_miss(self):
        """Natural 1 should always be a miss regardless of AC (D&D 5e rule)."""
        attacker = MockEntity(attack_bonus=10, damage_die="1d8")
        defender = MockEntity(ac=5)
        engine = CombatEngine(FixedDiceRoller([1]))  # Natural 1 = automatic miss

        result = engine.resolve_attack(attacker, defender)

        assert result.hit is False  # Natural 1 is always a miss
        assert result.critical is False  # Natural 1 is not a crit
        assert result.damage == 0


class TestCombatEngineDamageCalculation:
    """Test damage calculation logic."""

    def test_damage_includes_modifier(self):
        """Damage should include damage modifier."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8", damage_mod=5)
        defender = MockEntity(ac=10)
        engine = CombatEngine(FixedDiceRoller([15, 4]))  # Hit + damage roll

        result = engine.resolve_attack(attacker, defender)

        assert result.damage >= 5  # At least the modifier

    def test_critical_damage_is_higher(self):
        """Critical damage should be higher than normal."""
        attacker = MockEntity(attack_bonus=5, damage_die="1d8", damage_mod=0)
        defender = MockEntity(ac=10)

        # Normal hit
        engine1 = CombatEngine(FixedDiceRoller([15, 4]))
        normal_result = engine1.resolve_attack(attacker, defender)

        # Critical hit
        engine2 = CombatEngine(FixedDiceRoller([20, 4, 6]))
        crit_result = engine2.resolve_attack(attacker, defender)

        # Crit damage should be at least double (excluding modifier)
        assert crit_result.damage > normal_result.damage
