"""Tests for logger module."""
from pathlib import Path
import tempfile
from src.utils.logger import GameLogger, get_logger


class TestGameLogger:
    def test_logger_creation(self):
        logger = GameLogger("test_logger")
        assert logger.logger is not None
        assert logger.logger.name == "test_logger"

    def test_logger_has_console_handler(self):
        logger = GameLogger("test_console")
        assert len(logger.logger.handlers) > 0

    def test_logger_debug_method(self):
        logger = GameLogger("test_debug")
        # Should not raise
        logger.debug("debug message")

    def test_logger_info_method(self):
        logger = GameLogger("test_info")
        logger.info("info message")

    def test_logger_warning_method(self):
        logger = GameLogger("test_warning")
        logger.warning("warning message")

    def test_logger_error_method(self):
        logger = GameLogger("test_error")
        logger.error("error message")

    def test_logger_critical_method(self):
        logger = GameLogger("test_critical")
        logger.critical("critical message")

    def test_logger_with_file_handler(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = GameLogger("test_file", log_file=log_file)
            logger.info("test message")
            assert log_file.exists()


class TestGetLogger:
    def test_get_logger_returns_logger(self):
        logger = get_logger("singleton_test")
        assert isinstance(logger, GameLogger)

    def test_get_logger_singleton(self):
        logger1 = get_logger("singleton_test2")
        logger2 = get_logger("singleton_test2")
        assert logger1 is logger2
