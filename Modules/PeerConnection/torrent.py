from Modules.PeerConnection.peer_manager import PeerManager
from configuration import Configuration
from Modules.PeerConnection.piece import Piece
import threading


class Torrent:
    def __init__(
        self,
        torrent_id: str,
        file_name: str,
        pieces: list[Piece],
        total_size: int,
        tracker_url: str,
        configs: Configuration,
        torrent_manager,
    ):
        self.torrent_id = torrent_id
        self.file_name = file_name
        self.pieces = pieces
        self.total_size = total_size
        self.tracker_url = tracker_url
        self.configs = configs
        self.peer_manager = PeerManager(self)
        self.thread = None
        self.torrent_manager = torrent_manager
        self.downloaded_pieces = 0
        for piece in self.pieces:
            if piece.verifyDownload():
                self.downloaded_pieces += 1

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
        # TODO: Implement merging pieces
        print("Merging pieces...")

    def to_announcer_dict(self):
        # Format: {"torrentId": "6734f7a6d04a4e80469e5d32", "pieceIndexes": [1]}
        return {
            "torrentId": self.torrent_id,
            "pieceIndexes": [piece.index for piece in self.pieces if piece.downloaded],
        }

    def to_dict(self):
        return {
            "torrent_id": self.torrent_id,
            "file_name": self.file_name,
            "pieces": Piece.convertPieceArrayToDictArray(self.pieces),
            "total_size": self.total_size,
            "tracker_url": self.tracker_url,
        }

    @staticmethod
    def from_dict(torrent_dict, configs: Configuration, torrent_manager):
        return Torrent(
            torrent_id=torrent_dict["torrent_id"],
            file_name=torrent_dict["file_name"],
            pieces=[
                Piece.from_dict(piece, torrent_dict["torrent_id"])
                for piece in torrent_dict["pieces"]
            ],
            total_size=torrent_dict["total_size"],
            configs=configs,
            tracker_url=torrent_dict["tracker_url"],
            torrent_manager=torrent_manager,
        )

    @staticmethod
    def convertTorrentArrayToDict(torrents: list):
        return [torrent.to_dict() for torrent in torrents]
