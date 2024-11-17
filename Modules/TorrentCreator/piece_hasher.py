import hashlib


class PieceHasher:
    def __init__(self):
        self.pieceHashes = []

    @staticmethod
    def generateHashes(piece):
        return hashlib.sha1(piece).digest()  # Hash SHA-1, chưa chắc đúng nha

    def generateAllHashes(self, pieces):
        for piece in pieces:
            self.pieceHashes.append(
                {
                    "index": piece["index"],
                    "size": piece["size"],
                    "hash": PieceHasher.generateHashes(piece["data"]).hex(),
                }
            )
        return self.pieceHashes
