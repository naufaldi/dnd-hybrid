"""Validation for scenes and mechanics."""

from typing import List, Tuple
from .models import Scene
from .mechanics import AVAILABLE_MECHANICS


def validate_scene(scene: Scene) -> Tuple[bool, List[str]]:
    """
    Validate scene references only available mechanics.

    Args:
        scene: The scene to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for duplicate choice IDs within scene
    choice_ids = [c.id for c in scene.choices]
    if len(choice_ids) != len(set(choice_ids)):
        duplicates = [x for x in choice_ids if choice_ids.count(x) > 1]
        errors.append(f"Scene '{scene.id}': Duplicate choice IDs: {set(duplicates)}")

    # Validate scene-level required mechanics
    for mechanic in scene.required_mechanics:
        if mechanic not in AVAILABLE_MECHANICS:
            errors.append(f"Scene '{scene.id}': Unknown mechanic '{mechanic}'")

    # Validate choice-level required mechanics
    for choice in scene.choices:
        for mechanic in choice.required_mechanics:
            if mechanic not in AVAILABLE_MECHANICS:
                errors.append(
                    f"Scene '{scene.id}', Choice '{choice.id}': Unknown mechanic '{mechanic}'"
                )

    return (len(errors) == 0, errors)


def validate_mechanic_availability(
    mechanic: str, character_class: str = None
) -> Tuple[bool, str]:
    """
    Check if a mechanic is available for use.

    Args:
        mechanic: The mechanic name to check
        character_class: Optional character class for class-specific checks

    Returns:
        Tuple of (is_available, reason_if_not)
    """
    if mechanic not in AVAILABLE_MECHANICS:
        return (False, f"mechanic '{mechanic}' not defined in AVAILABLE_MECHANICS")

    return (True, "")


def get_valid_mechanics_for_scene(scene: Scene) -> List[str]:
    """
    Get list of mechanics that are both required and valid.

    Args:
        scene: The scene to check

    Returns:
        List of valid required mechanic names
    """
    valid = []
    for mechanic in scene.required_mechanics:
        if mechanic in AVAILABLE_MECHANICS:
            valid.append(mechanic)
    return valid


def get_missing_mechanics(scene: Scene) -> List[str]:
    """
    Get list of mechanics required by scene but not available.

    Args:
        scene: The scene to check

    Returns:
        List of missing mechanic names
    """
    missing = []
    for mechanic in scene.required_mechanics:
        if mechanic not in AVAILABLE_MECHANICS:
            missing.append(mechanic)
    return missing
