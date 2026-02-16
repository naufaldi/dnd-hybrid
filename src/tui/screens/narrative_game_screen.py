"""Narrative game screen for story-driven gameplay."""

import asyncio
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, ScrollableContainer  # noqa: F401
from textual.widgets import Static, Button
from textual import events

from ...narrative.models import Scene, Choice, GameState  # noqa: F401
from ...combat.dice_display import DiceDisplay
from ...utils.logger import get_logger

logger = get_logger(__name__)


class NarrativeGameScreen(Screen):
    """Main game screen for narrative/story-driven gameplay."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_scene: Scene | None = None
        self.game_state: GameState | None = None
        self.dice_display = DiceDisplay()
        self._start_time: float | None = None

    def compose(self):
        """Compose the narrative game screen."""
        yield Horizontal(
            Vertical(
                ScrollableContainer(
                    Static("", id="scene_title"),
                    Static("", id="scene_description", markup=True),
                    id="narrative_content",
                ),
                id="narrative_panel",
            ),
            Vertical(
                Static("CHOICES", id="choices_header"),
                Vertical(id="choices_container"),
                Static("", id="dice_display"),
                Static("", id="status_info"),
                Static("", id="action_buttons"),
                id="sidebar_panel",
            ),
            id="narrative_layout",
        )

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        import time

        self._start_time = time.time()
        if not self.game_state and hasattr(self.app, "narrative_game_state"):
            self.game_state = self.app.narrative_game_state
        if not self.current_scene and hasattr(self.app, "narrative_initial_scene"):
            scene_id = self.app.narrative_initial_scene
            if scene_id and hasattr(self.app, "scene_manager"):
                try:
                    self.current_scene = self.app.scene_manager.get_scene(scene_id)
                except ValueError:
                    pass
        if self.current_scene:
            await self._update_display()

    async def set_game_state(self, state: GameState) -> None:
        """Set the game state."""
        self.game_state = state
        await self._update_display()

    async def set_scene(self, scene: Scene) -> None:
        """Set and display a new scene."""
        self.current_scene = scene
        await self._update_display()

    async def _update_display(self) -> None:
        """Update the narrative display."""
        if not self.current_scene:
            return

        title_widget = self.query_one("#scene_title", Static)
        desc_widget = self.query_one("#scene_description", Static)

        # Format title with decoration per PRD
        title_widget.update(f"[b]═══ {self.current_scene.title} ═══[/b]")

        # Get description - enhance with AI when available for rich content
        if (
            hasattr(self.app, "scene_manager")
            and self.app.scene_manager.ai_client
            and self.game_state
        ):
            try:
                description = await self.app.scene_manager.render_scene(
                    self.current_scene, self.game_state
                )
            except Exception as e:
                logger.warning(f"Scene enhancement failed: {e}")
                description = self.current_scene.description
        else:
            description = self.current_scene.description

        description = self._format_description(description)

        # Check for AI-enhanced dialogue
        if self.current_scene.ai_dialogue and self.current_scene.npc_name:
            # Get AI service from app
            ai_service = self.app.ai_service

            # Build context for AI
            npc_context = self._build_npc_context()

            # Generate AI dialogue
            if ai_service and ai_service.is_enabled():
                try:
                    ai_dialogue = await ai_service.enhance_dialogue(
                        npc_name=self.current_scene.npc_name,
                        mood=self.current_scene.npc_mood or "neutral",
                        context=npc_context,
                        dialogue_type="greeting",
                    )
                    description += self._format_ai_dialogue(
                        self.current_scene.npc_name, ai_dialogue
                    )
                except Exception as e:
                    # Log error for debugging but continue with fallback
                    logger.error(
                        f"AI dialogue generation failed for {self.current_scene.npc_name}: {e}"
                    )
                    # Continue with static description as fallback

        desc_widget.update(description)

        await self._update_choices()
        self._update_status()
        self._update_action_buttons()

    def _format_description(self, description: str) -> str:
        """Format description - make NPC dialogue distinct with styling."""
        import re

        def replace_dialogue(match):
            quote = match.group(0)
            return f"[italic #87CEEB]{quote}[/italic #87CEEB]"

        formatted = re.sub(r"\"([^\"]*)\"", replace_dialogue, description)

        return formatted

    def _format_ai_dialogue(self, npc_name: str, dialogue: str) -> str:
        """Format AI-generated NPC dialogue with distinct roleplay styling."""
        return f"""
[dim]────────────────────────────────[/dim]
[bold cyan]{npc_name}:[/bold cyan] [italic #87CEEB]"{dialogue}"[/italic #87CEEB]
[dim]────────────────────────────────[/dim]"""

    def _build_npc_context(self) -> str:
        """Build context string for NPC AI."""
        if not self.game_state or not self.game_state.character:
            return "A new adventurer approaches."

        char = self.game_state.character
        flags = self.game_state.flags

        context_parts = [
            f"Player is a {char.race} {char.character_class} named {char.name}.",
        ]

        # Get NPC memory context if available
        npc_id = self.current_scene.npc_name if self.current_scene else None
        if npc_id:
            npc_context = self.app.npc_memory.get_npc_context(npc_id.lower())
            if npc_context:
                context_parts.append(npc_context)

        # Add notable flags
        if flags.get("met_stranger"):
            context_parts.append("The player has met me before.")
        if flags.get("learned_dungeon_secret"):
            context_parts.append("The player knows about the dungeon's secrets.")
        if flags.get("allied_with_stranger"):
            context_parts.append("The player is my ally in this quest.")
        if flags.get("accepted_quest"):
            context_parts.append("The player accepted my quest.")

        return " ".join(context_parts)

    async def _update_choices(self) -> None:
        """Update the choices display."""
        choices_container = self.query_one("#choices_container", Vertical)
        await choices_container.remove_children()

        if not self.current_scene or not self.current_scene.choices:
            return

        for choice in self.current_scene.choices:
            if self._is_choice_available(choice):
                # Format: [A] Choice text - shortcut in yellow (NOT a hotkey)
                # Use scene ID prefix to ensure unique button IDs across scenes
                scene_id = self.current_scene.id if self.current_scene else "unknown"
                btn = Button(
                    f"[yellow]{choice.shortcut.upper()}[/yellow] {choice.text}",
                    id=f"choice_{scene_id}_{choice.id}",
                    variant="default",
                )
                choices_container.mount(btn)

    def _is_choice_available(self, choice: Choice) -> bool:
        """Check if a choice is available based on flags."""
        if not self.game_state:
            return True

        for flag, required_value in choice.required_flags.items():
            if self.game_state.flags.get(flag, False) != required_value:
                return False
        return True

    def _update_status(self) -> None:
        """Update the status display."""
        status_widget = self.query_one("#status_info", Static)
        if not self.game_state:
            return

        lines = [
            f"Scene: {self.game_state.current_scene}",
            f"Act: {self.game_state.current_act}",
        ]
        if self.game_state.character:
            char = self.game_state.character
            hp_line = f"HP: {char.hit_points}/{char.max_hp}"
            if hasattr(char, "level"):
                lines.append(f"Level {char.level} {char.race} {char.character_class}")
            lines.append(hp_line)

        status_widget.update("\n".join(lines))

    def _update_action_buttons(self) -> None:
        """Update action buttons (save, etc.)."""
        buttons_container = self.query_one("#action_buttons", Static)
        buttons_container.update("[S] Save Game")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for choices."""
        button_id = event.button.id
        if not button_id:
            return

        if button_id.startswith("choice_"):
            # Button ID format: choice_{scene_id}_{choice_id}
            # Extract choice_id by removing the prefix
            if self.current_scene:
                prefix = f"choice_{self.current_scene.id}_"
                choice_id = button_id.replace(prefix, "", 1)
            else:
                # Fallback: just remove "choice_" prefix
                choice_id = button_id.replace("choice_", "")
            await self._handle_choice(choice_id)
        elif button_id == "btn_save":
            self._save_game()

    def _save_game(self) -> None:
        """Save the current game."""
        if not self.game_state:
            self.notify("No game to save")
            return

        try:
            save_data = self._build_save_data()
            if hasattr(self.app, "save_narrative_game"):
                success = self.app.save_narrative_game(save_data)
                if success:
                    self.notify("Game saved!")
                else:
                    self.notify("Failed to save game")
            else:
                self.notify("Save functionality not available")
        except Exception as e:
            self.notify(f"Error saving: {e}")

    def _build_save_data(self) -> dict:
        """Build save data from current game state."""
        import time
        from ...narrative.serializers import SaveDataBuilder

        metadata = {
            "playtime_seconds": int(time.time() - self._start_time) if self._start_time else 0,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return SaveDataBuilder.build_full_save(self.game_state, metadata)

    async def _handle_choice(self, choice_id: str) -> None:
        """Handle a player's choice."""
        if not self.current_scene or not self.game_state:
            return

        choice = next((c for c in self.current_scene.choices if c.id == choice_id), None)
        if not choice:
            return

        self.game_state.choices_made.append(choice_id)

        for flag, value in choice.set_flags.items():
            self.game_state.flags[flag] = value

        # Check for combat encounter first
        if choice.combat_encounter:
            await self._start_combat(choice)
        elif choice.skill_check:
            self._handle_skill_check(choice)
        else:
            await self._transition_to_scene(choice.next_scene)

    async def _start_combat(self, choice) -> None:
        """Start a combat encounter with the specified enemy."""
        from ...entities.enemy_definitions import get_enemy

        enemy_type = choice.combat_encounter
        enemy = get_enemy(enemy_type)

        if not enemy:
            # Fallback: enemy not found, just transition
            self.notify(f"Unknown enemy: {enemy_type}")
            await self._transition_to_scene(choice.next_scene or "dungeon_entry_hall")
            return

        # Set combat state
        self.game_state.is_combat = True
        self.game_state.current_enemy = enemy_type
        self.game_state.victory_scene = choice.victory_next_scene
        self.game_state.defeat_scene = choice.defeat_scene

        # Import and show combat screen
        try:
            from .combat_screen import CombatScreen

            combat_screen = CombatScreen(
                enemy_name=enemy.name,
                enemy_hp=enemy.hp,
                enemy_ac=enemy.ac,
                enemy_description=enemy.description,
                enemy_attacks=enemy.attacks,
                enemy_abilities=enemy.abilities,
                victory_scene=choice.victory_next_scene or "dungeon_entry_hall",
                defeat_scene=choice.defeat_scene or "death_in_dungeon",
            )
            self.app.push_screen(combat_screen)
        except Exception as e:
            # Fallback if combat screen not available
            self.notify(f"Combat error: {e}, proceeding to next scene")
            await self._transition_to_scene(choice.next_scene or "dungeon_entry_hall")

    def _handle_skill_check(self, choice: Choice) -> None:
        """Handle a skill check for a choice."""
        if not choice.skill_check or not self.game_state:
            return

        skill_check = choice.skill_check
        modifier = self._get_skill_modifier(skill_check.ability)
        ability_names = {
            "str": "Strength",
            "dex": "Dexterity",
            "con": "Constitution",
            "int": "Intelligence",
            "wis": "Wisdom",
            "cha": "Charisma",
        }
        skill_name = ability_names.get(skill_check.ability, skill_check.ability.upper())
        self.app.run_worker(
            self._animate_and_reveal_skill_check(choice, skill_check, modifier, skill_name)
        )

    def _get_skill_modifier(self, ability: str) -> int:
        """Get modifier for an ability from character."""
        ability_mods = {
            "str": "strength_mod",
            "dex": "dexterity_mod",
            "con": "constitution_mod",
            "int": "intelligence_mod",
            "wis": "wisdom_mod",
            "cha": "charisma_mod",
        }
        attr = ability_mods.get(ability, "strength_mod")
        if self.game_state and hasattr(self.game_state.character, attr):
            return getattr(self.game_state.character, attr, 0)
        return 0

    async def _animate_and_reveal_skill_check(
        self, choice: Choice, skill_check, modifier: int, skill_name: str
    ) -> None:
        """Animate rolling, then reveal result."""
        try:
            dice_widget = self.query_one("#dice_display", Static)
        except Exception:
            return

        pre_roll = DiceDisplay.display_pre_roll(skill_name, skill_check.dc, modifier)
        dice_widget.update(pre_roll)
        await asyncio.sleep(0.2)

        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        for i in range(4):
            try:
                q = "?" * ((i % 3) + 1)
                rolling = f"""
╭───────────────────────────────────╮
│    🔍 {skill_name.upper()} CHECK          │
│                                   │
│        DC {skill_check.dc} · {skill_name} ({mod_str})   │
│                                   │
│         Rolling... {q:<3}              │
╰───────────────────────────────────╯"""
                dice_widget.update(rolling)
            except Exception:
                return
            await asyncio.sleep(0.15)

        result = DiceDisplay.roll_d20(modifier)
        success = result.total >= skill_check.dc

        if result.is_critical:
            try:
                import sys

                sys.stdout.write("\a")
                sys.stdout.flush()
            except Exception:
                pass

        try:
            display = DiceDisplay.display_skill_check(skill_name, result, skill_check.dc, success)
            dice_widget.update(display)
        except Exception:
            return

        await asyncio.sleep(0.5)

        if success:
            await self._transition_to_scene(skill_check.success_next_scene)
        else:
            await self._transition_to_scene(skill_check.failure_next_scene)

    async def _transition_to_scene(self, scene_id: str) -> None:
        """Transition to a new scene."""
        if not self.game_state:
            return

        scene_manager = getattr(self.app, "scene_manager", None)
        if not scene_manager:
            return

        try:
            scene = scene_manager.get_scene(scene_id)
            self.game_state.current_scene = scene_id
            self.game_state.scene_history.append(scene_id)
            await self.set_scene(scene)

            for flag, value in scene.flags_set.items():
                self.game_state.flags[flag] = value

            if scene.is_combat:
                self.game_state.is_combat = True

            if scene.is_ending:
                self._handle_ending(scene)

        except ValueError:
            self.notify(f"Scene not found: {scene_id}")

    def _handle_ending(self, scene: Scene) -> None:
        """Handle reaching an ending."""
        if not self.game_state:
            return

        ending_manager = getattr(self.app, "ending_manager", None)
        if not ending_manager:
            return

        ending = ending_manager.determine_ending(self.game_state)
        if not ending:
            return

        self.game_state.ending_determined = ending.id

        import time
        from .ending_screen import EndingScreen

        stats = {
            "Choices Made": str(len(self.game_state.choices_made)),
            "Scenes Visited": str(len(self.game_state.scene_history)),
            "Play Time": f"{int((time.time() - self._start_time) / 60) if self._start_time else 0} minutes",
        }
        ending_screen = EndingScreen()
        ending_screen.set_ending(ending.title, ending.description, stats)
        self.app.push_screen(ending_screen)

    async def on_key(self, event: events.Key) -> None:
        """Handle key presses for quick choice selection."""
        if event.key.lower() == "s":
            self._save_game()
            return
        if event.key == "escape":
            self.app.action_show_menu()
            return

        if not self.current_scene:
            return

        key = event.key.upper()
        for choice in self.current_scene.choices:
            if choice.shortcut.upper() == key and self._is_choice_available(choice):
                await self._handle_choice(choice.id)
                break
