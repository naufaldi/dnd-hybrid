"""AI fallback templates when generation fails or is disabled."""

from typing import Dict

FALLBACK_DIALOGUE: Dict[str, Dict[str, str]] = {
    "enigmatic": {
        "greeting": "The figure's eyes glint with secrets untold...",
        "hostile": "You would do well to leave these matters to those who understand them.",
        "neutral": "Perhaps... you might be of use yet.",
        "friendly": "I have watched your journey with interest.",
        "curious": "Tell me more of this quest you speak.",
    },
    "hostile": {
        "greeting": "You dare approach me?!",
        "hostile": "Your words are meaningless. Prepare to die!",
        "neutral": "Speak quickly, before I lose my patience.",
        "friendly": "I... might have misjudged you.",
        "curious": "Why should I trust a stranger?",
    },
    "neutral": {
        "greeting": "A traveler. How unexpected.",
        "hostile": "You push your luck, mortal.",
        "neutral": "We are not enemies... yet.",
        "friendly": "Perhaps we can help each other.",
        "curious": "What brings you to these parts?",
    },
    "friendly": {
        "greeting": "Ah, a friend! Please, come closer.",
        "hostile": "Wait, let's talk about this!",
        "neutral": "I'm glad our paths crossed.",
        "friendly": "It's good to see a friendly face.",
        "curious": "Tell me of your adventures!",
    },
}

FALLBACK_SCENE_DESCRIPTIONS: Dict[str, str] = {
    "tavern": "The warmth of the hearth and the murmur of patrons fill the air. Wooden beams creak overhead as you take in the scene.",
    "dungeon": "Stone walls loom around you, damp and ancient. Torchlight casts flickering shadows across the passage ahead.",
    "exploration": "You find yourself in an unfamiliar place. The path ahead holds both promise and peril.",
}


def get_fallback_dialogue(mood: str, dialogue_type: str = "greeting") -> str:
    """Get static fallback dialogue when AI is unavailable."""
    mood_templates = FALLBACK_DIALOGUE.get(mood, FALLBACK_DIALOGUE["neutral"])
    return mood_templates.get(dialogue_type, mood_templates["greeting"])


def get_fallback_outcome(action: str, success: bool) -> str:
    """Get static fallback outcome when AI is unavailable."""
    if success:
        return f"Your {action} succeeds! Luck favors the bold."
    return f"Your {action} fails. The odds were against you."


def get_fallback_scene_description(scene_id: str) -> str:
    """Get generic rich fallback description when AI fails."""
    for key, desc in FALLBACK_SCENE_DESCRIPTIONS.items():
        if key in scene_id.lower():
            return desc
    return "The scene unfolds before you, details emerging as your eyes adjust to the surroundings."
