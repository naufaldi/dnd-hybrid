"""Tests for Enemy class."""

import pytest
from src.entities.enemy import Enemy, AIType, EnemyType


class TestEnemy:
    def test_enemy_creation(self):
        enemy = Enemy(
            id="goblin1", name="Goblin", enemy_type=EnemyType.HUMANOID,
            cr=0.25, armor_class=15, max_hp=7, position=(5, 5)
        )
        assert enemy.id == "goblin1"
        assert enemy.alive is True

    def test_enemy_aggressive_default(self):
        enemy = Enemy(id="test", name="Test", ai_type=AIType.AGGRESSIVE, aggro_range=5)
        assert enemy.ai_type == AIType.AGGRESSIVE

    def test_enemy_in_aggro_range(self):
        enemy = Enemy(id="test", name="Test", position=(5, 5), aggro_range=5)
        assert enemy.is_in_aggro_range((7, 5)) is True  # distance 2
        assert enemy.is_in_aggro_range((15, 5)) is False  # distance 10

    def test_enemy_take_damage(self):
        enemy = Enemy(id="test", name="Test", max_hp=10, current_hp=10)
        enemy.take_damage(4)
        assert enemy.current_hp == 6

    def test_enemy_dies_at_zero(self):
        enemy = Enemy(id="test", name="Test", max_hp=10, current_hp=5)
        enemy.take_damage(5)
        assert enemy.current_hp == 0
        assert enemy.alive is False
