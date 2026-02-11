"""Narrative game screen for story-driven gameplay."""

from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button
from textual import events
from textual.app import App

from ...narrative.models import Scene, Choice, GameState, DiceRollResult
from ...narrative.scene_manager import SceneManager
from ...narrative.ending_manager import EndingManager
from ...combat.dice_display import DiceDisplay


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

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        import time

        self._start_time = time.time()
        self._update_display()

    def set_game_state(self, state: GameState) -> None:
        """Set the game state."""
        self.game_state = state
        self._update_display()

    def set_scene(self, scene: Scene) -> None:
        """Set and display a new scene."""
        self.current_scene = scene
        self._update_display()

    def _update_display(self) -> None:
        """Update the narrative display."""
        if not self.current_scene:
            return

        title_widget = self.query_one("#scene_title", Static)
        desc_widget = self.query_one("#scene_description", Static)

        title_widget.update(f"[b]{self.current_scene.title}[/b]")
        desc_widget.update(self.current_scene.description)

        self._update_choices()
        self._update_status()
        self._update_action_buttons()

    def _update_choices(self) -> None:
        """Update the choices display."""
        choices_container = self.query_one("#choices_container", Vertical)
        choices_container.remove_children()

        if not self.current_scene or not self.current_scene.choices:
            return

        for choice in self.current_scene.choices:
            if self._is_choice_available(choice):
                btn = Button(
                    f"[{choice.shortcut}] {choice.text}",
                    id=f"choice_{choice.id}",
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for choices."""
        button_id = event.button.id
        if not button_id:
            return

        if button_id.startswith("choice_"):
            choice_id = button_id.replace("choice_", "")
            self._handle_choice(choice_id)
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

    def _handle_choice(self, choice_id: str) -> None:
        """Handle a player's choice."""
        if not self.current_scene or not self.game_state:
            return

        choice = next((c for c in self.current_scene.choices if c.id == choice_id), None)
        if not choice:
            return

        self.game_state.choices_made.append(choice_id)

        for flag, value in choice.set_flags.items():
            self.game_state.flags[flag] = value

        if choice.skill_check:
            self._handle_skill_check(choice)
        else:
            self._transition_to_scene(choice.next_scene)

    def _handle_skill_check(self, choice: Choice) -> None:
        """Handle a skill check for a choice."""
        if not choice.skill_check or not self.game_state:
            return

        skill_check = choice.skill_check
        dice_widget = self.query_one("#dice_display", Static)

        ability_mods = {
            "str": 0,
            "dex": 0,
            "con": 0,
            "int": 0,
            "wis": 0,
            "cha": 0,
        }

        if hasattr(self.game_state.character, "strength_mod"):
            ability_mods["str"] = getattr(self.game_state.character, "strength_mod", 0)
        if hasattr(self.game_state.character, "dexterity_mod"):
            ability_mods["dex"] = getattr(self.game_state.character, "dexterity_mod", 0)
        if hasattr(self.game_state.character, "constitution_mod"):
            ability_mods["con"] = getattr(self.game_state.character, "constitution_mod", 0)
        if hasattr(self.game_state.character, "intelligence_mod"):
            ability_mods["int"] = getattr(self.game_state.character, "intelligence_mod", 0)
        if hasattr(self.game_state.character, "wisdom_mod"):
            ability_mods["wis"] = getattr(self.game_state.character, "wisdom_mod", 0)
        if hasattr(self.game_state.character, "charisma_mod"):
            ability_mods["cha"] = getattr(self.game_state.character, "charisma_mod", 0)

        modifier = ability_mods.get(skill_check.ability, 0)
        result = DiceDisplay.roll_d20(modifier)

        display = DiceDisplay.format_d20_roll(result)
        display += f"\n\nDC: {skill_check.dc} | Ability: {skill_check.ability.upper()}"
        dice_widget.update(display)

        if result.total >= skill_check.dc:
            self._transition_to_scene(skill_check.success_next_scene)
        else:
            self._transition_to_scene(skill_check.failure_next_scene)

    def _transition_to_scene(self, scene_id: str) -> None:
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
            self.set_scene(scene)

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
        if ending_manager:
            ending = ending_manager.determine_ending(self.game_state)
            if ending:
                self.game_state.ending_determined = ending.id

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for quick choice selection."""
        if not self.current_scene:
            return

        key = event.key.upper()
        for choice in self.current_scene.choices:
            if choice.shortcut.upper() == key and self._is_choice_available(choice):
                self._handle_choice(choice.id)
                break

        if event.key == "escape":
            self.app.action_show_menu()
