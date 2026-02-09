"""Logging utilities for the game."""

import logging
import sys
from pathlib import Path
from typing import Optional


class GameLogger:
    """Game logger with file and console output."""

    def __init__(
        self,
        name: str = "dnd_roguelike",
        log_file: Optional[Path] = None,
        level: int = logging.INFO,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        # Console handler
        console = logging.StreamHandler(sys.stderr)
        console.setLevel(level)
        console.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        )
        self.logger.addHandler(console)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            )
            self.logger.addHandler(file_handler)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg)


# Default logger instance
default_logger: Optional[GameLogger] = None


def get_logger(name: str = "dnd_roguelike", log_file: Optional[Path] = None) -> GameLogger:
    """Get or create a logger instance."""
    global default_logger
    if default_logger is None:
        default_logger = GameLogger(name, log_file)
    return default_logger
