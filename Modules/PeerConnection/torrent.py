class Torrent:
    def __init__(
        self,
        torrent_id: str,
        file_name: str,
        pieces: list,
        total_size: int,
        downloaded_pieces: int,
    ):
        self.torrent_id = torrent_id
        self.file_name = file_name
        self.pieces = pieces
        self.total_size = total_size
        self.downloaded_pieces = downloaded_pieces

    def startDownload(self):
        print("Starting download...")

    def isComplete(self):
        print("Checking if torrent is complete...")
        return self.downloaded_pieces == len(self.pieces)

    def to_dict(self):
        return {
            "torrent_id": self.torrent_id,
            "file_name": self.file_name,
            "pieces": self.pieces,
            "total_size": self.total_size,
            "downloaded_pieces": self.downloaded_pieces,
        }

    @staticmethod
    def from_dict(torrent_dict):
        return Torrent(
            torrent_dict["torrent_id"],
            torrent_dict["file_name"],
            torrent_dict["pieces"],
            torrent_dict["total_size"],
            torrent_dict["downloaded_pieces"],
        )

    @staticmethod
    def convertTorrentArrayToDict(torrents: list):
        return [torrent.to_dict() for torrent in torrents]
