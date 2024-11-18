from Modules.PeerConnection.peer_manager import PeerManager
from configuration import Configuration
from Modules.PeerConnection.piece import Piece
import threading
import os


class Torrent:
    def __init__(
        self,
        torrent_id: str,
        files: list[str],
        pieces: list[Piece],
        piece_size: int,
        tracker_url: str,
        configs: Configuration,
        torrent_manager,
        downloaded_path: list[
            str
        ] = [],  # If downloaded_path is not None, the file is already downloaded
        torrent_name: str = "",
    ):
        self.torrent_id = torrent_id
        self.files = files
        self.pieces = pieces
        self.piece_size = piece_size
        self.tracker_url = tracker_url
        self.configs = configs
        self.peer_manager = PeerManager(self)
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
            if piece.verifyDownload():
                self.downloaded_pieces += 1
            self.convert_filename_index_to_piece_index[piece.file_name][
                piece.index
            ] = index
            index += 1

    def startDownload(self, max_connections: int = 10):
        self.peer_manager.max_connections = max_connections
        self.peer_manager.fetchPeers()
        self.thread = threading.Thread(target=self.peer_manager.startDownload)
        self.thread.start()
        print("Starting download...")

    def stopPeer(self):
        if self.isComplete():
            self.mergePieces()
            self.torrent_manager.completeDownload(self.torrent_id)
        else:
            self.torrent_manager.pauseDownload(self.torrent_id)

    def stopDownload(self):
        self.peer_manager.stopDownload()
        if self.thread is not None:
            self.thread.join()
        print("Download stopped")
        self.stopPeer()

    def isComplete(self):
        print("Checking if torrent is complete...")
        return self.downloaded_pieces == len(self.pieces)

    def progress(self):
        # Round to integer
        return int((self.downloaded_pieces / len(self.pieces)) * 100)

    def mergePieces(self):
        # Check if all pieces are downloaded and the file is not already created
        if not self.downloaded_path and self.isComplete():
            os.makedirs(f"downloads/{self.torrent_name}", exist_ok=True)
            for file in self.files:
                with open(f"downloads/{self.torrent_name}/{file}", "wb") as f:
                    for piece in self.pieces:
                        if piece.file_name == file:
                            f.write(piece.getData())
                self.downloaded_path.append(f"downloads/{self.torrent_name}/{file}")
            print("File created.")
            self.open()

    def to_announcer_dict(self):
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

    def to_dict(self):
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
        # Open the downloaded file
        if self.downloaded_path:
            if len(self.downloaded_path) > 1:
                print("Opening folder...")
                os.system(f'explorer "{os.path.dirname(self.downloaded_path[0])}"')
            else:
                print("Opening file...")
                os.system(f'start "{self.downloaded_path[0]}"')

    @staticmethod
    def from_dict(torrent_dict, configs: Configuration, torrent_manager):
        return Torrent(
            torrent_id=torrent_dict["torrent_id"],
            pieces=[
                Piece.from_dict(piece, torrent_dict["torrent_id"])
                for piece in torrent_dict["pieces"]
            ],
            files=torrent_dict["files"],
            piece_size=torrent_dict["piece_size"],
            configs=configs,
            tracker_url=torrent_dict["tracker_url"],
            torrent_manager=torrent_manager,
            downloaded_path=torrent_dict["downloaded_path"],
            torrent_name=torrent_dict["torrent_name"],
        )

    @staticmethod
    def convertTorrentArrayToDict(torrents: list):
        return [torrent.to_dict() for torrent in torrents]
