class TorrentDecoder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = None

    def decode(self):
        print("Decoding torrent file...")
        self.metadata = "Decoded metadata"
