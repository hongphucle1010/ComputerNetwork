import bencodepy

class TorrentEncoder:
    def __init__(self, metadata):
        self.metadata = metadata
        self.encodedata = None

    def bencode(self):
        self.encodedata = bencodepy.encode(self.metadata)
    def save(self, output_path):
        with open(output_path, "wb") as file:
            file.write(self.encodedata)