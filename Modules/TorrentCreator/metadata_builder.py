from Modules.TorrentCreator.file_handler import FileHandler
import os
import requests


class MetadataBuilder:
    def __init__(self, tracker_url, file_path, file_size, piece_size, pieceHashes):
        self.tracker_url = tracker_url
        self.name = MetadataBuilder.split_file_path(file_path)
        self.size = file_size
        self.piece_size = piece_size
        self.pieceHashes = pieceHashes
        self.torrent_id = None

    def set_file_info(self):
        pass

    @staticmethod
    def split_file_path(file_path):
        return os.path.basename(file_path)

    def to_dict(self):
        return {
            "tracker_url": self.tracker_url,
            "name": self.name,
            "size": self.size,
            "piece_size": self.piece_size,
            "pieces": self.pieceHashes,
            "torrent_id": self.torrent_id,
        }

    def registerTorrent(self):
        response = requests.post(
            self.tracker_url + "/api/register-torrent", json=self.to_dict()
        )
        self.torrent_id = response.json()["id"]
        return response.json()
