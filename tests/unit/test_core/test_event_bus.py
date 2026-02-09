"""Tests for event bus."""

import pytest
from unittest.mock import Mock
from src.core.event_bus import EventBus, Event


class TestEventBusSync:
    def test_sync_subscriber_receives_event(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe("test_event", handler)
        bus.publish(Event("test_event", {"data": "value"}))

        assert len(received) == 1
        assert received[0].data["data"] == "value"

    def test_multiple_subscribers(self):
        bus = EventBus()
        received1 = []
        received2 = []

        bus.subscribe("event", lambda e: received1.append(e))
        bus.subscribe("event", lambda e: received2.append(e))
        bus.publish(Event("event", {}))

        assert len(received1) == 1
        assert len(received2) == 1

    def test_unsubscribe_removes_handler(self):
        bus = EventBus()
        handler = Mock()
        bus.subscribe("event", handler)
        bus.unsubscribe("event", handler)
        bus.publish(Event("event", {}))
        handler.assert_not_called()

    def test_unsubscribe_one_preserves_others(self):
        bus = EventBus()
        handler1 = Mock()
        handler2 = Mock()
        bus.subscribe("event", handler1)
        bus.subscribe("event", handler2)
        bus.unsubscribe("event", handler1)
        bus.publish(Event("event", {}))
        handler1.assert_not_called()
        handler2.assert_called()


class TestEventBusAsync:
    @pytest.mark.asyncio
    async def test_async_subscriber_receives_event(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe_async("test_event", handler)
        await bus.publish_async(Event("test_event", {"data": "value"}))

        assert len(received) == 1


class TestEventStructure:
    def test_event_has_type_and_data(self):
        event = Event("combat", {"damage": 10})
        assert event.type == "combat"
        assert event.data["damage"] == 10

    def test_event_default_source(self):
        event = Event("test", {})
        assert event.source == "unknown"
