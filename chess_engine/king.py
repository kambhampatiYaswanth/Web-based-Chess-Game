from .piece import Piece

class King(Piece):
    def symbol(self):
        return "K" if self.color == "WHITE" else "k"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if board.is_inside_board(r, c):
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))

        return moves
