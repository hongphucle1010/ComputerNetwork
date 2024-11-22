from Modules.TorrentCreator.metadata_builder import MetadataBuilder
from Modules.TorrentCreator.torrent_encoder import TorrentEncoder


class TorrentCreator:
    def __init__(
        self, file_paths: list[str], tracker_url, piece_size: int = 512 * 1024
    ):
        self.file_paths = file_paths
        self.tracker_url = tracker_url
        self.piece_size = piece_size
        self._stop = False
        self.metadata = MetadataBuilder(self.tracker_url, self.file_paths, self.piece_size)

    def stop(self):
        self._stop = True
        self.metadata.stop()

    def create(self, output_path):
        if self._stop:
            return
        self.metadata.split_files()  # Split files into pieces
        if self._stop:
            return
        self.metadata.registerTorrent()  # Register torrent with tracker to get torrent_id
        if self._stop:
            return
        torrent_encoder = TorrentEncoder(
            self.metadata.to_dict()
        )  # Encode metadata to torrent file'
        torrent_encoder.bencode()  # Bencode the metadata
        torrent_encoder.save(output_path)  # Save the torrent file
        self.metadata.save_pieces()  # Save the pieces of the file

    @property
    def progress(self) -> float:
        return self.metadata.progress
