# ============================================================
# main.py
# Entry point for Monkey Running Adventure Game
# Run this file to start the game: python main.py
# ============================================================

from src.game import Game


def main():
    """Create a Game instance and start the game loop."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
