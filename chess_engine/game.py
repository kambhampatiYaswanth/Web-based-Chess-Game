# game.py - CORRECTED VERSION
import random

class Game:
    def __init__(self):
        from .board import Board  # Import here to avoid circular imports
        self.board = Board()
        self.turn = "WHITE"
        self.move_history = []

    def switch_turn(self):
        self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

    def make_move(self, start, end):
        piece = self.board.get_piece(*start)

        if piece is None:
            raise Exception("No piece at selected square")

        if piece.color != self.turn:
            raise Exception("Not your turn")

        legal_moves = piece.get_legal_moves(self.board, start)
        if end not in legal_moves:
            raise Exception("Illegal move")

        captured = self.board.get_piece(*end)

        # simulate move
        self.board.grid[end[0]][end[1]] = piece
        self.board.grid[start[0]][start[1]] = None

        # king safety
        if self.board.is_king_in_check(piece.color):
            self.board.grid[start[0]][start[1]] = piece
            self.board.grid[end[0]][end[1]] = captured
            raise Exception("Move leaves king in check")
        
        # 🔥 PAWN PROMOTION CHECK
        if self.is_pawn_promotion(piece, end):
            return "PROMOTION"
        
        # --- MOVE HISTORY ---
        from_square = self.coord_to_notation(start)
        to_square = self.coord_to_notation(end)
        piece_name = piece.name()
        player = piece.color

        move_text = f"{player}: {piece_name} {from_square} → {to_square}"
        self.move_history.append(move_text)

        # finalize
        self.switch_turn()
        print("Turn switched to:", self.turn)

        return "OK"

    def has_any_legal_move(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == color:
                    start = (r, c)
                    for end in piece.get_legal_moves(self.board, start):
                        captured = self.board.get_piece(*end)

                        # simulate move
                        self.board.grid[end[0]][end[1]] = piece
                        self.board.grid[start[0]][start[1]] = None

                        in_check = self.board.is_king_in_check(color)

                        # undo
                        self.board.grid[start[0]][start[1]] = piece
                        self.board.grid[end[0]][end[1]] = captured

                        if not in_check:
                            return True
        return False

    def is_checkmate(self, color):
        # If king is not in check, it's not checkmate
        if not self.board.is_king_in_check(color):
            return False

        # Try every possible move for this color
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == color:
                    start = (r, c)
                    for end in piece.get_legal_moves(self.board, start):
                        captured = self.board.get_piece(*end)

                        # simulate move
                        self.board.grid[end[0]][end[1]] = piece
                        self.board.grid[start[0]][start[1]] = None

                        still_in_check = self.board.is_king_in_check(color)

                        # undo move
                        self.board.grid[start[0]][start[1]] = piece
                        self.board.grid[end[0]][end[1]] = captured

                        # if ANY move escapes check → not checkmate
                        if not still_in_check:
                            return False

        # No escape found
        return True
    
    def coord_to_notation(self, position):
        row, col = position
        file = chr(ord('a') + col)
        rank = 8 - row
        return f"{file}{rank}"

    def is_pawn_promotion(self, piece, end):
        if piece.name() != "Pawn":
            return False

        row, _ = end
        if piece.color == "WHITE" and row == 0:
            return True
        if piece.color == "BLACK" and row == 7:
            return True
        return False

    def get_all_legal_moves(self, color):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == color:
                    start = (r, c)
                    for end in piece.get_legal_moves(self.board, start):
                        # simulate
                        captured = self.board.get_piece(*end)
                        self.board.grid[end[0]][end[1]] = piece
                        self.board.grid[start[0]][start[1]] = None

                        if not self.board.is_king_in_check(color):
                            moves.append((start, end))

                        # undo
                        self.board.grid[start[0]][start[1]] = piece
                        self.board.grid[end[0]][end[1]] = captured
        return moves

    def make_ai_move(self):
        """Improved AI with better decision making"""
        print(f"\n{'='*50}")
        print("AI (BLACK) THINKING...")
        print(f"{'='*50}")
        
        # Get all legal moves
        moves = self.get_all_legal_moves("BLACK")
        
        if not moves:
            print("No legal moves for AI!")
            return False
        
        print(f"Found {len(moves)} legal moves")
        
        # Piece values for evaluation
        piece_values = {
            "Pawn": 1, "Knight": 3, "Bishop": 3, 
            "Rook": 5, "Queen": 9, "King": 100
        }
        
        # Evaluate each move
        scored_moves = []
        for start, end in moves:
            score = 0
            
            # 1. Capture evaluation
            target = self.board.get_piece(*end)
            if target:
                target_value = piece_values.get(target.name(), 0)
                score += target_value * 10  # Big bonus for captures
            
            # 2. Center control bonus
            center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
            if end in center_squares:
                score += 3
            
            # 3. Development bonus (move pieces out)
            piece = self.board.get_piece(*start)
            if piece and piece.name() in ["Knight", "Bishop"]:
                if start[0] == 0:  # Starting rank for black
                    score += 2
            
            # 4. Pawn advancement bonus
            if piece and piece.name() == "Pawn":
                if end[0] > start[0]:  # Moving forward (black moves downward)
                    score += 1
            
            # 5. Check bonus
            # Simulate move to see if it gives check
            captured = self.board.get_piece(*end)
            self.board.grid[end[0]][end[1]] = piece
            self.board.grid[start[0]][start[1]] = None
            
            if self.board.is_king_in_check("WHITE"):
                score += 5  # Bonus for giving check
            
            # Undo simulation
            self.board.grid[start[0]][start[1]] = piece
            self.board.grid[end[0]][end[1]] = captured
            
            scored_moves.append((score, (start, end)))
            print(f"Move {start}->{end}: score={score}")
        
        # Sort by score (highest first)
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        
        # Pick the best move (with some randomness for top moves)
        if len(scored_moves) > 3:
            top_moves = scored_moves[:3]  # Consider top 3 moves
            import random
            best_score, best_move = random.choice(top_moves)
        else:
            best_score, best_move = scored_moves[0]
        
        print(f"\nSelected move: {best_move} with score {best_score}")
        
        # Execute the move
        try:
            start, end = best_move
            result = self.make_move(start, end)
            
            # Handle promotion
            if result == "PROMOTION":
                from .queen import Queen
                self.board.grid[end[0]][end[1]] = Queen("BLACK")
                print("Promoted pawn to Queen")
            
            print(f"AI move successful. New turn: {self.turn}")
            print(f"{'='*50}\n")
            return True
            
        except Exception as e:
            print(f"Best move failed: {e}")
            # Fallback to first legal move
            for start, end in moves:
                try:
                    self.make_move(start, end)
                    print(f"Fallback move: {start}->{end}")
                    return True
                except:
                    continue
            
            return False

    def simulate_move(self, start, end):
        piece = self.board.get_piece(*start)
        captured = self.board.get_piece(*end)

        self.board.grid[end[0]][end[1]] = piece
        self.board.grid[start[0]][start[1]] = None

        return captured
    
    def undo_simulated_move(self, start, end, captured):
        piece = self.board.get_piece(*end)
        self.board.grid[start[0]][start[1]] = piece
        self.board.grid[end[0]][end[1]] = captured