import hashlib


class Piece:
    def __init__(self, index: int, hash: str, size: int, torrent_id: str = None):
        self.index = index
        self.hash = hash
        self.size = size
        self.downloaded = False
        self.torrent_id = torrent_id
        self.verifyDownload()

    def getFileName(self):
        return f"{self.torrent_id}_{self.index}.dat"

    def setData(self, data: bytes):
        # Save data to file, path: /pieces/{torrent_id}_{index}.dat
        with open(f"pieces/{self.getFileName()}", "wb") as f:
            f.write(data)
        self.downloaded = True

    def getData(self):
        # Check if file exists. If not, return None.
        try:
            with open(f"pieces/{self.getFileName()}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def verifyIntegrity(self):
        data = self.getData()
        if data is None:
            return False
        return hashlib.sha1(data).hexdigest() == self.hash

    def verifyDownload(self):
        if self.verifyIntegrity():
            self.downloaded = True
            return True
        return False

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
