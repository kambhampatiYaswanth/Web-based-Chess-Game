from .piece import Piece

class Knight(Piece):
    def symbol(self):
        return "N" if self.color == "WHITE" else "n"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        knight_moves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1),
        ]

        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if board.is_inside_board(r, c):
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))

        return moves
