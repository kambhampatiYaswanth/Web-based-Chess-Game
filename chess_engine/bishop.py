from .piece import Piece

class Bishop(Piece):
    def symbol(self):
        return "B" if self.color == "WHITE" else "b"

    def get_legal_moves(self, board, position):
        moves = []
        row, col = position

        directions = [
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1),    # down-right
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
