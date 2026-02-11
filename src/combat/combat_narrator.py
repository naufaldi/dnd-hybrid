"""Combat narrator for generating battle text descriptions."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..combat.attack_result import AttackResult


class CombatVerbosity(Enum):
    """How much detail to include in combat narration."""

    BRIEF = "brief"
    NORMAL = "normal"
    VERBOSE = "verbose"


@dataclass
class CombatNarrator:
    """Generates text descriptions for combat events."""

    verbosity: CombatVerbosity = CombatVerbosity.NORMAL

    HIT_TEMPLATES = {
        "brief": "Hit for {damage}!",
        "normal": "You hit the {enemy} for {damage} damage!",
        "verbose": "Your attack strikes true! The {enemy} takes {damage} damage.",
    }

    CRITICAL_TEMPLATES = {
        "brief": "CRITICAL! {damage}!",
        "normal": "CRITICAL HIT! You deal {damage} damage to the {enemy}!",
        "verbose": "A devastating strike! You crit the {enemy} for {damage} damage!",
    }

    MISS_TEMPLATES = {
        "brief": "Miss!",
        "normal": "You miss the {enemy}!",
        "verbose": "Your attack goes wide, missing the {enemy} by inches!",
    }

    ENEMY_HIT_TEMPLATES = {
        "brief": "You take {damage}!",
        "normal": "The {enemy} hits you for {damage} damage!",
        "verbose": "The {enemy}'s attack lands! You take {damage} damage.",
    }

    ENEMY_CRITICAL_TEMPLATES = {
        "brief": "CRITICAL! -{damage} HP!",
        "normal": "CRITICAL HIT! The {enemy} deals {damage} damage to you!",
        "verbose": "A brutal blow! The {enemy} crits you for {damage} damage!",
    }

    ENEMY_MISS_TEMPLATES = {
        "brief": "Dodge!",
        "normal": "You dodge the {enemy}'s attack!",
        "verbose": "You nimbly avoid the {enemy}'s strike!",
    }

    DAMAGE_TYPE_TEMPLATES = {
        "slashing": [
            "slices through",
            "cleaves into",
            "shreds",
        ],
        "piercing": [
            "pierces",
            "punctures",
            "skewers",
        ],
        "bludgeoning": [
            "crushes",
            "smashes",
            "bashes",
        ],
        "fire": [
            "engulfs in flames",
            "burns",
            "sears",
        ],
        "cold": [
            "freezes",
            "chills",
            "frosts",
        ],
        "lightning": [
            "shocks",
            "electrocutes",
            "jolts",
        ],
        "acid": [
            "dissolves",
            "corrodes",
            "eats away at",
        ],
        "poison": [
            "poisons",
            "toxins affect",
            "sickens",
        ],
        "default": [
            "hits",
            "strikes",
            "damages",
        ],
    }

    def narrate_player_hit(
        self,
        damage: int,
        enemy_name: str,
        damage_type: str = "default",
    ) -> str:
        """Generate text for player hitting an enemy."""
        template = self.HIT_TEMPLATES[self.verbosity.value]
        verb = self._get_damage_verb(damage_type)

        text = template.format(damage=damage, enemy=enemy_name)
        if self.verbosity == CombatVerbosity.VERBOSE and damage_type != "default":
            text += f" The attack {verb} the {enemy_name}!"

        return text

    def narrate_player_critical(
        self,
        damage: int,
        enemy_name: str,
        damage_type: str = "default",
    ) -> str:
        """Generate text for player getting a critical hit."""
        template = self.CRITICAL_TEMPLATES[self.verbosity.value]
        verb = self._get_damage_verb(damage_type)

        text = template.format(damage=damage, enemy=enemy_name)
        if self.verbosity == CombatVerbosity.VERBOSE:
            text += f" A devastating blow!"

        return text

    def narrate_player_miss(self, enemy_name: str) -> str:
        """Generate text for player missing an enemy."""
        template = self.MISS_TEMPLATES[self.verbosity.value]
        return template.format(enemy=enemy_name)

    def narrate_enemy_hit(
        self,
        damage: int,
        enemy_name: str,
        damage_type: str = "default",
    ) -> str:
        """Generate text for enemy hitting the player."""
        template = self.ENEMY_HIT_TEMPLATES[self.verbosity.value]
        return template.format(damage=damage, enemy=enemy_name)

    def narrate_enemy_critical(
        self,
        damage: int,
        enemy_name: str,
    ) -> str:
        """Generate text for enemy getting a critical hit."""
        template = self.ENEMY_CRITICAL_TEMPLATES[self.verbosity.value]
        return template.format(damage=damage, enemy=enemy_name)

    def narrate_enemy_miss(self, enemy_name: str) -> str:
        """Generate text for enemy missing the player."""
        template = self.ENEMY_MISS_TEMPLATES[self.verbosity.value]
        return template.format(enemy=enemy_name)

    def narrate_combat_intro(self, enemy_name: str, enemy_type: str = "enemy") -> str:
        """Generate text for starting combat."""
        intros = {
            "brief": f"A {enemy_name} appears!",
            "normal": f"Combat with {enemy_name}!",
            "verbose": f"A {enemy_name} blocks your path! Prepare for battle!",
        }
        return intros[self.verbosity.value]

    def narrate_combat_end(self, enemy_name: str, survived: bool = True) -> str:
        """Generate text for combat ending."""
        if survived:
            outs = {
                "brief": f"Defeated {enemy_name}!",
                "normal": f"You've defeated the {enemy_name}!",
                "verbose": f"The {enemy_name} falls, defeated. Victory is yours!",
            }
        else:
            outs = {
                "brief": "You were defeated...",
                "normal": "You have been defeated...",
                "verbose": "Your journey ends here, fallen in battle...",
            }
        return outs[self.verbosity.value]

    def narrate_turn_start(self, character_name: str) -> str:
        """Generate text for turn start."""
        return f"{character_name}'s turn."

    def narrate_health_status(
        self,
        current_hp: int,
        max_hp: int,
        enemy_name: str,
        enemy_hp: int,
        enemy_max_hp: int,
    ) -> str:
        """Generate health status text."""
        player_hp = f"Your HP: {current_hp}/{max_hp}"
        enemy_hp = f"{enemy_name}: {enemy_hp}/{enemy_max_hp}"

        if self.verbosity == CombatVerbosity.BRIEF:
            return f"{player_hp} | {enemy_hp}"
        else:
            return f"{player_hp} | {enemy_hp}"

    def narrate_damage_preview(self, damage_dice: str, modifier: int) -> str:
        """Generate text for damage dice being rolled."""
        return f"Damage: {damage_dice}+{modifier}"

    def narrate_attack_roll(
        self,
        attack_roll: int,
        total: int,
        ac: int,
        is_critical: bool = False,
    ) -> str:
        """Generate text for attack roll result."""
        result = "HIT" if total >= ac else "MISS"
        if is_critical:
            return f"d20: {attack_roll} + bonus = {total} vs AC {ac} [CRITICAL!]"
        return f"d20: {attack_roll} + bonus = {total} vs AC {ac} [{result}]"

    def _get_damage_verb(self, damage_type: str) -> str:
        """Get a verb for the damage type."""
        verbs = self.DAMAGE_TYPE_TEMPLATES.get(damage_type, self.DAMAGE_TYPE_TEMPLATES["default"])
        return verbs[0]


def create_narrator(verbosity: str = "normal") -> CombatNarrator:
    """Factory function to create a CombatNarrator."""
    try:
        v = CombatVerbosity(verbosity)
    except ValueError:
        v = CombatVerbosity.NORMAL
    return CombatNarrator(verbosity=v)
