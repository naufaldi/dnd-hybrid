"""Load game screen for resuming saved games."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button
from textual import events
from textual.app import App

from datetime import datetime


class SaveFileInfo:
    """Information about a save file."""

    def __init__(self, path: Path, data: Dict[str, Any]):
        self.path = path
        self.data = data
        self.filename = path.name
        self.timestamp = data.get("metadata", {}).get("saved_at", "Unknown")
        self.scene = data.get("narrative_state", {}).get("current_scene", "Unknown")
        self.character_name = "Unknown"
        if data.get("narrative_state", {}).get("character"):
            self.character_name = (
                data.get("narrative_state", {}).get("character", {}).get("name", "Unknown")
            )


class LoadGameScreen(Screen):
    """Screen for loading saved games."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saves: List[SaveFileInfo] = []
        self.selected_index = 0

    def compose(self):
        """Compose the load game screen."""
        yield Container(
            Vertical(
                Static("[b]Load Game[/b]", id="load_title"),
                Static("", id="saves_list"),
                Static("", id="save_details"),
                Static("\n[Enter] Load  [Escape] Back", id="load_help"),
                id="load_content",
            ),
            id="load_container",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._load_saves()
        self._update_display()

    def _load_saves(self) -> None:
        """Load list of available save files."""
        self.saves = []
        save_dir = Path.home() / ".dnd_roguelike" / "saves"

        if not save_dir.exists():
            return

        import json
        import zlib

        for save_file in sorted(
            save_dir.glob("*.sav"), key=lambda f: f.stat().st_mtime, reverse=True
        ):
            try:
                with open(save_file, "rb") as f:
                    compressed = f.read()
                    decompressed = zlib.decompress(compressed)
                    data = json.loads(decompressed)

                if data.get("game_type") == "narrative":
                    self.saves.append(SaveFileInfo(save_file, data))
            except Exception:
                continue

    def _update_display(self) -> None:
        """Update the saves list display."""
        list_widget = self.query_one("#saves_list", Static)
        details_widget = self.query_one("#save_details", Static)

        if not self.saves:
            list_widget.update("No saves found.")
            details_widget.update("")
            return

        lines = []
        for i, save in enumerate(self.saves):
            prefix = ">" if i == self.selected_index else " "
            lines.append(f"{prefix} {save.filename}")
            if i == self.selected_index:
                lines.append(f"   Scene: {save.scene}")
                lines.append(f"   Saved: {save.timestamp}")

        list_widget.update("\n".join(lines))
        details_widget.update("")

    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self._update_display()
        elif event.key == "down":
            self.selected_index = min(len(self.saves) - 1, self.selected_index + 1)
            self._update_display()
        elif event.key == "enter":
            self._load_selected_save()
        elif event.key == "escape":
            self.app.pop_screen()

    def _load_selected_save(self) -> None:
        """Load the selected save file."""
        if not self.saves or self.selected_index >= len(self.saves):
            return

        save_info = self.saves[self.selected_index]

        try:
            save_data = save_info.data
            self.dismiss(save_data)
        except Exception as e:
            self.notify(f"Failed to load save: {e}")
