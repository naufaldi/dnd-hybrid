"""ASCII art dice display for terminal."""

import random
from typing import List
from ..narrative.models import DiceRollResult


class DiceDisplay:
    """Generates ASCII art for dice rolls."""

    @staticmethod
    def roll_d20(modifier: int = 0) -> DiceRollResult:
        """Roll a d20 and return DiceRollResult."""
        natural = random.randint(1, 20)
        total = natural + modifier
        is_critical = natural == 20
        is_fumble = natural == 1
        return DiceRollResult(
            dice_type="d20",
            rolls=[natural],
            modifier=modifier,
            total=total,
            natural=natural,
            is_critical=is_critical,
            is_fumble=is_fumble,
        )

    @staticmethod
    def format_d20_roll(result: DiceRollResult) -> str:
        """Format d20 roll as string for display."""
        return DiceDisplay.display_d20(result)

    @staticmethod
    def display_d20(result: DiceRollResult) -> str:
        """Generate ASCII art for d20 roll."""
        natural = result.natural
        total = result.total
        modifier = result.modifier
        is_crit = result.is_critical
        is_fumble = result.is_fumble

        if is_crit:
            face = f"★ {natural} ★"
            result_text = "CRITICAL HIT!"
        elif is_fumble:
            face = f"  {natural}  "
            result_text = "MISS..."
        else:
            face = f"  {natural}  "
            result_text = "HIT!" if total >= 10 else "MISS..."

        return f"""
╭───────────────────────────────────╮
│         ⚔️ D20 ROLL ⚔️            │
│                                   │
│        ╭─────────────╮            │
│        │{face:^13}│            │
│        ╰─────────────╯            │
│         d20 = {natural}                   │
│       +{modifier} (bonus) = {total:>2}              │
│                                   │
│    ╭───────────────────╮         │
│    │   {result_text:^15}   │         │
│    ╰───────────────────╯         │
╰───────────────────────────────────╯"""

    @staticmethod
    def display_pre_roll(skill_name: str, dc: int, modifier: int) -> str:
        """Display pre-roll context: DC and modifier before rolling."""
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        return f"""
╭───────────────────────────────────╮
│    🔍 {skill_name.upper()} CHECK          │
│                                   │
│        DC {dc} · {skill_name} ({mod_str})   │
│                                   │
│         Rolling... ?              │
╰───────────────────────────────────╯"""

    @staticmethod
    def display_damage(dice: str, rolls: List[int], total: int) -> str:
        """Generate ASCII art for damage roll."""
        rolls_str = str(rolls)[1:-1]
        return f"""
Damage: {dice} = [{rolls_str}] = {total}
"""

    @staticmethod
    def display_skill_check(skill_name: str, result: DiceRollResult, dc: int, success: bool) -> str:
        """Generate ASCII art for skill check."""
        natural = result.natural
        modifier = result.modifier
        total = result.total

        if result.is_critical:
            face = f"★ {natural} ★"
            status = "★ CRITICAL ★"
        elif result.is_fumble:
            face = f"  {natural}  "
            status = "✗ FUMBLE ✗"
        else:
            face = f"  {natural}  "
            status = "✓ SUCCESS!" if success else "✗ FAILED"

        return f"""
╭───────────────────────────────────╮
│    🔍 {skill_name.upper()} CHECK ({result.dice_type})   │
│                                   │
│        ╭─────────────╮            │
│        │{face:^13}│            │
│        ╰─────────────╯            │
│         d20 = {natural}                   │
│       +{modifier} ({skill_name[:3].upper()}) = {total:>2}              │
│        DC {dc}                        │
│                                   │
│    ╭───────────────────╮         │
│    │   {status:^15}   │         │
│    ╰───────────────────╯         │
╰───────────────────────────────────╯"""

    @staticmethod
    def display_full_attack(
        attacker_name: str,
        target_name: str,
        attack_result: DiceRollResult,
        damage_result: DiceRollResult,
        hit: bool,
    ) -> str:
        """Display full attack sequence."""
        attack_display = DiceDisplay.display_d20(attack_result)

        damage_str = ""
        if hit and damage_result:
            damage_str = DiceDisplay.display_damage(
                f"{damage_result.dice_type}+{damage_result.modifier}",
                damage_result.rolls,
                damage_result.total,
            )

        outcome = (
            f"You hit {target_name} for {damage_result.total} damage!"
            if hit
            else f"You miss {target_name}!"
        )

        return f"""
═══════════════════════════════════════════════════
⚔️ ATTACK: {target_name} ⚔️

{attacker_name} attacks {target_name}!

{attack_display}
{outcome}
═══════════════════════════════════════════════════
"""
