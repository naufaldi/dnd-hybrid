"""Serializers for narrative game state."""

from typing import Dict, Any, Optional, List
from dataclasses import asdict

from ..narrative.models import GameState, Scene, Choice, SkillCheck, Consequence, Ending
from ..entities.character import Character


class NarrativeSerializer:
    """Serializes and deserializes narrative game state."""

    @staticmethod
    def serialize_game_state(state: GameState) -> Dict[str, Any]:
        """Serialize GameState to a dictionary for saving."""
        data = {
            "current_scene": state.current_scene,
            "scene_history": state.scene_history,
            "choices_made": state.choices_made,
            "flags": state.flags,
            "relationships": state.relationships,
            "inventory": state.inventory,
            "current_act": state.current_act,
            "is_combat": state.is_combat,
            "ending_determined": state.ending_determined,
            "turns_spent": state.turns_spent,
            "character": None,
        }

        if state.character is not None:
            data["character"] = NarrativeSerializer.serialize_character(state.character)

        return data

    @staticmethod
    def deserialize_game_state(data: Dict[str, Any]) -> GameState:
        """Deserialize GameState from a dictionary."""
        character_data = data.get("character")
        character = None
        if character_data:
            character = NarrativeSerializer.deserialize_character(character_data)

        return GameState(
            character=character,
            current_scene=data.get("current_scene", "start"),
            scene_history=data.get("scene_history", []),
            choices_made=data.get("choices_made", []),
            flags=data.get("flags", {}),
            relationships=data.get("relationships", {}),
            inventory=data.get("inventory", []),
            current_act=data.get("current_act", 1),
            is_combat=data.get("is_combat", False),
            ending_determined=data.get("ending_determined"),
            turns_spent=data.get("turns_spent", 0),
        )

    @staticmethod
    def serialize_character(character: Character) -> Dict[str, Any]:
        """Serialize Character to a dictionary."""
        return {
            "id": character.id,
            "name": character.name,
            "level": character.level,
            "experience": character.experience,
            "character_class": character.character_class,
            "race": character.race,
            "strength": character.strength,
            "dexterity": character.dexterity,
            "constitution": character.constitution,
            "intelligence": character.intelligence,
            "wisdom": character.wisdom,
            "charisma": character.charisma,
            "current_hp": character.current_hp,
            "max_hp": character.max_hp,
            "gold": getattr(character, "gold", 0),
            "position": character.position,
        }

    @staticmethod
    def deserialize_character(data: Dict[str, Any]) -> Character:
        """Deserialize Character from a dictionary."""
        character = Character(
            id=data["id"],
            name=data["name"],
            character_class=data.get("character_class", "fighter"),
            race=data.get("race", "human"),
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            constitution=data.get("constitution", 10),
            intelligence=data.get("intelligence", 10),
            wisdom=data.get("wisdom", 10),
            charisma=data.get("charisma", 10),
        )
        character.level = data.get("level", 1)
        character.experience = data.get("experience", 0)
        character.hit_points = data.get("current_hp", data.get("hit_points", character.hit_points))

        if "position" in data:
            character.position = data["position"]

        return character

    @staticmethod
    def serialize_scene(scene: Scene) -> Dict[str, Any]:
        """Serialize Scene to a dictionary."""
        return {
            "id": scene.id,
            "act": scene.act,
            "title": scene.title,
            "description": scene.description,
            "choices": [asdict(c) for c in scene.choices],
            "flags_set": scene.flags_set,
            "is_combat": scene.is_combat,
            "is_ending": scene.is_ending,
            "ending_type": scene.ending_type,
        }

    @staticmethod
    def deserialize_scene(data: Dict[str, Any]) -> Scene:
        """Deserialize Scene from a dictionary."""
        choices = []
        for choice_data in data.get("choices", []):
            skill_check = None
            if choice_data.get("skill_check"):
                sc_data = choice_data["skill_check"]
                skill_check = SkillCheck(
                    ability=sc_data["ability"],
                    dc=sc_data["dc"],
                    success_next_scene=sc_data["success_next_scene"],
                    failure_next_scene=sc_data["failure_next_scene"],
                )

            consequences = []
            for cons_data in choice_data.get("consequences", []):
                consequences.append(
                    Consequence(
                        type=cons_data["type"],
                        target=cons_data["target"],
                        value=cons_data["value"],
                    )
                )

            choice = Choice(
                id=choice_data["id"],
                text=choice_data["text"],
                shortcut=choice_data["shortcut"],
                next_scene=choice_data["next_scene"],
                consequences=consequences,
                skill_check=skill_check,
                required_flags=choice_data.get("required_flags", {}),
                set_flags=choice_data.get("set_flags", {}),
            )
            choices.append(choice)

        return Scene(
            id=data["id"],
            act=data["act"],
            title=data["title"],
            description=data["description"],
            choices=choices,
            next_scene=data.get("next_scene"),
            flags_required=data.get("flags_required", {}),
            flags_set=data.get("flags_set", {}),
            is_combat=data.get("is_combat", False),
            is_ending=data.get("is_ending", False),
            ending_type=data.get("ending_type"),
        )


class SaveDataBuilder:
    """Builder for creating save data packages."""

    @staticmethod
    def build_full_save(
        game_state: GameState, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a complete save data package."""
        return {
            "version": 2,
            "game_type": "narrative",
            "metadata": metadata or {},
            "narrative_state": NarrativeSerializer.serialize_game_state(game_state),
        }

    @staticmethod
    def extract_narrative_state(save_data: Dict[str, Any]) -> GameState:
        """Extract narrative state from save data."""
        return NarrativeSerializer.deserialize_game_state(save_data.get("narrative_state", {}))
