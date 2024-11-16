from Modules.PeerConnection.peer_manager import PeerManager
from configuration import Configuration
from Modules.PeerConnection.piece import Piece
import threading


class Torrent:
    def __init__(
        self,
        torrent_id: str,
        file_name: str,
        pieces: list,
        total_size: int,
        tracker_url: str,
        configs: Configuration,
        downloaded_pieces: int = 0,
    ):
        self.torrent_id = torrent_id
        self.file_name = file_name
        self.pieces = pieces
        self.total_size = total_size
        self.downloaded_pieces = downloaded_pieces
        self.tracker_url = tracker_url
        self.configs = configs
        self.peer_manager = PeerManager(self)
        self.thread = None

    def startDownload(self, max_connections: int = 10):
        self.peer_manager.max_connections = max_connections
        self.peer_manager.fetchPeers()
        self.thread = threading.Thread(target=self.peer_manager.startDownload)
        self.thread.start()
        print("Starting download...")

    def stopDownload(self):
        self.peer_manager.stopDownload()
        self.thread.join()
        print("Download stopped")

    def isComplete(self):
        print("Checking if torrent is complete...")
        return self.downloaded_pieces == len(self.pieces)

    def progress(self):
        # Round to integer
        return int((self.downloaded_pieces / len(self.pieces)) * 100)

    def mergePieces(self):
        # TODO: Implement merging pieces
        print("Merging pieces...")

    def to_dict(self):
        return {
            "torrent_id": self.torrent_id,
            "file_name": self.file_name,
            "pieces": Piece.convertPieceArrayToDictArray(self.pieces),
            "total_size": self.total_size,
            "downloaded_pieces": self.downloaded_pieces,
            "tracker_url": self.tracker_url,
        }

    @staticmethod
    def from_dict(torrent_dict, configs: Configuration):
        return Torrent(
            torrent_id=torrent_dict["torrent_id"],
            file_name=torrent_dict["file_name"],
            pieces=[
                Piece.from_dict(piece, torrent_dict["torrent_id"])
                for piece in torrent_dict["pieces"]
            ],
            total_size=torrent_dict["total_size"],
            downloaded_pieces=torrent_dict["downloaded_pieces"],
            configs=configs,
            tracker_url=torrent_dict["tracker_url"],
        )

    @staticmethod
    def convertTorrentArrayToDict(torrents: list):
        return [torrent.to_dict() for torrent in torrents]
