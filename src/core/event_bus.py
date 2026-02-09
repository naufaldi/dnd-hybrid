"""Event-driven communication system."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Any
from collections import defaultdict
import inspect


@dataclass
class Event:
    """Base event class."""

    type: str
    data: Dict[str, Any]
    source: str = "unknown"


class EventBus:
    """Pub/sub event system with sync and async support."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to synchronous events."""
        self._subscribers[event_type].append(callback)

    def subscribe_async(self, event_type: str, callback: Callable) -> None:
        """Subscribe to asynchronous events."""
        self._async_subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe a callback."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
        if callback in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(callback)

    def publish(self, event: Event) -> None:
        """Publish a synchronous event."""
        for callback in self._subscribers.get(event.type, []):
            callback(event)

    async def publish_async(self, event: Event) -> None:
        """Publish an async event to all subscribers."""
        for callback in self._subscribers.get(event.type, []):
            callback(event)

        for callback in self._async_subscribers.get(event.type, []):
            if inspect.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)


# Event types
class GameEvents:
    PLAYER_ACTION = "player_action"
    COMBAT = "combat"
    MOVEMENT = "movement"
    TICK = "tick"
    GAME_STATE_CHANGE = "game_state_change"
    FLOOR_CHANGE = "floor_change"
    LEVEL_UP = "level_up"
    DEATH = "death"
    SAVE = "save"
    LOAD = "load"


# Global event bus
event_bus = EventBus()
