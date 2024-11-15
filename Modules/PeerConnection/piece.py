import hashlib


class Piece:
    def __init__(self, index: int, hash: str, size: int):
        self.index = index
        self.hash = hash
        self.size = size
        self.data = None
        self.downloaded = False

    def setData(self, data: bytes):
        self.data = data
        self.downloaded = True

    def verifyIntegrity(self):
        return hashlib.sha1(self.data).hexdigest() == self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "hash": self.hash,
            "size": self.size,
            "downloaded": self.downloaded,
        }

    @staticmethod
    def from_dict(piece_dict):
        piece = Piece(
            piece_dict["index"],
            piece_dict["hash"],
            piece_dict["size"],
        )
        piece.data = piece_dict["data"]
        piece.downloaded = piece_dict["downloaded"]
        return piece
