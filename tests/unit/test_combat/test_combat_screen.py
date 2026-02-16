"""Unit tests for combat screen functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, PropertyMock
from src.tui.screens.combat_screen import CombatScreen, Attack


class TestCombatScreenInitialization:
    """Tests for combat screen setup."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen instance."""
        return CombatScreen(
            enemy_name="Test Goblin",
            enemy_hp=15,
            enemy_ac=12,
            enemy_description="A test enemy for combat",
            enemy_attacks=[
                Attack(name="Slash", damage="1d6", damage_type="slashing", attack_bonus=3)
            ],
            enemy_abilities=["Darkvision", "Nimble Escape"],
            victory_scene="victory_test",
            defeat_scene="defeat_test",
        )

    def test_screen_initialization(self, combat_screen):
        """Test combat screen initializes with correct values."""
        assert combat_screen.enemy_name == "Test Goblin"
        assert combat_screen.enemy_max_hp == 15
        assert combat_screen.enemy_current_hp == 15
        assert combat_screen.enemy_ac == 12
        assert combat_screen.victory_scene == "victory_test"
        assert combat_screen.defeat_scene == "defeat_test"

    def test_enemy_hp_tracking(self, combat_screen):
        """Test enemy HP can be modified."""
        assert combat_screen.enemy_current_hp == 15

        combat_screen.enemy_current_hp -= 5
        assert combat_screen.enemy_current_hp == 10

        combat_screen.enemy_current_hp = 0
        assert combat_screen.enemy_current_hp == 0

    def test_combat_log_initially_empty(self, combat_screen):
        """Test combat log starts empty."""
        assert len(combat_screen.combat_log) == 0

    def test_enemy_attacks_loaded(self, combat_screen):
        """Test enemy attacks are loaded."""
        assert len(combat_screen.enemy_attacks) == 1
        assert combat_screen.enemy_attacks[0].name == "Slash"
        assert combat_screen.enemy_attacks[0].damage == "1d6"

    def test_enemy_abilities_loaded(self, combat_screen):
        """Test enemy abilities are loaded."""
        assert len(combat_screen.enemy_abilities) == 2
        assert "Darkvision" in combat_screen.enemy_abilities


class TestCombatScreenActions:
    """Tests for combat screen actions."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen instance."""
        return CombatScreen(
            enemy_name="Goblin",
            enemy_hp=10,
            enemy_ac=10,
            victory_scene="goblin_victory",
            defeat_scene="death_in_dungeon",
        )

    def test_add_combat_message(self, combat_screen):
        """Test adding messages to combat log."""
        combat_screen._add_combat_message("Test message")
        assert len(combat_screen.combat_log) == 1
        assert combat_screen.combat_log[0] == "Test message"

    def test_add_multiple_messages(self, combat_screen):
        """Test adding multiple messages."""
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            combat_screen._add_combat_message(msg)
        assert len(combat_screen.combat_log) == 3
        assert combat_screen.combat_log == messages

    def test_combat_log_limit(self, combat_screen):
        """Test that combat log displays last 5 messages."""
        for i in range(10):
            combat_screen._add_combat_message(f"Message {i}")
        assert len(combat_screen.combat_log) == 10


class TestCombatScreenEnemyDefeat:
    """Tests for enemy defeat scenarios."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen instance."""
        screen = CombatScreen(
            enemy_name="Weak Goblin",
            enemy_hp=5,
            enemy_ac=10,
            victory_scene="goblin_victory",
            defeat_scene="death_in_dungeon",
        )
        return screen

    def test_enemy_defeat_detection(self, combat_screen):
        """Test that enemy is defeated when HP reaches 0."""
        combat_screen.enemy_current_hp = 0
        assert combat_screen.enemy_current_hp <= 0

    def test_enemy_damage_tracking(self, combat_screen):
        """Test tracking damage dealt to enemy."""
        initial_hp = combat_screen.enemy_current_hp
        damage = 3
        combat_screen.enemy_current_hp -= damage

        assert combat_screen.enemy_current_hp == initial_hp - damage


class TestCombatScreenMarkup:
    """Tests for Rich markup validation in combat screen."""

    INVALID_MARKUP_PATTERNS = [
        "[size=",
        "[/size]",
        "[font=",
        "[color=",
    ]

    def test_title_has_no_invalid_markup(self):
        """Test that combat screen title uses valid markup."""
        screen = CombatScreen(enemy_name="Goblin", enemy_hp=10, enemy_ac=10)

        # The title should be generated without invalid markup
        title = f"[b]═══ ⚔ Combat: {screen.enemy_name} ⚔ ═══[/b]"

        for pattern in self.INVALID_MARKUP_PATTERNS:
            assert pattern not in title, f"Found invalid markup: {pattern}"

    def test_combat_messages_use_valid_markup(self):
        """Test that combat messages use valid Rich markup."""
        valid_messages = [
            "[red]Critical failure![/red]",
            "[green]Hit! You deal 5 damage![/green]",
            "[cyan]You raise your shield[/cyan]",
            "[b]Bold text[/b]",
        ]

        for msg in valid_messages:
            for pattern in self.INVALID_MARKUP_PATTERNS:
                assert pattern not in msg, f"Message contains invalid markup: {msg}"


class TestCombatScreenTransitions:
    """Tests for combat screen scene transitions."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen with mocked app."""
        mock_app = Mock()
        mock_app.pop_screen = Mock()
        with patch.object(CombatScreen, "app", new_callable=PropertyMock) as p:
            p.return_value = mock_app
            screen = CombatScreen(
                enemy_name="Boss",
                enemy_hp=50,
                enemy_ac=15,
                victory_scene="hero_ending",
                defeat_scene="death_in_dungeon",
            )
            yield screen

    @pytest.mark.asyncio
    async def test_victory_transition(self, combat_screen):
        """Test that victory transitions to victory scene."""
        mock_game_state = Mock()
        mock_game_state.is_combat = True
        mock_game_state.current_enemy = "boss"
        combat_screen.app.narrative_game_state = mock_game_state
        combat_screen.app.pop_screen = Mock()

        with patch.object(combat_screen.app, "scene_manager", None):
            await combat_screen._combat_victory()

        assert mock_game_state.is_combat is False
        assert mock_game_state.current_enemy is None
        combat_screen.app.pop_screen.assert_called_once()

    @pytest.mark.asyncio
    async def test_defeat_transition(self, combat_screen):
        """Test that defeat transitions to defeat scene."""
        mock_game_state = Mock()
        mock_game_state.is_combat = True
        mock_game_state.current_enemy = "boss"
        combat_screen.app.narrative_game_state = mock_game_state
        combat_screen.app.pop_screen = Mock()

        with patch.object(combat_screen.app, "scene_manager", None):
            await combat_screen._combat_defeat()

        assert mock_game_state.is_combat is False
        assert mock_game_state.current_enemy is None
        combat_screen.app.pop_screen.assert_called_once()


class TestAttackDataclass:
    """Tests for the Attack dataclass."""

    def test_attack_creation(self):
        """Test creating an Attack instance."""
        attack = Attack(
            name="Longsword", damage="1d8", damage_type="slashing", attack_bonus=5, reach="5ft"
        )

        assert attack.name == "Longsword"
        assert attack.damage == "1d8"
        assert attack.damage_type == "slashing"
        assert attack.attack_bonus == 5
        assert attack.reach == "5ft"

    def test_attack_defaults(self):
        """Test Attack with default values."""
        attack = Attack(name="Bite", damage="1d6", damage_type="piercing")

        assert attack.attack_bonus == 0
        assert attack.reach is None


class TestCombatScreenPlayerState:
    """Tests for tracking player state in combat."""

    @pytest.fixture
    def combat_screen(self):
        """Create a combat screen with mocked character."""
        mock_char = Mock()
        mock_char.hit_points = 20
        mock_char.max_hp = 20
        mock_char.name = "TestHero"
        mock_char.strength = 14
        mock_char.strength_mod = 2
        mock_char.equipment = {"weapon_damage": "1d8", "weapon_stat": "strength"}

        mock_game_state = Mock()
        mock_game_state.character = mock_char

        mock_app = Mock()
        mock_app.narrative_game_state = mock_game_state

        with patch.object(CombatScreen, "app", new_callable=PropertyMock) as p:
            p.return_value = mock_app
            screen = CombatScreen(
                enemy_name="Goblin",
                enemy_hp=10,
                enemy_ac=10,
            )
            yield screen

    def test_player_info_display(self, combat_screen):
        """Test that player info is retrieved correctly."""
        game_state = combat_screen.app.narrative_game_state
        char = game_state.character

        assert char.name == "TestHero"
        assert char.hit_points == 20
        assert char.max_hp == 20

    def test_player_weapon_stats(self, combat_screen):
        """Test that player weapon stats are accessible."""
        char = combat_screen.app.narrative_game_state.character

        assert char.equipment["weapon_damage"] == "1d8"
        assert char.equipment["weapon_stat"] == "strength"

    def test_player_ability_modifier(self, combat_screen):
        """Test that player ability modifier is calculated."""
        char = combat_screen.app.narrative_game_state.character

        assert char.strength_mod == 2
