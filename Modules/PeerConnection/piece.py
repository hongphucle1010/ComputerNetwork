import hashlib


class Piece:
    def __init__(self, index: int, hash: str, size: int, torrent_id: str = None):
        self.index = index
        self.hash = hash
        self.size = size
        self.downloaded = False
        self.torrent_id = torrent_id

    def getFileName(self):
        return f"{self.torrent_id}_{self.index}.dat"

    def setData(self, data: bytes):
        # Save data to file, path: /pieces/{torrent_id}_{index}.dat
        with open(f"pieces/{self.getFileName()}", "wb") as f:
            f.write(data)
        self.downloaded = True

    def getData(self):
        # Load data from file, path: /pieces/{torrent_id}_{index}.dat
        with open(f"pieces/{self.getFileName()}", "rb") as f:
            return f.read()

    def verifyIntegrity(self):
        return hashlib.sha1(self.getData()).hexdigest() == self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "hash": self.hash,
            "size": self.size,
            "downloaded": self.downloaded,
        }

    @staticmethod
    def from_dict(piece_dict, torrent_id):
        piece = Piece(
            piece_dict["index"], piece_dict["hash"], piece_dict["size"], torrent_id
        )
        piece.downloaded = (
            piece_dict["downloaded"] if "downloaded" in piece_dict else False
        )
        return piece

    @staticmethod
    def convertPieceArrayToDictArray(pieces):
        return [piece.to_dict() for piece in pieces]
