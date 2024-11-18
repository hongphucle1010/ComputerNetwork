from Modules.TorrentCreator.metadata_builder import MetadataBuilder
from Modules.TorrentCreator.torrent_encoder import TorrentEncoder


class TorrentCreator:
    def __init__(
        self, file_paths: list[str], tracker_url, piece_size: int = 512 * 1024
    ):
        self.file_paths = file_paths
        self.tracker_url = tracker_url
        self.piece_size = piece_size

    def create(self, output_path):
        metadata = MetadataBuilder(self.tracker_url, self.file_paths, self.piece_size)
        metadata.split_files()  # Split files into pieces
        metadata.registerTorrent()  # Register torrent with tracker to get torrent_id
        torrent_encoder = TorrentEncoder(
            metadata.to_dict()
        )  # Encode metadata to torrent file
        torrent_encoder.bencode()  # Bencode the metadata
        torrent_encoder.save(output_path)  # Save the torrent file
        metadata.save_pieces()  # Save the pieces of the file
