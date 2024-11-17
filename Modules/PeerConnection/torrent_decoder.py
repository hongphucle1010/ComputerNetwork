import bencodepy


class TorrentDecoder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = None

    def decode(self):
        with open(self.file_path, "rb") as f:
            self.metadata = self._convert_bytes_to_str(bencodepy.decode(f.read()))
        # Convert bytes to string, key and value
        return self.metadata

    @staticmethod
    def _convert_bytes_to_str(data):
        if isinstance(data, dict):
            return {
                TorrentDecoder._convert_bytes_to_str(
                    k
                ): TorrentDecoder._convert_bytes_to_str(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [TorrentDecoder._convert_bytes_to_str(item) for item in data]
        elif isinstance(data, bytes):
            return data.decode("utf-8")
        else:
            return data


if __name__ == "__main__":
    TorrentDecoder = TorrentDecoder(
        "torrents/ĐATH-CNPM-TN03_2-BKBotScheduler.pdf.torrent"
    )
    print(TorrentDecoder.decode())
