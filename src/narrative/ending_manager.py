"""Ending manager for determining game endings."""

from pathlib import Path
from typing import Dict, Optional
import yaml
from ..utils.logger import get_logger
from .models import Ending, GameState

logger = get_logger(__name__)


class EndingManager:
    """Manages game endings and determines which ending the player earned."""

    def __init__(self, endings_file: Path):
        self.endings_file = endings_file
        self.endings: Dict[str, Ending] = {}
        self._load_endings()

    def _load_endings(self) -> None:
        """Load endings from YAML file."""
        if not self.endings_file.exists():
            logger.warning(f"Endings file not found: {self.endings_file}")
            return

        try:
            with open(self.endings_file, "r") as f:
                data = yaml.safe_load(f)
                for ending_id, ending_data in data.get("endings", {}).items():
                    self.endings[ending_id] = Ending(
                        id=ending_id,
                        title=ending_data.get("title", ""),
                        description=ending_data.get("description", ""),
                        requirements=ending_data.get("requirements", {}),
                    )
                    logger.info(f"Loaded ending: {ending_id}")
        except Exception as e:
            logger.error(f"Error loading endings: {e}")

    def determine_ending(self, state: GameState) -> Optional[Ending]:
        """Determine which ending the player earned based on their choices."""
        for ending in self.endings.values():
            if self._check_requirements(ending.requirements, state):
                logger.info(f"Ending determined: {ending.id}")
                return ending

        logger.warning("No ending matched, using default")
        return self.endings.get("mystery")

    def _check_requirements(self, requirements: Dict, state: GameState) -> bool:
        """Check if game state meets ending requirements."""
        flags_required = requirements.get("flags_required", {})
        for flag, expected_value in flags_required.items():
            if state.flags.get(flag, False) != expected_value:
                return False

        min_gold = requirements.get("min_gold", 0)
        if hasattr(state.character, "gold"):
            if getattr(state.character, "gold", 0) < min_gold:
                return False

        min_level = requirements.get("min_level", 1)
        if hasattr(state.character, "level"):
            if getattr(state.character, "level", 1) < min_level:
                return False

        choices_required = requirements.get("choices_made", [])
        for choice_id in choices_required:
            if choice_id not in state.choices_made:
                return False

        return True

    def get_ending(self, ending_id: str) -> Optional[Ending]:
        """Get ending by ID."""
        return self.endings.get(ending_id)

    def get_all_endings(self) -> Dict[str, Ending]:
        """Get all available endings."""
        return self.endings

    def get_ending_count(self) -> int:
        """Get total number of endings."""
        return len(self.endings)
