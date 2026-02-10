"""Main game engine implementation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto

from .event_bus import EventBus, event_bus, GameEvents, Event
from .config import config
from ..entities.entity import Entity
from ..entities.character import Character
from ..entities.enemy import Enemy
from ..entities.item import Item
from ..world.map import GameMap, Room
from ..world.fov import FieldOfView
from ..combat.combat_engine import CombatEngine
from ..combat.attack_result import AttackResult


class GameState(Enum):
    """Game state."""
    MENU = auto()
    PLAYING = auto()
    COMBAT = auto()
    PAUSED = auto()
    GAMEOVER = auto()


DIRECTION_OFFSETS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
    "northeast": (1, -1),
    "northwest": (-1, -1),
    "southeast": (1, 1),
    "southwest": (-1, 1),
}


@dataclass
class GameEngine:
    """Main game engine coordinating all game systems.

    Attributes:
        state: Current game state
        event_bus: Event bus for game events
        current_floor: Current dungeon floor number
        turn_count: Total turns elapsed
        player: Current player character
        enemies: List of active enemies
        items: List of items on current floor
        current_map: Active dungeon map
        combat_engine: Combat resolution engine
    """

    state: GameState = GameState.MENU
    event_bus: EventBus = field(default_factory=lambda: event_bus)
    current_floor: int = 1
    turn_count: int = 0

    # Entity management
    _player: Optional[Character] = field(default=None, repr=False)
    enemies: List[Enemy] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)

    # Map and FOV
    _current_map: Optional[GameMap] = field(default=None, repr=False)
    _fov_cache: set = field(default_factory=set, repr=False)

    # Combat
    combat_engine: CombatEngine = field(default_factory=CombatEngine)
    _in_combat: bool = False

    def __post_init__(self):
        """Initialize default map after dataclass initialization."""
        if self._current_map is None:
            self._current_map = GameMap(
                width=config.map_width,
                height=config.map_height
            )

    @property
    def player(self) -> Optional[Character]:
        """Get current player character."""
        return self._player

    @property
    def current_map(self) -> GameMap:
        """Get current game map."""
        return self._current_map

    @current_map.setter
    def current_map(self, map_obj: GameMap) -> None:
        """Set current game map."""
        self._current_map = map_obj
        self._fov_cache.clear()

    # =========================================================================
    # State Management
    # =========================================================================

    def start(self) -> None:
        """Start the game."""
        self.state = GameState.PLAYING
        self.event_bus.publish(Event(GameEvents.GAME_STATE_CHANGE, {"state": self.state}))

    def stop(self) -> None:
        """Stop the game."""
        self.state = GameState.GAMEOVER
        self.event_bus.publish(Event(GameEvents.GAME_STATE_CHANGE, {"state": self.state}))

    def pause(self) -> None:
        """Pause the game."""
        self.state = GameState.PAUSED
        self.event_bus.publish(Event(GameEvents.GAME_STATE_CHANGE, {"state": self.state}))

    def resume(self) -> None:
        """Resume the game."""
        self.state = GameState.PLAYING
        self.event_bus.publish(Event(GameEvents.GAME_STATE_CHANGE, {"state": self.state}))

    def get_state(self) -> Dict[str, Any]:
        """Get current game state for serialization.

        Returns:
            Dictionary containing serializable game state.
        """
        state_dict = {
            "state": self.state.name,
            "current_floor": self.current_floor,
            "turn_count": self.turn_count,
        }
        if self._player:
            state_dict["player"] = {
                "name": self._player.name,
                "level": self._player.level,
                "experience": self._player.experience,
                "character_class": self._player.character_class,
                "race": self._player.race,
                "position": self._player.position,
                "hit_points": self._player.hit_points,
                "max_hp": self._player.max_hp,
            }
        return state_dict

    def set_state(self, state_dict: Dict[str, Any]) -> None:
        """Set game state from dictionary.

        Args:
            state_dict: Dictionary containing game state.
        """
        if "state" in state_dict:
            self.state = GameState[state_dict["state"]]
        if "current_floor" in state_dict:
            self.current_floor = state_dict["current_floor"]
        if "turn_count" in state_dict:
            self.turn_count = state_dict["turn_count"]

    # =========================================================================
    # Player Management
    # =========================================================================

    def create_player(self, name: str, character_class: str, race: str) -> Character:
        """Create a new player character.

        Args:
            name: Character name
            character_class: Character class (e.g., "fighter", "wizard")
            race: Character race (e.g., "human", "elf")

        Returns:
            Created Character instance.
        """
        self._player = Character(
            id="player",
            name=name,
            character_class=character_class,
            race=race,
            position=self._current_map.find_random_floor_tile() or (1, 1)
        )
        self.event_bus.publish(Event(GameEvents.PLAYER_ACTION, {
            "action": "create",
            "player": self._player
        }))
        return self._player

    # =========================================================================
    # Entity Management
    # =========================================================================

    def add_enemy(self, enemy: Enemy) -> None:
        """Add an enemy to the current floor.

        Args:
            enemy: Enemy to add.
        """
        self.enemies.append(enemy)
        self.event_bus.publish(Event(GameEvents.MOVEMENT, {
            "action": "spawn",
            "entity": enemy
        }))

    def remove_enemy(self, enemy_id: str) -> None:
        """Remove an enemy by ID.

        Args:
            enemy_id: ID of enemy to remove.
        """
        for i, enemy in enumerate(self.enemies):
            if enemy.id == enemy_id:
                removed = self.enemies.pop(i)
                self.event_bus.publish(Event(GameEvents.DEATH, {
                    "entity": removed,
                    "killer": self._player
                }))
                break

    def add_item(self, item: Item) -> None:
        """Add an item to the current floor.

        Args:
            item: Item to add.
        """
        self.items.append(item)
        self.event_bus.publish(Event(GameEvents.PLAYER_ACTION, {
            "action": "spawn_item",
            "item": item
        }))

    def remove_item(self, item_id: str) -> None:
        """Remove an item by ID.

        Args:
            item_id: ID of item to remove.
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                break

    def get_entities_at(self, x: int, y: int) -> List[Entity]:
        """Get all entities at a position.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            List of entities at position (player, enemies, items).
        """
        entities = []

        # Check player
        if self._player and self._player.position == (x, y):
            entities.append(self._player)

        # Check enemies
        for enemy in self.enemies:
            if enemy.position == (x, y):
                entities.append(enemy)

        # Check items
        for item in self.items:
            if item.position == (x, y):
                entities.append(item)

        return entities

    def get_enemies_at(self, x: int, y: int) -> List[Enemy]:
        """Get all enemies at a position.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            List of enemies at position.
        """
        return [e for e in self.enemies if e.position == (x, y)]

    # =========================================================================
    # Turn System
    # =========================================================================

    def next_turn(self) -> None:
        """Advance the game turn counter."""
        self.turn_count += 1
        self.event_bus.publish(Event(GameEvents.TICK, {"turn": self.turn_count}))

    def player_turn(self, action: Dict[str, Any]) -> bool:
        """Process a player action.

        Args:
            action: Dictionary containing action details.

        Returns:
            True if action was processed successfully.
        """
        if self.state not in (GameState.PLAYING, GameState.COMBAT):
            return False

        action_type = action.get("action")

        if action_type == "move":
            return self.move_player(action.get("direction", "south"))
        elif action_type == "wait":
            self.next_turn()
            return True
        elif action_type == "pickup":
            return self.pickup_item(action.get("item_id"))
        elif action_type == "use":
            return self.use_item(action.get("item_id"))
        elif action_type == "attack":
            return self.player_attack(action.get("target_id"))

        return False

    def enemy_turns(self) -> None:
        """Process turns for all enemies."""
        if not self._player:
            return

        for enemy in list(self.enemies):
            if not enemy.alive:
                continue

            # Simple AI: move toward player if in aggro range
            if enemy.is_in_aggro_range(self._player.position):
                self._process_enemy_ai(enemy)

        self.event_bus.publish(Event(GameEvents.TICK, {"turn": self.turn_count, "phase": "enemies"}))

    def _process_enemy_ai(self, enemy: Enemy) -> None:
        """Process AI for a single enemy.

        Args:
            enemy: Enemy to process.
        """
        if not self._player:
            return

        player_pos = self._player.position
        enemy_pos = enemy.position

        # Calculate direction toward player
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]

        # Normalize to primary direction
        if abs(dx) >= abs(dy):
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            new_pos = (enemy_pos[0] + move_x, enemy_pos[1])
        else:
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0
            new_pos = (enemy_pos[0], enemy_pos[1] + move_y)

        # Try to move
        if self.can_move_to(*new_pos) and not self.get_enemies_at(*new_pos):
            enemy.position = new_pos
            self.event_bus.publish(Event(GameEvents.MOVEMENT, {
                "entity": enemy,
                "from": enemy_pos,
                "to": new_pos
            }))

    # =========================================================================
    # Movement
    # =========================================================================

    def move_player(self, direction: str) -> bool:
        """Move the player in a direction.

        Args:
            direction: Direction string (north, south, east, west, etc.)

        Returns:
            True if move was successful.
        """
        if not self._player:
            return False

        offset = DIRECTION_OFFSETS.get(direction)
        if not offset:
            return False

        new_x = self._player.position[0] + offset[0]
        new_y = self._player.position[1] + offset[1]

        if not self.can_move_to(new_x, new_y):
            return False

        old_pos = self._player.position
        self._player.position = (new_x, new_y)

        # Update FOV
        self._update_fov()

        self.next_turn()
        self.event_bus.publish(Event(GameEvents.MOVEMENT, {
            "entity": self._player,
            "from": old_pos,
            "to": (new_x, new_y)
        }))

        return True

    def can_move_to(self, x: int, y: int) -> bool:
        """Check if a position is passable.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if position can be moved onto.
        """
        # Check map bounds and tile
        if not self._current_map.is_walkable(x, y):
            return False

        # Check for blocking entities
        if self.is_blocked(x, y):
            return False

        return True

    def is_blocked(self, x: int, y: int) -> bool:
        """Check if a position is blocked by an entity.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if position is blocked.
        """
        # Check for enemies
        for enemy in self.enemies:
            if enemy.position == (x, y) and enemy.alive:
                return True

        # Player blocks their own position
        if self._player and self._player.position == (x, y):
            return True

        return False

    # =========================================================================
    # Combat
    # =========================================================================

    def start_combat(self) -> None:
        """Enter combat mode."""
        self.state = GameState.COMBAT
        self._in_combat = True
        self.event_bus.publish(Event(GameEvents.COMBAT, {"action": "start"}))

    def end_combat(self) -> None:
        """Exit combat mode."""
        self.state = GameState.PLAYING
        self._in_combat = False
        self.event_bus.publish(Event(GameEvents.COMBAT, {"action": "end"}))

    def resolve_attack(self, attacker: Any, defender: Any) -> AttackResult:
        """Resolve an attack between entities.

        Args:
            attacker: Entity making the attack.
            defender: Entity being attacked.

        Returns:
            AttackResult with hit, damage, and roll info.
        """
        return self.combat_engine.resolve_attack(attacker, defender)

    def player_attack(self, target_id: str) -> bool:
        """Player attacks a target.

        Args:
            target_id: ID of target enemy.

        Returns:
            True if attack was executed.
        """
        if not self._player:
            return False

        # Find target
        target = None
        for enemy in self.enemies:
            if enemy.id == target_id:
                target = enemy
                break

        if not target:
            return False

        # Check range (simple adjacency check)
        if not self._is_adjacent(self._player.position, target.position):
            return False

        # Resolve attack
        result = self.resolve_attack(self._player, target)

        if result.hit:
            damage = result.damage
            target.take_damage(damage)
            self.event_bus.publish(Event(GameEvents.COMBAT, {
                "action": "hit",
                "attacker": self._player,
                "target": target,
                "damage": damage,
                "critical": result.critical
            }))

            # Check if enemy died
            if not target.alive:
                self.remove_enemy(target.id)
                # Award XP
                xp_gain = int(target.cr * 100)
                self._player.add_experience(xp_gain)
        else:
            self.event_bus.publish(Event(GameEvents.COMBAT, {
                "action": "miss",
                "attacker": self._player,
                "target": target
            }))

        self.next_turn()
        return True

    def _is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if two positions are adjacent.

        Args:
            pos1: First position.
            pos2: Second position.

        Returns:
            True if positions are adjacent (including diagonal).
        """
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return dx <= 1 and dy <= 1 and (dx or dy)

    # =========================================================================
    # Inventory/Items
    # =========================================================================

    def pickup_item(self, item_id: str) -> bool:
        """Pick up an item from the floor.

        Args:
            item_id: ID of item to pick up.

        Returns:
            True if item was picked up.
        """
        if not self._player:
            return False

        # Find item
        item = None
        for i, itm in enumerate(self.items):
            if itm.id == item_id:
                item = itm
                break

        if not item:
            return False

        # Check if player is on item
        if self._player.position != item.position:
            return False

        # Remove from floor and add to inventory (simplified)
        self.items.remove(item)
        self.event_bus.publish(Event(GameEvents.PLAYER_ACTION, {
            "action": "pickup",
            "item": item
        }))

        self.next_turn()
        return True

    def use_item(self, item_id: str) -> bool:
        """Use an item.

        Args:
            item_id: ID of item to use.

        Returns:
            True if item was used.
        """
        if not self._player:
            return False

        self.event_bus.publish(Event(GameEvents.PLAYER_ACTION, {
            "action": "use_item",
            "item_id": item_id
        }))

        self.next_turn()
        return True

    # =========================================================================
    # Map/Floor Management
    # =========================================================================

    def change_floor(self, floor_num: int) -> None:
        """Change to a different floor.

        Args:
            floor_num: Floor number to change to.
        """
        self.current_floor = floor_num
        self._fov_cache.clear()
        self.event_bus.publish(Event(GameEvents.FLOOR_CHANGE, {
            "floor": floor_num
        }))

    def _update_fov(self) -> None:
        """Update field of view from player position."""
        if not self._player:
            return

        fov = FieldOfView(self._current_map)
        self._fov_cache = fov.compute(
            self._player.position[0],
            self._player.position[1],
            radius=config.fov_radius
        )

        # Mark tiles as explored
        for x, y in self._fov_cache:
            self._current_map.mark_explored(x, y)

    @property
    def visible_tiles(self) -> set:
        """Get currently visible tiles."""
        if not self._player:
            return set()
        if not self._fov_cache:
            self._update_fov()
        return self._fov_cache
