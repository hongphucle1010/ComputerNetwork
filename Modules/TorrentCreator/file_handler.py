import os


class FileHandler:
    def __init__(self, file_path, piece_size):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.piece_size = piece_size
        self.pieces = []

    def splitIntoPieces(self):
        index = 0
        with open(self.file_path, "rb") as f:
            while True:
                piece = f.read(self.piece_size)
                if not piece:
                    break
                self.pieces.append({
                    "index": index,
                    "size": self.piece_size,
                    "data": piece
                })
