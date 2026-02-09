"""Combat resolution engine for D&D Roguelike."""
from typing import Protocol

from .attack_result import AttackResult
from .dice import DiceRoller


class CombatEntity(Protocol):
    """Protocol for entities that can participate in combat."""

    position: tuple
    dexterity: int
    armor_class: int
    attack_bonus: int
    damage_die: str
    magical_bonus: int

    @property
    def dexterity_modifier(self) -> int:
        """Return the dexterity modifier."""
        ...


class CombatEngine:
    """Handles combat resolution mechanics.

    Implements D&D 5e attack resolution:
    - Natural 20 = critical hit (roll damage dice twice)
    - Natural 1 = automatic miss
    - Attack hits if (d20 + bonuses) >= defender's AC
    - Attack bonus = proficiency_bonus + ability_mod + magical_bonus
    """

    def __init__(self, dice_roller: DiceRoller = None):
        """Initialize combat engine with dice roller.

        Args:
            dice_roller: DiceRoller instance. Creates new one if None.
        """
        self.dice_roller = dice_roller or DiceRoller()

    def resolve_attack(
        self,
        attacker: CombatEntity,
        defender: CombatEntity,
        attack_type: str = "melee"
    ) -> AttackResult:
        """Resolve an attack from attacker against defender.

        Args:
            attacker: The entity making the attack
            defender: The entity being attacked
            attack_type: Type of attack (melee, ranged, thrown) - for future expansion

        Returns:
            AttackResult containing hit status, damage, and roll information
        """
        # Roll the d20
        d20_rolls = self.dice_roller.roll("1d20")
        d20_roll = d20_rolls[0]

        # Calculate attack bonus
        attack_bonus = self._calculate_attack_bonus(attacker)
        total_attack = d20_roll + attack_bonus

        # Check for critical (natural 20)
        is_critical = d20_roll == 20

        # Check for miss (natural 1 or total < AC)
        is_miss = d20_roll == 1 or total_attack < defender.armor_class

        # Calculate damage
        damage = 0
        if not is_miss:
            damage = self._calculate_damage(attacker, is_critical)

        return AttackResult(
            hit=not is_miss,
            critical=is_critical,
            damage=damage,
            rolled=d20_roll,
            total=total_attack
        )

    def _calculate_attack_bonus(self, attacker: CombatEntity) -> int:
        """Calculate the attack bonus for an entity.

        Args:
            attacker: The entity making the attack

        Returns:
            Total attack bonus
        """
        # Base attack bonus + dex modifier + magical bonus
        dex_mod = (attacker.dexterity - 10) // 2
        return attacker.attack_bonus + dex_mod + attacker.magical_bonus

    def _calculate_damage(self, attacker: CombatEntity, is_critical: bool) -> int:
        """Calculate damage dealt by an attack.

        Args:
            attacker: The entity making the attack
            is_critical: Whether this is a critical hit

        Returns:
            Total damage dealt
        """
        # Get damage die notation (e.g., "1d8")
        damage_die = attacker.damage_die

        # Parse number of damage dice
        import re
        match = re.match(r"(\d+)d(\d+)", damage_die)
        if not match:
            raise ValueError(f"Invalid damage die notation: {damage_die}")

        num_dice = int(match.group(1))
        die_size = int(match.group(2))

        # Roll damage dice
        # For critical hits, roll damage dice twice
        rolls_needed = num_dice * 2 if is_critical else num_dice
        damage_dice = self.dice_roller.roll(f"{rolls_needed}d{die_size}")

        # Calculate total damage
        damage = sum(damage_dice)

        # Add damage modifier (only once, not on crit)
        if hasattr(attacker, 'damage_modifier'):
            damage += attacker.damage_modifier
        elif hasattr(attacker, 'damage_mod'):
            damage += attacker.damage_mod

        return damage
