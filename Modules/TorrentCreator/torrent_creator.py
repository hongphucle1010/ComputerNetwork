from file_handler import FileHandler
from metadata_builder import MetadataBuilder
from torrent_encoder import TorrentEncoder
from piece_hasher import PieceHasher


class TorrentCreator:
    def __init__(self, file_path, tracker_url):
        self.file_path = file_path
        self.file_handler = FileHandler(file_path, 1024 * 1024)
        self.metadata_builder = MetadataBuilder(tracker_url, file_path, 1024)
        self.piece_hasher = PieceHasher()
        self.torrent_encoder = TorrentEncoder()

    def create(self, output_path):
        pass
