"""Tests for Combat Narrator."""

import pytest
from src.combat.combat_narrator import (
    CombatNarrator,
    CombatVerbosity,
    create_narrator,
)


class TestCombatNarrator:
    """Test combat narration generation."""

    @pytest.fixture
    def narrator(self):
        """Create a normal verbosity narrator."""
        return CombatNarrator(verbosity=CombatVerbosity.NORMAL)

    @pytest.fixture
    def brief_narrator(self):
        """Create a brief verbosity narrator."""
        return CombatNarrator(verbosity=CombatVerbosity.BRIEF)

    @pytest.fixture
    def verbose_narrator(self):
        """Create a verbose verbosity narrator."""
        return CombatNarrator(verbosity=CombatVerbosity.VERBOSE)

    def test_narrate_player_hit_normal(self, narrator):
        """Test normal hit narration."""
        text = narrator.narrate_player_hit(8, "goblin")
        assert "goblin" in text
        assert "8" in text
        assert "hit" in text.lower()

    def test_narrate_player_critical_normal(self, narrator):
        """Test critical hit narration."""
        text = narrator.narrate_player_critical(16, "orc")
        assert "or" in text.lower()
        assert "16" in text
        assert "critical" in text.lower()

    def test_narrate_player_miss_normal(self, narrator):
        """Test miss narration."""
        text = narrator.narrate_player_miss("goblin")
        assert "goblin" in text
        assert "miss" in text.lower()

    def test_narrate_enemy_hit_normal(self, narrator):
        """Test enemy hit narration."""
        text = narrator.narrate_enemy_hit(6, "goblin")
        assert "goblin" in text
        assert "6" in text
        assert "hit" in text.lower()

    def test_narrate_enemy_critical_normal(self, narrator):
        """Test enemy critical hit narration."""
        text = narrator.narrate_enemy_critical(12, "dragon")
        assert "dragon" in text
        assert "12" in text
        assert "critical" in text.lower()

    def test_narrate_enemy_miss_normal(self, narrator):
        """Test enemy miss narration."""
        text = narrator.narrate_enemy_miss("goblin")
        assert "goblin" in text
        assert "dodge" in text.lower() or "miss" in text.lower()

    def test_narrate_combat_intro(self, narrator):
        """Test combat intro."""
        text = narrator.narrate_combat_intro("Dragon")
        assert "Dragon" in text

    def test_narrate_combat_end_victory(self, narrator):
        """Test combat end victory."""
        text = narrator.narrate_combat_end("Goblin King", survived=True)
        assert "defeated" in text.lower() or "Goblin King" in text

    def test_narrate_combat_end_defeat(self, narrator):
        """Test combat end defeat."""
        text = narrator.narrate_combat_end("Goblin", survived=False)
        assert "defeated" in text.lower()

    def test_narrate_health_status(self, narrator):
        """Test health status."""
        text = narrator.narrate_health_status(10, 20, "Goblin", 5, 15)
        assert "10" in text
        assert "20" in text
        assert "5" in text
        assert "15" in text

    def test_narrate_attack_roll_hit(self, narrator):
        """Test attack roll narration (hit)."""
        text = narrator.narrate_attack_roll(15, 20, 12)
        assert "15" in text
        assert "20" in text
        assert "HIT" in text

    def test_narrate_attack_roll_miss(self, narrator):
        """Test attack roll narration (miss)."""
        text = narrator.narrate_attack_roll(5, 8, 15)
        assert "5" in text
        assert "8" in text
        assert "MISS" in text

    def test_narrate_attack_roll_critical(self, narrator):
        """Test attack roll narration (critical)."""
        text = narrator.narrate_attack_roll(20, 25, 10, is_critical=True)
        assert "20" in text
        assert "CRITICAL" in text

    def test_verbosity_brief(self, brief_narrator):
        """Test brief verbosity."""
        text = brief_narrator.narrate_player_hit(8, "goblin")
        assert len(text) < 30

    def test_verbosity_verbose(self, verbose_narrator):
        """Test verbose verbosity."""
        text = verbose_narrator.narrate_player_hit(8, "goblin")
        assert len(text) > 20

    def test_damage_type_fire(self, verbose_narrator):
        """Test fire damage type verb."""
        text = verbose_narrator.narrate_player_hit(10, "troll", damage_type="fire")
        assert "engulf" in text.lower() or "fire" in text.lower() or "burn" in text.lower()

    def test_damage_type_slashing(self, verbose_narrator):
        """Test slashing damage type verb."""
        text = verbose_narrator.narrate_player_hit(8, "orc", damage_type="slashing")
        assert "slash" in text.lower() or "slice" in text.lower()


class TestCreateNarrator:
    """Test the narrator factory function."""

    def test_create_default(self):
        """Test creating narrator with defaults."""
        narrator = create_narrator()
        assert narrator.verbosity == CombatVerbosity.NORMAL

    def test_create_brief(self):
        """Test creating brief narrator."""
        narrator = create_narrator("brief")
        assert narrator.verbosity == CombatVerbosity.BRIEF

    def test_create_verbose(self):
        """Test creating verbose narrator."""
        narrator = create_narrator("verbose")
        assert narrator.verbosity == CombatVerbosity.VERBOSE

    def test_create_invalid_verbosity(self):
        """Test creating narrator with invalid verbosity falls back to normal."""
        narrator = create_narrator("invalid")
        assert narrator.verbosity == CombatVerbosity.NORMAL
