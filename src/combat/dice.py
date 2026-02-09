"""D&D dice mechanics for combat system."""
import random
import re
from typing import List


class DiceRoller:
    """Handles D&D dice notation rolling.

    Supports standard dice notation:
    - d4, d6, d8, d10, d12, d20, d100
    - Multiple dice: 2d6, 4d8, etc.
    - Modifiers: + and - operations
    - Examples: 2d6+3, 1d20-1, 4d6+2
    """

    DICE_SIZES = [4, 6, 8, 10, 12, 20, 100]

    def __init__(self, seed: int = None):
        """Initialize dice roller with optional seed for reproducibility."""
        self._random = random.Random(seed)

    def roll(self, notation: str) -> List[int]:
        """Roll dice according to notation.

        Args:
            notation: Dice notation string (e.g., "2d6+3", "1d20")

        Returns:
            List of individual die results

        Examples:
            >>> roller = DiceRoller()
            >>> roller.roll("2d6+3")
            [4, 6]  # Returns dice values, sum = 13
            >>> roller.roll("1d20")
            [15]
        """
        notation = notation.lower().replace(" ", "")

        # Parse dice notation
        match = re.match(r"^(\d*)d(\d+)([+-]\d+)?$", notation)
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        num_dice_str = match.group(1) or "1"
        die_size = int(match.group(2))

        num_dice = int(num_dice_str)

        if die_size not in self.DICE_SIZES:
            raise ValueError(f"Unsupported die size: d{die_size}. Supported: {self.DICE_SIZES}")

        if num_dice < 0:
            raise ValueError("Number of dice cannot be negative")

        # Roll the dice
        results = [self._random.randint(1, die_size) for _ in range(num_dice)]

        return results

    def roll_sum(self, notation: str) -> int:
        """Roll dice and return total including modifier.

        Args:
            notation: Dice notation string (e.g., "2d6+3")

        Returns:
            Total including all dice and modifiers

        Examples:
            >>> roller = DiceRoller()
            >>> roller.roll_sum("2d6+3")
            13  # Sum of dice + modifier
        """
        notation = notation.lower().replace(" ", "")

        # Parse dice notation
        match = re.match(r"^(\d*)d(\d+)([+-]\d+)?$", notation)
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        num_dice_str = match.group(1) or "1"
        die_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        num_dice = int(num_dice_str)

        if die_size not in self.DICE_SIZES:
            raise ValueError(f"Unsupported die size: d{die_size}. Supported: {self.DICE_SIZES}")

        # Roll the dice and sum
        dice_sum = sum(self._random.randint(1, die_size) for _ in range(num_dice))

        return dice_sum + modifier
