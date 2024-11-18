import os
import hashlib


class FilePiece:
    def __init__(self, index: int, data: bytes, size: int):
        self.index = index
        self.size = size
        self.data = data
        self.hash = FilePiece.hash(data)

    @staticmethod
    def hash(data: bytes) -> str:
        return hashlib.sha1(data).digest().hex()

    def to_dict(self):
        return {
            "index": self.index,
            "size": self.size,
            "hash": self.hash,
        }

    def save(self, torrent_id: str, file_name: str):
        with open(f"pieces/{torrent_id}_{file_name}_{self.index}.dat", "wb") as f:
            f.write(self.data)
            f.close()


class File:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pieces: list[FilePiece] = []

    def to_dict(self):
        return {
            "filename": self.file_name,
            "size": self.file_size,
            "pieces": [piece.to_dict() for piece in self.pieces],
        }

    def split_into_pieces(self, piece_size: int):
        with open(self.file_path, "rb") as f:
            index = -1
            while True:
                index += 1
                piece = f.read(piece_size)
                if not piece:
                    break
                self.pieces.append(FilePiece(index, piece, piece_size))
            f.close()

    def save(self, torrent_id: str):
        for piece in self.pieces:
            piece.save(torrent_id, self.file_name)

    @property
    def file_name(self):
        return os.path.basename(self.file_path)

    @property
    def file_size(self):
        return os.path.getsize(self.file_path)
