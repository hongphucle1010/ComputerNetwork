from Modules.TorrentCreator.file_handler import FileHandler
from Modules.TorrentCreator.metadata_builder import MetadataBuilder
from Modules.TorrentCreator.torrent_encoder import TorrentEncoder
from Modules.TorrentCreator.piece_hasher import PieceHasher
import requests
import json


class TorrentCreator:
    def __init__(self, file_path, tracker_url, piece_size: int = 512 * 1024):
        self.file_path = file_path
        self.file_handler = FileHandler(file_path, piece_size)
        self.piece_hasher = PieceHasher()
        self.tracker_url = tracker_url
        self.piece_size = piece_size

    def create(self, output_path):
        self.file_handler.splitIntoPieces()
        self.piece_hasher.generateAllHashes(self.file_handler.pieces)
        metadata_builder = MetadataBuilder(
            self.tracker_url,
            self.file_path,
            self.file_handler.file_size,
            self.piece_size,
            self.piece_hasher.pieceHashes,
        )
        metadata_builder.registerTorrent()
        torrent_encoder = TorrentEncoder(metadata_builder.to_dict())
        torrent_encoder.bencode()
        torrent_encoder.save(output_path)
        self.file_handler.savePieces(metadata_builder.torrent_id)
