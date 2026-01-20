class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def symbol(self):
        raise NotImplementedError("symbol() not implemented")

    def get_legal_moves(self, board, position):
        return []
    def name(self):
        return self.__class__.__name__
