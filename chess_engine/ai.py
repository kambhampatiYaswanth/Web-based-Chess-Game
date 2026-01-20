# ai.py - SIMPLE BUT WORKING AI
import random

PIECE_VALUES = {
    "p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 100
}

def get_all_legal_moves(game_state, color):
    """Get ALL legal moves for a color"""
    moves = []
    
    for r in range(8):
        for c in range(8):
            piece = game_state.board.grid[r][c]
            if piece and piece.color == color:
                start = (r, c)
                # Get moves from piece's get_legal_moves method
                piece_moves = piece.get_legal_moves(game_state.board, start)
                
                for end in piece_moves:
                    # Simulate move to check if king is safe
                    captured = game_state.board.grid[end[0]][end[1]]
                    
                    # Make move
                    game_state.board.grid[end[0]][end[1]] = piece
                    game_state.board.grid[start[0]][start[1]] = None
                    
                    # Check if king is in check
                    king_in_check = game_state.board.is_king_in_check(color)
                    
                    # Undo move
                    game_state.board.grid[start[0]][start[1]] = piece
                    game_state.board.grid[end[0]][end[1]] = captured
                    
                    if not king_in_check:
                        moves.append((start, end))
    
    return moves

def evaluate_move(game_state, start, end, color):
    """Evaluate how good a move is"""
    score = 0
    
    piece = game_state.board.grid[start[0]][start[1]]
    target = game_state.board.grid[end[0]][end[1]]
    
    # 1. Capture score (most important)
    if target:
        target_symbol = target.symbol().lower()
        if target_symbol in PIECE_VALUES:
            score += PIECE_VALUES[target_symbol] * 100
    
    # 2. Piece development (encourage moving pieces out)
    piece_symbol = piece.symbol().lower()
    
    # For knights and bishops, encourage moving from starting position
    if piece_symbol in ['n', 'b']:
        if color == "BLACK":
            # Black knights/bishops start on row 0
            if start[0] == 0:
                score += 10
    
    # 3. Center control for pawns
    if piece_symbol == 'p':
        # Encourage pawns to move toward center
        center_files = [3, 4]  # d and e files
        if end[1] in center_files:
            score += 5
        
        # Encourage advancing pawns
        if color == "BLACK":  # Black moves downward (increasing row)
            if end[0] > start[0]:  # Moving forward
                score += 2
    
    # 4. King safety (discourage moving king early)
    if piece_symbol == 'k':
        score -= 20  # Penalize moving king unless necessary
    
    # 5. Check if move gives check
    # Simulate move
    captured = game_state.board.grid[end[0]][end[1]]
    game_state.board.grid[end[0]][end[1]] = piece
    game_state.board.grid[start[0]][start[1]] = None
    
    opponent_color = "WHITE" if color == "BLACK" else "BLACK"
    gives_check = game_state.board.is_king_in_check(opponent_color)
    
    # Undo
    game_state.board.grid[start[0]][start[1]] = piece
    game_state.board.grid[end[0]][end[1]] = captured
    
    if gives_check:
        score += 50  # Bonus for giving check
    
    return score
# ai.py - SIMPLE WORKING VERSION
"""
Simple AI module for chess.
Note: The main AI logic is now in game.py's make_ai_move method.
This file is kept for compatibility.
"""

def find_best_move(game_state, depth=1):
    """Simple AI - picks first legal capture, otherwise random move"""
    # Get all legal moves
    moves = game_state.get_all_legal_moves("BLACK")
    
    if not moves:
        return None
    
    # Try to find a capture
    import random
    
    capturing_moves = []
    for start, end in moves:
        target = game_state.board.get_piece(*end)
        if target:
            capturing_moves.append((start, end))
    
    if capturing_moves:
        # Return a random capture
        return random.choice(captaining_moves)
    
    # Return a random move
    return random.choice(moves)

def find_simple_move(game_state):
    """Even simpler - just random move"""
    moves = game_state.get_all_legal_moves("BLACK")
    import random
    return random.choice(moves) if moves else None