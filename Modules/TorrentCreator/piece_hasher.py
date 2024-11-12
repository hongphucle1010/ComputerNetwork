import hashlib


class PieceHasher:
    def __init__(self):
        self.pieceHashes = []

    def generateHashes(self, piece):
        return hashlib.sha1(piece).digest()  # Hash SHA-1, chưa chắc đúng nha

    def generateAllHashes(self, pieces):
        for piece in pieces:
            self.pieceHashes.append(self.generateHashes(piece))
        return self.pieceHashes
