import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chess_engine.game import Game
from chess_engine.ai import find_best_move

def test_ai():
    game = Game()
    print("Initial board:")
    game.board.display()
    
    print("\nLooking for AI move...")
    move = find_best_move(game, depth=2)
    
    if move:
        print(f"AI suggests: {move}")
        start, end = move
        try:
            result = game.make_move(start, end)
            print(f"Move result: {result}")
            print("\nBoard after AI move:")
            game.board.display()
        except Exception as e:
            print(f"Move failed: {e}")
    else:
        print("No move found!")

if __name__ == "__main__":
    test_ai()