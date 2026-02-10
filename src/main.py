"""Main entry point for D&D Roguelike."""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Main entry point."""
    try:
        from src.tui.app import DNDRoguelikeApp
        from src.core.config import config

        # Ensure directories exist
        config.ensure_directories()

        # Run the TUI app
        app = DNDRoguelikeApp()
        app.run()

    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
