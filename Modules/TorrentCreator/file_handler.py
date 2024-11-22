import os
import hashlib


class FilePiece:
    def __init__(self, index: int, data: bytes, size: int, filename: str):
        self.index = index
        self.size = size
        self.filename = filename
        self.hash = FilePiece.hash(data)
        self.save(data)

    @staticmethod
    def hash(data: bytes) -> str:
        return hashlib.sha1(data).digest().hex()

    def to_dict(self):
        return {
            "index": self.index,
            "size": self.size,
            "hash": self.hash,
        }

    def save(self, data: bytes):
        with open(f"pieces/temp_{self.filename}_{self.index}.dat", "wb") as f:
            f.write(data)
            f.close()

    def rename(self, torrent_id: str):
        os.rename(
            f"pieces/temp_{self.filename}_{self.index}.dat",
            f"pieces/{torrent_id}_{self.filename}_{self.index}.dat",
        )


class File:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pieces: list[FilePiece] = []
        self._stop = False
        self.progress = 0  # Progress percentage for this file

    def stop(self):
        self._stop = True

    def to_dict(self):
        return {
            "filename": self.file_name,
            "size": self.file_size,
            "pieces": [piece.to_dict() for piece in self.pieces],
        }

    def split_into_pieces(self, piece_size: int, progress_callback=None):
        total_size = self.file_size
        processed_size = 0
        with open(self.file_path, "rb") as f:
            index = -1
            while True:
                if self._stop:
                    break
                index += 1
                piece = f.read(piece_size)
                if not piece:
                    break
                self.pieces.append(FilePiece(index, piece, piece_size, self.file_name))
                processed_size += len(piece)
                self.progress = (processed_size / total_size) * 100
                if progress_callback:
                    progress_callback(len(piece))
        self._stop = False  # Reset the stop flag after stopping

    def save(self, torrent_id: str):
        for piece in self.pieces:
            piece.rename(torrent_id)

    @property
    def file_name(self):
        return os.path.basename(self.file_path)

    @property
    def file_size(self):
        return os.path.getsize(self.file_path)
