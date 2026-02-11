# AI Dungeon Chronicles

A narrative D&D interactive fiction game combining D&D 5th Edition mechanics with story-driven gameplay. Built with Python and Textual TUI.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Textual](https://img.shields.io/badge/textual-4.x-purple)
![License](https://img.shields.io/badge/license-MIT-green)

<div align="center">
  <a href="https://bit.ly/49t6aTh">
    <img src="docs/minimax-banner.png" alt="Get 12% Discount Coding Plan" width="100%">
  </a>
  
  **[Get 12% Discount →](https://bit.ly/49t6aTh)**
</div>

## Features

- **Narrative-Driven Story**: Branching story scenes with choices and consequences
- **D&D 5e Mechanics**: Skill checks, dice rolls, attribute modifiers
- **Character Creation**: Choose class and race for your adventurer
- **Save/Load System**: Compressed narrative saves
- **Multiple Endings**: Your choices determine how the story concludes

## Installation

```bash
# Clone the repository
git clone https://github.com/naufaldi/dnd-hybrid.git
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
| `1-9` or letter shortcuts | Select choice |
| `s` | Save game |
| `escape` | Back to menu |
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

### Narrative Gameplay

- Read scene descriptions and choose your path
- Skill checks use d20 + ability modifier
- Natural 20 = critical success
- Natural 1 = automatic failure
- Your choices affect the story and lead to different endings

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
2. **Narrative Layer** - Scene manager, endings, story flow
3. **Character Layer** - Attributes, skill checks
4. **Persistence Layer** - Save/load with compression

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
