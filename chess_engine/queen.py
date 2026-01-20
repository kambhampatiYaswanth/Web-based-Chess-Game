from .piece import Piece

class Queen(Piece):
    def symbol(self):
        return "Q" if self.color == "WHITE" else "q"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        directions = [
            # Rook-like directions
            (-1, 0), (1, 0), (0, -1), (0, 1),
            # Bishop-like directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_inside_board(r, c):
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc

        return moves
