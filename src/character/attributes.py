"""Attribute management and calculations."""

import random
from dataclasses import dataclass
from typing import Dict


def d20() -> int:
    """Roll a 20-sided die."""
    return random.randint(1, 20)


@dataclass
class AttributeSet:
    """Set of six D&D attributes."""

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Valid attribute names
    VALID_ATTRIBUTES = {"strength", "dexterity", "constitution",
                        "intelligence", "wisdom", "charisma"}

    # Attribute score cap
    MAX_SCORE = 30
    MIN_SCORE = 1

    @property
    def str_mod(self) -> int:
        """Strength modifier."""
        return attribute_modifier(self.strength)

    @property
    def dex_mod(self) -> int:
        """Dexterity modifier."""
        return attribute_modifier(self.dexterity)

    @property
    def con_mod(self) -> int:
        """Constitution modifier."""
        return attribute_modifier(self.constitution)

    @property
    def int_mod(self) -> int:
        """Intelligence modifier."""
        return attribute_modifier(self.intelligence)

    @property
    def wis_mod(self) -> int:
        """Wisdom modifier."""
        return attribute_modifier(self.wisdom)

    @property
    def cha_mod(self) -> int:
        """Charisma modifier."""
        return attribute_modifier(self.charisma)

    def _get_modifier(self, attr: str) -> int:
        """Get modifier for an attribute by name."""
        attr_lower = attr.lower()
        if attr_lower == "strength":
            return self.str_mod
        elif attr_lower == "dexterity":
            return self.dex_mod
        elif attr_lower == "constitution":
            return self.con_mod
        elif attr_lower == "intelligence":
            return self.int_mod
        elif attr_lower == "wisdom":
            return self.wis_mod
        elif attr_lower == "charisma":
            return self.cha_mod
        else:
            raise ValueError(f"Invalid attribute: {attr}")

    def _get_score(self, attr: str) -> int:
        """Get score for an attribute by name."""
        attr_lower = attr.lower()
        if attr_lower == "strength":
            return self.strength
        elif attr_lower == "dexterity":
            return self.dexterity
        elif attr_lower == "constitution":
            return self.constitution
        elif attr_lower == "intelligence":
            return self.intelligence
        elif attr_lower == "wisdom":
            return self.wisdom
        elif attr_lower == "charisma":
            return self.charisma
        else:
            raise ValueError(f"Invalid attribute: {attr}")

    def _set_score(self, attr: str, value: int) -> None:
        """Set score for an attribute by name."""
        attr_lower = attr.lower()
        value = max(self.MIN_SCORE, min(value, self.MAX_SCORE))

        if attr_lower == "strength":
            self.strength = value
        elif attr_lower == "dexterity":
            self.dexterity = value
        elif attr_lower == "constitution":
            self.constitution = value
        elif attr_lower == "intelligence":
            self.intelligence = value
        elif attr_lower == "wisdom":
            self.wisdom = value
        elif attr_lower == "charisma":
            self.charisma = value
        else:
            raise ValueError(f"Invalid attribute: {attr}")

    def ability_check(self, attr: str, proficient: bool = False,
                     proficiency_bonus: int = 0) -> int:
        """
        Perform an ability check.

        Args:
            attr: Attribute name (e.g., "strength", "dexterity")
            proficient: Whether the character is proficient
            proficiency_bonus: Character's proficiency bonus

        Returns:
            The result of the d20 + modifier (+ proficiency if proficient)
        """
        modifier = self._get_modifier(attr)
        result = d20()
        if proficient:
            result += modifier + proficiency_bonus
        else:
            result += modifier
        return result

    def increase_attribute(self, attr: str, amount: int = 2) -> None:
        """
        Increase an attribute by the specified amount.

        Args:
            attr: Attribute name
            amount: Amount to increase (default 2)

        Raises:
            ValueError: If attribute name is invalid
        """
        attr_lower = attr.lower()
        if attr_lower not in self.VALID_ATTRIBUTES:
            raise ValueError(f"Invalid attribute: {attr}")

        current = self._get_score(attr)
        new_value = min(current + amount, self.MAX_SCORE)
        self._set_score(attr, new_value)

    def save_throw(self, attr: str, proficient: bool = False,
                   proficiency_bonus: int = 0) -> int:
        """
        Perform a saving throw (same as ability check).

        Args:
            attr: Attribute name
            proficient: Whether the character is proficient
            proficiency_bonus: Character's proficiency bonus

        Returns:
            The result of the d20 + modifier (+ proficiency if proficient)
        """
        return self.ability_check(attr, proficient, proficiency_bonus)

    def get_modifier(self, attr: str) -> int:
        """Get modifier for an attribute by name."""
        return self._get_modifier(attr)

    def get_score(self, attr: str) -> int:
        """Get score for an attribute by name."""
        return self._get_score(attr)

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "AttributeSet":
        """Create from dictionary."""
        return cls(
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            constitution=data.get("constitution", 10),
            intelligence=data.get("intelligence", 10),
            wisdom=data.get("wisdom", 10),
            charisma=data.get("charisma", 10),
        )


def attribute_modifier(score: int) -> int:
    """
    Calculate attribute modifier from score.

    Args:
        score: Attribute score (typically 1-30)

    Returns:
        Modifier value (score - 10) // 2
    """
    return (score - 10) // 2


def ability_score_increase_levels() -> set:
    """Return set of levels that grant ability score increases."""
    return {4, 8, 12, 16, 19}
