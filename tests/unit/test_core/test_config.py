"""Tests for game config."""

from src.core.config import GameConfig, config


class TestGameConfigDefaults:
    def test_default_map_size(self):
        cfg = GameConfig()
        assert cfg.map_width == 80
        assert cfg.map_height == 24

    def test_default_tick_rate(self):
        cfg = GameConfig()
        assert cfg.tick_rate == 0.1

    def test_default_fov_radius(self):
        cfg = GameConfig()
        assert cfg.fov_radius == 8

    def test_default_room_sizes(self):
        cfg = GameConfig()
        assert cfg.min_room_size == 5
        assert cfg.max_room_size == 15


class TestGameConfigFromDict:
    def test_partial_override(self):
        cfg = GameConfig.from_dict({"map_width": 100, "debug": True})
        assert cfg.map_width == 100
        assert cfg.debug is True
        assert cfg.map_height == 24  # default

    def test_ignore_unknown_fields(self):
        cfg = GameConfig.from_dict({"unknown_field": "value"})
        assert cfg.map_width == 80  # unchanged


class TestConfigSingleton:
    def test_config_is_singleton(self):

        assert isinstance(config, GameConfig)
