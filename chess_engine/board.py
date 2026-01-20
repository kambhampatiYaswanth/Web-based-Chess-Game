from .pawn import Pawn
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen
from .king import King


class Board:
    def __init__(self):
        # 8x8 board, initially empty
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

    from .pawn import Pawn

    def setup_board(self):
    # White pawns
        for col in range(8):
            self.grid[6][col] = Pawn("WHITE")
    # Black pawns
        for col in range(8):
            self.grid[1][col] = Pawn("BLACK")

    # White rooks
        self.grid[7][0] = Rook("WHITE")
        self.grid[7][7] = Rook("WHITE")
    # Black rooks
        self.grid[0][0] = Rook("BLACK")
        self.grid[0][7] = Rook("BLACK")

    # White knights
        self.grid[7][1] = Knight("WHITE")
        self.grid[7][6] = Knight("WHITE")
    # Black knights
        self.grid[0][1] = Knight("BLACK")
        self.grid[0][6] = Knight("BLACK")

    # White bishops
        self.grid[7][2] = Bishop("WHITE")
        self.grid[7][5] = Bishop("WHITE")
    # Black bishops
        self.grid[0][2] = Bishop("BLACK")
        self.grid[0][5] = Bishop("BLACK")

    # White queen
        self.grid[7][3] = Queen("WHITE")
    # Black queen
        self.grid[0][3] = Queen("BLACK")

    # White king
        self.grid[7][4] = King("WHITE")

    # Black king
        self.grid[0][4] = King("BLACK")

    def is_inside_board(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, row, col):
        if not self.is_inside_board(row, col):
            return None
        return self.grid[row][col]

    def set_piece(self, row, col, piece):
        if self.is_inside_board(row, col):
            self.grid[row][col] = piece

    def move_piece(self, start, end):
        """
        start = (row, col)
        end   = (row, col)
        """
        piece = self.get_piece(*start)
        self.set_piece(*end, piece)
        self.set_piece(*start, None)
        piece.has_moved = True
    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.symbol().lower() == 'k' and piece.color == color:
                    return (r, c)
        return None
    def is_square_attacked(self, position, by_color):
        r, c = position

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == by_color:
                    moves = piece.get_legal_moves(self, (row, col))
                    if (r, c) in moves:
                        return True
        return False
    def is_king_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        enemy = "BLACK" if color == "WHITE" else "WHITE"
        return self.is_square_attacked(king_pos, enemy)