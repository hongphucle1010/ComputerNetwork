import hashlib
from log import download_logger
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from Modules.PeerConnection.torrent import Torrent


class Piece:
    def __init__(
        self,
        index: int,
        hash: str,
        size: int,
        torrent: "Torrent",
        file_name: str = None,
    ):
        self.index = index
        self.hash = hash
        self.size = size
        self.downloaded = False
        self.torrent: "Torrent" = torrent
        self.file_name = file_name

    def setTorrent(self, torrent: "Torrent"):
        self.torrent = torrent
        self.setIsDownloaded(self.downloaded or self.verifyDownload())

    def setIsDownloaded(self, downloaded: bool):
        if downloaded:
            self.downloaded = downloaded
            self.torrent.downloaded_pieces += 1

    def getFileName(self):
        return f"{self.torrent.torrent_id}_{self.file_name}_{self.index}.dat"

    def setData(self, data: bytes):
        # Save data to file, path: /pieces/{torrent_id}_{index}.dat
        with open(f"pieces/{self.getFileName()}", "wb") as f:
            f.write(data)
        download_logger.logger.info(
            f"Saved piece {self.getFileName()} with hash {self.hash}"
        )
        self.setIsDownloaded(self.verifyDownload())

    def deleteData(self):
        try:
            os.remove(f"pieces/{self.getFileName()}")
        except FileNotFoundError:
            pass

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
        download_logger.logger.info(
            f"Verifying piece {self.getFileName()} with hash {self.hash}"
        )
        return self.verifyIntegrity()

    def to_dict(self):
        return {
            "index": self.index,
            "hash": self.hash,
            "size": self.size,
            "filename": self.file_name,
            "downloaded": self.downloaded,
        }

    @staticmethod
    def from_dict(piece_dict, torrent: "Torrent") -> "Piece":
        piece = Piece(
            index=piece_dict["index"],
            hash=piece_dict["hash"],
            size=piece_dict["size"],
            torrent=torrent,
            file_name=piece_dict["filename"],
        )
        piece.downloaded = (
            piece_dict["downloaded"] if "downloaded" in piece_dict else False
        )
        return piece

    @staticmethod
    def convertPieceArrayToDictArray(pieces):
        return [piece.to_dict() for piece in pieces]
