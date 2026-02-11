"""Ending screen for displaying game conclusions."""

from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button
from textual import events


class EndingScreen(Screen):
    """Screen displayed when the game ends."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ending_title: str = ""
        self.ending_description: str = ""
        self.stats: dict = {}

    def compose(self):
        """Compose the ending screen."""
        yield Container(
            Vertical(
                Static("", id="ending_title", markup=True),
                Static("", id="ending_description", markup=True),
                Static("", id="stats_section"),
                Static("", id="ending_buttons"),
                id="ending_content",
            ),
            id="ending_container",
        )

    def set_ending(self, title: str, description: str, stats: dict = None) -> None:
        """Set the ending details to display."""
        self.ending_title = title
        self.ending_description = description
        self.stats = stats or {}
        self._update_display()

    def _update_display(self) -> None:
        """Update the ending display."""
        title_widget = self.query_one("#ending_title", Static)
        desc_widget = self.query_one("#ending_description", Static)
        stats_widget = self.query_one("#stats_section", Static)
        buttons_widget = self.query_one("#ending_buttons", Static)

        title_widget.update(f"[b][size=30]{self.ending_title}[/size][/b]")
        desc_widget.update(f"\n{self.ending_description}\n")

        stats_lines = ["[b]STATISTICS[/b]", "-" * 20]
        if self.stats:
            for key, value in self.stats.items():
                stats_lines.append(f"{key}: {value}")
        else:
            stats_lines.append("No stats available")

        stats_widget.update("\n".join(stats_lines))

        buttons_widget.update("\n\n[Enter] Play Again  [Q] Quit")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._update_display()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "enter":
            self._play_again()
        elif event.key == "q":
            self._quit_game()

    def _play_again(self) -> None:
        """Start a new game."""
        self.app.pop_screen()
        self.app.action_show_menu()

    def _quit_game(self) -> None:
        """Quit the game."""
        self.app.exit()


class EndingData:
    """Data class for ending information."""

    def __init__(
        self,
        title: str,
        description: str,
        ending_type: str = "mystery",
        choices_made: int = 0,
        scenes_visited: int = 0,
        enemies_defeated: int = 0,
        playtime_minutes: int = 0,
    ):
        self.title = title
        self.description = description
        self.ending_type = ending_type
        self.choices_made = choices_made
        self.scenes_visited = scenes_visited
        self.enemies_defeated = enemies_defeated
        self.playtime_minutes = playtime_minutes

    def to_stats_dict(self) -> dict:
        """Convert to stats dictionary for display."""
        return {
            "Choices Made": str(self.choices_made),
            "Scenes Visited": str(self.scenes_visited),
            "Enemies Defeated": str(self.enemies_defeated),
            "Play Time": f"{self.playtime_minutes} minutes",
        }
