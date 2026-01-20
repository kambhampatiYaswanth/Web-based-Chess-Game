from .piece import Piece

class Rook(Piece):
    def symbol(self):
        return "R" if self.color == "WHITE" else "r"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        directions = [
            (-1, 0),  # up
            (1, 0),   # down
            (0, -1),  # left
            (0, 1)    # right
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
