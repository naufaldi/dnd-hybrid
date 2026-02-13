"""Combat screen for narrative combat encounters."""

from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button
from textual import events
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Attack:
    """Enemy attack for combat."""
    name: str
    damage: str
    damage_type: str
    attack_bonus: int = 0
    reach: Optional[str] = None


class CombatScreen(Screen):
    """Screen for combat encounters in narrative mode."""

    def __init__(
        self,
        enemy_name: str,
        enemy_hp: int,
        enemy_ac: int,
        enemy_description: str = "",
        enemy_attacks: List[Attack] = None,
        enemy_abilities: List[str] = None,
        victory_scene: str = "dungeon_entry_hall",
        defeat_scene: str = "death_in_dungeon",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.enemy_name = enemy_name
        self.enemy_max_hp = enemy_hp
        self.enemy_current_hp = enemy_hp
        self.enemy_ac = enemy_ac
        self.enemy_description = enemy_description
        self.enemy_attacks = enemy_attacks or []
        self.enemy_abilities = enemy_abilities or []
        self.victory_scene = victory_scene
        self.defeat_scene = defeat_scene
        self.combat_log: List[str] = []
        self.player_action: Optional[str] = None

    def compose(self):
        """Compose the combat screen."""
        yield Container(
            Vertical(
                Static("", id="combat_title"),
                Static("", id="combat_narrative", markup=True),
                Static("", id="combat_status"),
                Static("", id="combat_log", markup=True),
                Static("", id="combat_choices"),
                id="combat_content",
            ),
            id="combat_container",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._update_display()
        self._add_combat_message(f"A {self.enemy_name} appears! {self.enemy_description}")

    def _update_display(self) -> None:
        """Update the combat display."""
        # Get player info from game state
        game_state = getattr(self.app, "narrative_game_state", None)
        player_hp = "??"
        player_max_hp = "??"
        player_name = "Adventurer"

        if game_state and game_state.character:
            char = game_state.character
            player_hp = str(char.hit_points)
            player_max_hp = str(char.max_hp)
            player_name = char.name

        # Title
        title_widget = self.query_one("#combat_title", Static)
        title_widget.update(f"[b][size=25]═══ ⚔ Combat: {self.enemy_name} ⚔ ═══[/size][/b]")

        # Status
        status_widget = self.query_one("#combat_status", Static)
        status = f"""
[yellow]{player_name}[/yellow]
HP: {player_hp}/{player_max_hp}

[red]{self.enemy_name}[/red]
HP: {self.enemy_current_hp}/{self.enemy_max_hp}  AC: {self.enemy_ac}
"""
        if self.enemy_abilities:
            status += f"Abilities: {', '.join(self.enemy_abilities)}"
        status_widget.update(status)

        # Combat log
        log_widget = self.query_one("#combat_log", Static)
        log_widget.update("\n".join(self.combat_log[-5:]) if self.combat_log else "Combat begins!")

        # Choices
        choices_widget = self.query_one("#combat_choices", Static)
        if self.player_action is None:
            choices_widget.update(
                "\n[b]Choose your action:[/b]\n"
                "[yellow]A[/yellow] Attack\n"
                "[yellow]D[/yellow] Defend (+2 AC)\n"
                "[yellow]F[/yellow] Flee (DEX check DC 12)"
            )
        else:
            choices_widget.update("\n[b]Action in progress...[/b]")

    def _add_combat_message(self, message: str) -> None:
        """Add a message to the combat log."""
        self.combat_log.append(message)
        self._update_display()

    async def on_key(self, event: events.Key) -> None:
        """Handle key presses for combat actions."""
        if self.player_action is not None:
            return  # Already taking an action

        key = event.key.lower()

        if key == "a":
            await self._player_attack()
        elif key == "d":
            await self._player_defend()
        elif key == "f":
            await self._player_flee()
        elif key == "escape":
            self.app.pop_screen()

    async def _player_attack(self) -> None:
        """Player attacks the enemy."""
        import random
        from ...combat.dice import roll_dice, ability_modifier

        game_state = getattr(self.app, "narrative_game_state", None)
        if not game_state or not game_state.character:
            self._add_combat_message("Error: No character found")
            return

        char = game_state.character

        # Roll attack
        attack_roll = random.randint(1, 20)
        attack_modifier = getattr(char, f"{char.equipment.get('weapon_stat', 'strength')}_mod", 0) if hasattr(char, 'equipment') else char.strength_mod

        # Check proficiency
        proficiency = 2  # Level 1
        total_attack = attack_roll + attack_modifier + proficiency

        self._add_combat_message(f"You attack: d20({attack_roll}) + {attack_modifier} + {proficiency} = {total_attack} vs AC {self.enemy_ac}")

        if attack_roll == 1:
            self._add_combat_message("[red]Critical failure! You miss![/red]")
            await self._enemy_turn()
            return

        if total_attack >= self.enemy_ac:
            # Hit! Roll damage
            damage_dice = char.equipment.get('weapon_damage', '1d8') if hasattr(char, 'equipment') else "1d8"
            damage = roll_dice(damage_dice) + attack_modifier
            if attack_roll == 20:
                damage *= 2
                self._add_combat_message(f"[green]CRITICAL HIT! You deal {damage} damage![/green]")
            else:
                self._add_combat_message(f"[green]Hit! You deal {damage} damage![/green]")

            self.enemy_current_hp -= damage

            if self.enemy_current_hp <= 0:
                await self._combat_victory()
                return
        else:
            self._add_combat_message("[red]You miss![/red]")

        await self._enemy_turn()

    async def _player_defend(self) -> None:
        """Player takes a defensive stance."""
        self._add_combat_message("[cyan]You raise your shield, bracing for impact (+2 AC).[/cyan]")
        # TODO: Implement actual AC bonus
        await self._enemy_turn()

    async def _player_flee(self) -> None:
        """Player attempts to flee."""
        import random

        dex_check = random.randint(1, 20)
        dex_mod = 0  # Could get from character

        total = dex_check + dex_mod
        self._add_combat_message(f"You try to flee: d20({dex_check}) + {dex_mod} = {total} vs DC 12")

        if total >= 12:
            self._add_combat_message("[green]You successfully escape![/green]")
            # Return to previous scene
            self.app.pop_screen()
            # Transition back
            from .narrative_game_screen import NarrativeGameScreen
            # Just pop back
        else:
            self._add_combat_message("[red]You fail to escape![/red]")
            await self._enemy_turn()

    async def _enemy_turn(self) -> None:
        """Enemy takes their turn."""
        import random

        if self.enemy_current_hp <= 0:
            return

        # Simple enemy AI - always attack
        attack_roll = random.randint(1, 20)
        enemy_attack_bonus = 3  # Default

        total_attack = attack_roll + enemy_attack_bonus

        # Get player AC
        game_state = getattr(self.app, "narrative_game_state", None)
        player_ac = 10  # Default
        if game_state and game_state.character:
            player_ac = game_state.character.armor_class

        self._add_combat_message(f"{self.enemy_name} attacks: d20({attack_roll}) + {enemy_attack_bonus} = {total_attack} vs AC {player_ac}")

        if attack_roll == 1:
            self._add_combat_message(f"[cyan]The {self.enemy_name} trips and misses![/cyan]")
            return

        if total_attack >= player_ac:
            # Hit!
            damage_dice = "1d6"
            damage = random.randint(1, 6) + enemy_attack_bonus
            if attack_roll == 20:
                damage *= 2
                self._add_combat_message(f"[red]CRITICAL HIT! {self.enemy_name} deals {damage} damage![/red]")
            else:
                self._add_combat_message(f"[red]{self.enemy_name} hits for {damage} damage![/red]")

            if game_state and game_state.character:
                game_state.character.hit_points -= damage
                if game_state.character.hit_points <= 0:
                    await self._combat_defeat()
        else:
            self._add_combat_message(f"[cyan]The {self.enemy_name} misses![/cyan]")

        self._update_display()

    async def _combat_victory(self) -> None:
        """Handle combat victory."""
        self._add_combat_message(f"\n[green][b]VICTORY! You have defeated the {self.enemy_name}![/b][/green]")

        # Clear combat state
        game_state = getattr(self.app, "narrative_game_state", None)
        if game_state:
            game_state.is_combat = False
            game_state.current_enemy = None

        # Pop combat screen and transition
        self.app.pop_screen()

        # Transition to victory scene
        if self.victory_scene:
            from .narrative_game_screen import NarrativeGameScreen
            screen = NarrativeGameScreen()
            scene_mgr = getattr(self.app, "scene_manager", None)
            if scene_mgr:
                scene = scene_mgr.get_scene(self.victory_scene)
                screen.set_scene(scene)
                screen.game_state = game_state

    async def _combat_defeat(self) -> None:
        """Handle combat defeat."""
        self._add_combat_message(f"\n[red][b]DEFEAT! You have fallen in battle...[/b][/red]")

        # Clear combat state
        game_state = getattr(self.app, "narrative_game_state", None)
        if game_state:
            game_state.is_combat = False
            game_state.current_enemy = None

        # Pop combat screen
        self.app.pop_screen()

        # Transition to defeat scene
        if self.defeat_scene:
            from .narrative_game_screen import NarrativeGameScreen
            screen = NarrativeGameScreen()
            scene_mgr = getattr(self.app, "scene_manager", None)
            if scene_mgr:
                scene = scene_mgr.get_scene(self.defeat_scene)
                screen.set_scene(scene)
                screen.game_state = game_state
