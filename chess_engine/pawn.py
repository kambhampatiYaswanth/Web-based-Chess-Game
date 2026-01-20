from chess_engine import board
from .piece import Piece

class Pawn(Piece):
    def symbol(self):
        return "P" if self.color == "WHITE" else "p"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        direction = -1 if self.color == "WHITE" else 1
        start_row = 6 if self.color == "WHITE" else 1
    # Forward move (1 step)
        one_step = row + direction
        if board.is_inside_board(one_step, col) and board.get_piece(one_step, col) is None:
            moves.append((one_step, col))

        # First move (2 steps)
            two_step = row + 2 * direction
            if row == start_row and board.get_piece(two_step, col) is None:
                moves.append((two_step, col))

    # Diagonal captures
        for dc in [-1, 1]:
            diag_row = row + direction
            diag_col = col + dc

            if board.is_inside_board(diag_row, diag_col):
                target = board.get_piece(diag_row, diag_col)
                if target is not None and target.color != self.color:
                    moves.append((diag_row, diag_col))

        return moves
