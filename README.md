# D&D Roguelike Hybrid

A roguelike CLI game combining D&D 5th Edition mechanics with procedural dungeon generation. Built with Python and Textual TUI.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Textual](https://img.shields.io/badge/textual-4.x-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **D&D 5e Mechanics**: Full attribute system, combat resolution, proficiency bonuses, critical hits
- **Procedural Dungeons**: BSP-based room generation with connected corridors
- **Turn-Based Combat**: Strategic combat with initiative, attacks, and damage
- **Field of View**: Shadow casting visibility system
- **Save/Load System**: Compressed game saves with SQLite backend
- **ASCII Graphics**: Classic roguelike visuals in the terminal

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dnd-hybrid.git
cd dnd-hybrid

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python -m src.main
```

## Requirements

- Python 3.10+
- textual >= 4.0.0
- pytest >= 9.0.0 (for testing)

## How to Play

### Controls

| Key | Action |
|-----|--------|
| `↑↓←→` or `nsew` | Move |
| `y u b j` | Diagonal movement |
| `.` or `space` | Wait (skip turn) |
| `,` or `g` | Pick up item |
| `i` | Open inventory |
| `c` | View character sheet |
| `l` | View game log |
| `s` | Save game |
| `escape` | Back/Menu |
| `q` | Quit |

### Character Creation

Choose from 4 classes:
- **Fighter** - Strong melee combatant
- **Wizard** - Spellcaster with magical abilities
- **Rogue** - Stealthy damage dealer
- **Cleric** - Healer with divine magic

And 4 races:
- **Human** - Versatile
- **Elf** - Agile and magical
- **Dwarf** - Tough and resilient
- **Halfling** - Lucky and stealthy

### Combat

- Attack rolls use d20 + ability modifier + proficiency
- Natural 20 = critical hit (double damage dice)
- Natural 1 = automatic miss
- Damage = weapon dice + ability modifier

### Progression

- Gain XP by defeating enemies (100 × CR)
- Level up at specific XP thresholds
- Each level increases HP and proficiency bonus

## Project Structure

```
src/
├── cli/           # Command parser, display
├── tui/           # Textual app, screens, widgets
├── core/          # Game engine, event bus, config
├── entities/      # Character, Enemy, Item classes
├── world/         # Dungeon generator, map, FOV, tiles
├── combat/        # Combat engine, dice, initiative
├── character/     # Attributes, inventory, equipment
├── persistence/   # Database, save manager
└── utils/        # Logger, exceptions
```

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Type checking
mypy src/ --strict

# Linting
ruff check src/

# Formatting
ruff format src/
```

## Architecture

The game follows a layered architecture:

1. **TUI Layer** - Textual widgets and screens
2. **Interface Bridge** - State sync and action queue
3. **Game Engine** - Core game loop and events
4. **World Manager** - Dungeon generation, FOV
5. **Combat Engine** - Attack resolution, initiative
6. **Persistence Layer** - Save/load with compression

## Known Issues

See [docs/bug.md](docs/bug.md) for documented bugs and fixes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [D&D 5e SRD](https://5thsrd.org/) for game mechanics reference
- [Textual](https://textual.textualize.io/) for the TUI framework
