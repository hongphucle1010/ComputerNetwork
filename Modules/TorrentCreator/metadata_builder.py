from Modules.TorrentCreator.file_handler import File
import os
import requests


class MetadataBuilder:
    def __init__(self, tracker_url: str, file_paths: list[str], piece_size: int):
        self.tracker_url = tracker_url
        self.piece_size = piece_size
        self.files = [File(file_path) for file_path in file_paths]
        self.torrent_id = None

    def split_files(self):

        for file in self.files:
            file.split_into_pieces(self.piece_size)

    def to_dict(self):
        return {
            "tracker_url": self.tracker_url,
            "piece_size": self.piece_size,
            "torrent_id": self.torrent_id,
            "files": [file.to_dict() for file in self.files],
        }

    def registerTorrent(self):
        response = requests.post(
            self.tracker_url + "/api/register-torrent", json=self.to_dict()
        )
        self.torrent_id = response.json()["id"]
        return response.json()

    def save_pieces(self):
        for file in self.files:
            file.save(self.torrent_id)
