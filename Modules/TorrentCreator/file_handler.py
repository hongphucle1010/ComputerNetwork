import os


class FileHandler:
    def __init__(self, file_path, piece_size):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.piece_size = piece_size
        self.pieces = []

    def splitIntoPieces(self):
        index = -1
        with open(self.file_path, "rb") as f:
            while True:
                index += 1
                piece = f.read(self.piece_size)
                if not piece:
                    break
                self.pieces.append(
                    {"index": index, "size": self.piece_size, "data": piece}
                )

    def savePieces(self, torrent_id: str):
        for piece in self.pieces:
            print(f"Save to pieces/{torrent_id}_{piece['index']}.dat")
            with open(f"pieces/{torrent_id}_{piece['index']}.dat", "wb") as f:
                f.write(piece["data"])
                f.close()
