"""Reactive state management for TUI."""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class StateChange:
    """Represents a state change event."""

    key: str
    old_value: Any
    new_value: Any


class StateStore:
    """Observable state store for reactive UI updates.

    Provides a simple pub/sub mechanism for state changes
    that widgets can subscribe to for reactive updates.
    """

    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[Callable[[StateChange], None]]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value.

        Args:
            key: State key to retrieve.
            default: Default value if key doesn't exist.

        Returns:
            The state value or default.
        """
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a state value and notify subscribers.

        Args:
            key: State key to set.
            value: Value to set.
        """
        old_value = self._state.get(key)
        self._state[key] = value

        # Notify subscribers
        change = StateChange(key=key, old_value=old_value, new_value=value)
        self._notify_subscribers(key, change)

    def subscribe(self, key: str, callback: Callable[[StateChange], None]) -> None:
        """Subscribe to state changes for a key.

        Args:
            key: State key to subscribe to.
            callback: Function to call on state change.
        """
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)

    def unsubscribe(self, key: str, callback: Callable[[StateChange], None]) -> None:
        """Unsubscribe from state changes.

        Args:
            key: State key to unsubscribe from.
            callback: Callback to remove.
        """
        if key in self._subscribers:
            self._subscribers[key] = [
                cb for cb in self._subscribers[key] if cb != callback
            ]

    def _notify_subscribers(self, key: str, change: StateChange) -> None:
        """Notify all subscribers of a state change."""
        # Notify key-specific subscribers
        for callback in self._subscribers.get(key, []):
            try:
                callback(change)
            except Exception:
                pass

        # Notify wildcard subscribers
        for callback in self._subscribers.get("*", []):
            try:
                callback(change)
            except Exception:
                pass

    def __getattr__(self, name: str) -> Any:
        """Allow direct attribute access to state values."""
        if name.startswith("_"):
            raise AttributeError(name)
        return self.get(name, None)

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow direct attribute setting for state values."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.set(name, value)


# Global state instance
_state: Optional[StateStore] = None


def get_state() -> StateStore:
    """Get the global state store instance."""
    global _state
    if _state is None:
        _state = StateStore()
    return _state
