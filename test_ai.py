# test_simple_ai.py
import sys
import os
sys.path.append('.')

from chess_engine.game import Game

def test_ai():
    print("Testing AI moves...")
    game = Game()
    
    # Display initial board
    print("\nInitial board:")
    for r in range(8):
        row = []
        for c in range(8):
            piece = game.board.get_piece(r, c)
            row.append(piece.symbol() if piece else '.')
        print(' '.join(row))
    
    print(f"\nTurn: {game.turn}")
    
    # Make a white move
    print("\n1. Making white move (e2 to e4)...")
    try:
        game.make_move((6, 4), (4, 4))
        print(f"Success! Turn is now: {game.turn}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try AI move
    print("\n2. Trying AI move...")
    try:
        success = game.make_ai_move()
        print(f"AI move success: {success}")
        print(f"Turn after AI: {game.turn}")
        
        print("\nBoard after AI move:")
        for r in range(8):
            row = []
            for c in range(8):
                piece = game.board.get_piece(r, c)
                row.append(piece.symbol() if piece else '.')
            print(' '.join(row))
            
    except Exception as e:
        print(f"AI error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai()