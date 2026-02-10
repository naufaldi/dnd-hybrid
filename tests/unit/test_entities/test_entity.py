"""Tests for Entity class."""

import pytest
from src.entities.entity import Entity, EntityType


class TestEntity:
    def test_entity_creation(self):
        entity = Entity(id="ent1", name="TestEntity", entity_type=EntityType.PLAYER)
        assert entity.id == "ent1"
        assert entity.name == "TestEntity"
        assert entity.entity_type == EntityType.PLAYER
        assert entity.position == (0, 0)
        assert entity.alive is True

    def test_entity_equality(self):
        e1 = Entity(id="ent1", name="Entity1", entity_type=EntityType.PLAYER)
        e2 = Entity(id="ent1", name="Entity2", entity_type=EntityType.ENEMY)
        e3 = Entity(id="ent2", name="Entity1", entity_type=EntityType.PLAYER)
        assert e1 == e2  # Same ID
        assert e1 != e3  # Different ID

    def test_entity_hash(self):
        e1 = Entity(id="ent1", name="Entity1", entity_type=EntityType.PLAYER)
        e2 = Entity(id="ent1", name="Entity2", entity_type=EntityType.ENEMY)
        assert hash(e1) == hash(e2)  # Same ID means same hash

    def test_entity_move(self):
        entity = Entity(id="ent1", name="Test", entity_type=EntityType.ITEM)
        entity.move_to(5, 10)
        assert entity.position == (5, 10)
