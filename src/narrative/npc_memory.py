"""NPC Memory System - tracks what NPCs know about the player."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MemoryEvent:
    """A single memory event."""

    event_type: str  # e.g., "met_player", "quest_accepted", "helped_npc"
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


class NPCMemory:
    """Tracks what an NPC knows about the player."""

    # Relationship thresholds
    HOSTILE_THRESHOLD = -20
    UNFRIENDLY_THRESHOLD = -10
    NEUTRAL_THRESHOLD = 0
    FRIENDLY_THRESHOLD = 10
    ALLY_THRESHOLD = 20

    def __init__(self, npc_id: str, npc_name: str = ""):
        self.npc_id = npc_id
        self.npc_name = npc_name
        self.memories: List[MemoryEvent] = []
        self.relationship: int = 0  # -100 to +100

    def remember(self, event_type: str, context: Dict[str, Any] = None) -> None:
        """Add a memory when player does something notable."""
        import time

        memory = MemoryEvent(
            event_type=event_type,
            timestamp=time.time(),
            context=context or {},
        )
        self.memories.append(memory)

        # Update relationship based on event
        self._update_relationship(event_type, context)

    def _update_relationship(self, event_type: str, context: Optional[Dict]) -> None:
        """Update relationship score based on event."""
        changes = {
            "met_player": 0,
            "quest_accepted": 5,
            "quest_completed": 15,
            "quest_failed": -5,
            "helped_combat": 10,
            "showed_item": 3,
            "asked_about_dungeon": 2,
            "showed_hostility": -15,
            "attacked_npc": -25,
            "stole": -20,
            "insulted": -10,
            "complimented": 5,
            "gave_gift": 10,
        }
        change = changes.get(event_type, 0)
        self.relationship = max(-100, min(100, self.relationship + change))

    def get_relationship_level(self) -> str:
        """Get relationship level name."""
        if self.relationship >= self.ALLY_THRESHOLD:
            return "ally"
        elif self.relationship >= self.FRIENDLY_THRESHOLD:
            return "friendly"
        elif self.relationship >= self.NEUTRAL_THRESHOLD:
            return "neutral"
        elif self.relationship >= self.UNFRIENDLY_THRESHOLD:
            return "unfriendly"
        else:
            return "hostile"

    def get_relationship_description(self) -> str:
        """Get a description of the relationship."""
        level = self.get_relationship_level()
        if level == "ally":
            return "The NPC is a loyal ally who trusts you completely."
        elif level == "friendly":
            return "The NPC views you favorably and is willing to help."
        elif level == "neutral":
            return "The NPC treats you as a neutral acquaintance."
        elif level == "unfriendly":
            return "The NPC is wary and uncooperative toward you."
        else:
            return "The NPC is hostile and may attack you."

    def has_met_player(self) -> bool:
        """Check if NPC has met the player."""
        return any(m.event_type == "met_player" for m in self.memories)

    def remembers_event(self, event_type: str) -> bool:
        """Check if NPC remembers a specific event type."""
        return any(m.event_type == event_type for m in self.memories)

    def get_context_summary(self) -> str:
        """Get a context string for AI prompts."""
        if not self.memories:
            return "This is the first time meeting the player."

        summary_parts = []

        # Add relationship context
        rel_level = self.get_relationship_level()
        summary_parts.append(f"Relationship: {rel_level} (score: {self.relationship})")

        # Add recent memories
        for memory in self.memories[-5:]:  # Last 5 memories
            event = memory.event_type
            ctx = memory.context

            if event == "met_player":
                summary_parts.append("The player approached me.")
            elif event == "quest_accepted":
                summary_parts.append("The player accepted a quest.")
            elif event == "quest_completed":
                summary_parts.append("The player completed a task for me.")
            elif event == "helped_combat":
                char_class = ctx.get("character_class", "unknown")
                summary_parts.append(f"The player fought alongside me ({char_class}).")
            elif event == "showed_item":
                item = ctx.get("item", "something")
                summary_parts.append(f"The player showed me: {item}.")
            elif event == "asked_about_dungeon":
                summary_parts.append("The player asked about the dungeon.")
            elif event == "showed_hostility":
                summary_parts.append("The player threatened me.")
            elif event == "quest_failed":
                summary_parts.append("The player failed my task.")

        return " ".join(summary_parts)


class NPCMemoryManager:
    """Manages memory for all NPCs."""

    def __init__(self):
        self.npc_memories: Dict[str, NPCMemory] = {}

    def get_memory(self, npc_id: str, npc_name: str = "") -> NPCMemory:
        """Get or create memory for an NPC."""
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = NPCMemory(npc_id, npc_name)
        return self.npc_memories[npc_id]

    def record_meeting(self, npc_id: str, npc_name: str = "", context: Dict[str, Any] = None) -> None:
        """Record that player met an NPC."""
        memory = self.get_memory(npc_id, npc_name)
        memory.remember("met_player", context or {})

    def record_event(self, npc_id: str, event_type: str, context: Dict[str, Any] = None) -> None:
        """Record a specific event with an NPC."""
        memory = self.get_memory(npc_id)
        memory.remember(event_type, context or {})

    def get_npc_context(self, npc_id: str) -> str:
        """Get context string for an NPC."""
        memory = self.npc_memories.get(npc_id)
        if not memory:
            return ""
        return memory.get_context_summary()

    def get_relationship(self, npc_id: str) -> int:
        """Get relationship score for an NPC."""
        memory = self.npc_memories.get(npc_id)
        if not memory:
            return 0
        return memory.relationship
