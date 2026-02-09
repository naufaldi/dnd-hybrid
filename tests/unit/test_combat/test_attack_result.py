"""Tests for attack_result.py - Attack result dataclass."""
from dataclasses import asdict
from src.combat.attack_result import AttackResult


class TestAttackResult:
    """Test suite for AttackResult dataclass."""

    def test_attack_result_creation(self):
        """AttackResult should store all combat information."""
        result = AttackResult(
            hit=True,
            critical=False,
            damage=8,
            rolled=15,
            total=20
        )
        assert result.hit is True
        assert result.critical is False
        assert result.damage == 8
        assert result.rolled == 15
        assert result.total == 20

    def test_attack_result_miss(self):
        """Miss should have zero damage."""
        result = AttackResult(
            hit=False,
            critical=False,
            damage=0,
            rolled=5,
            total=10
        )
        assert result.hit is False
        assert result.damage == 0

    def test_attack_result_critical(self):
        """Critical hit should be marked as such."""
        result = AttackResult(
            hit=True,
            critical=True,
            damage=16,
            rolled=20,
            total=25
        )
        assert result.critical is True
        assert result.hit is True

    def test_attack_result_asdict(self):
        """AttackResult should convert to dict."""
        result = AttackResult(
            hit=True,
            critical=False,
            damage=8,
            rolled=15,
            total=20
        )
        data = asdict(result)
        assert data == {
            "hit": True,
            "critical": False,
            "damage": 8,
            "rolled": 15,
            "total": 20
        }

    def test_attack_result_equality(self):
        """Two AttackResults with same values should be equal."""
        result1 = AttackResult(hit=True, critical=False, damage=8, rolled=15, total=20)
        result2 = AttackResult(hit=True, critical=False, damage=8, rolled=15, total=20)
        assert result1 == result2
