from Modules.PeerConnection.peer_manager import PeerManager
from configuration import Configuration
from Modules.PeerConnection.piece import Piece
import threading
import os
from typing import TYPE_CHECKING
from log import download_logger

if TYPE_CHECKING:
    from Modules.PeerConnection.torrent_manager import TorrentManager


class Torrent:
    def __init__(
        self,
        torrent_id: str,
        files: list[str],
        pieces: list[Piece],
        piece_size: int,
        tracker_url: str,
        configs: Configuration,
        torrent_manager: "TorrentManager",
        downloaded_path: list[str] = [],
        torrent_name: str = "",
    ):
        self.torrent_id = torrent_id
        self.files = files
        self.pieces = pieces
        self.piece_size = piece_size
        self.tracker_url = tracker_url
        self.configs = configs
        self.peer_manager = PeerManager(self, self.configs.max_connections)
        self.thread = None
        self.torrent_manager = torrent_manager
        self.downloaded_pieces = 0
        self.downloaded_path = downloaded_path
        self.torrent_name = torrent_name
        self.convert_filename_index_to_piece_index = {}
        for file in self.files:
            self.convert_filename_index_to_piece_index[file] = {}
        index = 0
        for piece in self.pieces:
            self.convert_filename_index_to_piece_index[piece.file_name][
                piece.index
            ] = index
            index += 1
        # Update the pieces to have a reference to this torrent
        for piece in self.pieces:
            piece.setTorrent(self)

    def startDownload(self, max_connections: int = 10):
        self.peer_manager.max_connections = max_connections
        self.peer_manager.fetchPeers(self.files)
        self.thread = threading.Thread(target=self.peer_manager.startDownload)
        download_logger.logger.info(f"Starting download {self.torrent_name}...")
        self.thread.start()
        print(f"Starting download {self.torrent_name}...")

    def stopDownloadFromPeer(self):
        print(f"Calling stop download from peer")
        if self.isComplete():
            self.mergePieces()
            self.torrent_manager.completeDownload(self.torrent_id)
        else:
            self.torrent_manager.pauseDownload(self.torrent_id)

    def stopDownloadFromTorrentManager(self):
        self.peer_manager.stopDownload()
        if self.thread is not None and self.thread.is_alive():
            self.thread.join()
            self.thread = None
        print("Download stopped")
        if self.isComplete():
            self.mergePieces()

    def delete(self):
        for piece in self.pieces:
            piece.deleteData()

    def isComplete(self) -> bool:
        if len(self.pieces) == 0:
            return True
        return self.downloaded_pieces == len(self.pieces)

    def progress(self) -> int:
        # Round to integer
        if len(self.pieces) == 0:
            return 100
        return int((self.downloaded_pieces / len(self.pieces)) * 100)

    def mergePieces(self):
        # Check if all pieces are downloaded and the file is not already created
        if not self.downloaded_path and self.isComplete():
            os.makedirs(
                f"{self.configs.download_dir}/{self.torrent_name}", exist_ok=True
            )
            for file in self.files:
                with open(
                    f"{self.configs.download_dir}/{self.torrent_name}/{file}", "wb"
                ) as f:
                    for piece in self.pieces:
                        if piece.file_name == file:
                            f.write(piece.getData())
                self.downloaded_path.append(
                    f"{self.configs.download_dir}/{self.torrent_name}/{file}"
                )
            print("File created.")
            self.open()

    def to_announcer_dict(self) -> dict:
        # Format: {"torrentId": "6734f7a6d04a4e80469e5d32", "pieceIndexes": [1]}
        files = {}
        for file in self.files:
            files[file] = []

        for piece in self.pieces:
            files[piece.file_name].append(piece.index)

        files_array = []
        for file in files:
            # Check if the file does not have any pieces
            if len(files[file]) == 0:
                continue
            files_array.append({"filename": file, "pieceIndexes": files[file]})

        return {
            "torrentId": self.torrent_id,
            "files": files_array,
        }

    def to_dict(self) -> dict:
        return {
            "torrent_id": self.torrent_id,
            "files": self.files,
            "pieces": Piece.convertPieceArrayToDictArray(self.pieces),
            "piece_size": self.piece_size,
            "tracker_url": self.tracker_url,
            "downloaded_path": self.downloaded_path,
            "torrent_name": self.torrent_name,
        }

    def open(self):
        # Open the downloaded file if this is windows
        if self.downloaded_path:
            if len(self.downloaded_path) > 1:
                if os.name == "nt":
                    os.system(
                        f'explorer "{os.path.normpath(os.path.dirname(self.downloaded_path[0]))}"'
                    )
                elif os.name == "posix":
                    # os.system(f'xdg-open "{os.path.dirname(self.downloaded_path[0])}"')
                    pass
                elif os.name == "mac":
                    os.system(f'open "{os.path.dirname(self.downloaded_path[0])}"')
            else:
                if os.name == "nt":
                    os.system(f'start "" "{self.downloaded_path[0]}"')
                elif os.name == "posix":
                    # os.system(f'xdg-open "{self.downloaded_path[0]}"')
                    pass
                elif os.name == "mac":
                    os.system(f'open "{self.downloaded_path[0]}"')

    @staticmethod
    def from_dict(
        torrent_dict: dict,
        configs: Configuration,
        torrent_manager: "TorrentManager",
    ) -> "Torrent":
        torrent = Torrent(
            torrent_id=torrent_dict["torrent_id"],
            files=torrent_dict["files"],
            pieces=[
                Piece.from_dict(piece_dict, None)
                for piece_dict in torrent_dict["pieces"]
            ],  # Initialize empty list
            piece_size=torrent_dict["piece_size"],
            configs=configs,
            tracker_url=torrent_dict["tracker_url"],
            torrent_manager=torrent_manager,
            downloaded_path=torrent_dict["downloaded_path"],
            torrent_name=torrent_dict["torrent_name"],
        )
        return torrent

    @staticmethod
    def convertTorrentArrayToDict(torrents: list["Torrent"]) -> list[dict]:
        return [torrent.to_dict() for torrent in torrents]

    def __str__(self) -> str:
        return f"ID: {self.torrent_id}, Name: {self.torrent_name}, Progress: {self.progress()}%"
