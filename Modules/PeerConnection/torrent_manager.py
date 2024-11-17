import json
from Modules.PeerConnection.torrent import Torrent
from Modules.PeerConnection.piece import Piece
from Modules.PeerConnection.seeding_pieces_manager import SeedingPiecesManager
from Modules.PeerConnection.torrent_decoder import TorrentDecoder

torrent_dir = "torrents"
torrent_file_path = f"{torrent_dir}/torrents.json"


class TorrentManager:
    def __init__(self, download_dir: str, program):
        self.download_dir = download_dir
        self.active_torrents = []
        self.completed_torrents = []
        self.paused_torrents = []
        self.program = program
        self.loadTorrents()
        self.seeding_pieces_manager = SeedingPiecesManager(self)
        self.seeding_pieces_manager.start()

    def saveTorrents(self):
        with open(torrent_file_path, "w") as f:
            json.dump(
                {
                    "active": Torrent.convertTorrentArrayToDict(self.active_torrents),
                    "completed": Torrent.convertTorrentArrayToDict(
                        self.completed_torrents
                    ),
                    "paused": Torrent.convertTorrentArrayToDict(self.paused_torrents),
                },
                f,
                indent=4,
            )

    # def startDownload(self, torrent: Torrent):
    #     print("Starting download...")
    #     self.active_torrents.append(torrent)
    #     self.saveTorrents()

    def findTorrent(self, torrent_id: str, list_torrents: list[Torrent]) -> Torrent:
        for torrent in list_torrents:
            if torrent.torrent_id == torrent_id:
                return torrent
        return None

    def pauseDownload(self, torrent_id: str):
        print("Pausing download...")
        torrent = self.findTorrent(torrent_id, self.active_torrents)
        self.active_torrents.remove(torrent)
        self.paused_torrents.append(torrent)
        self.saveTorrents()

    def resumeDownload(self, torrent_id: str):
        print("Resuming download...")
        torrent = self.findTorrent(torrent_id, self.paused_torrents)
        print(self.paused_torrents)
        self.paused_torrents.remove(torrent)
        torrent.startDownload()
        self.active_torrents.append(torrent)
        self.saveTorrents()

    def completeDownload(self, torrent_id: str):
        print("Completing download...")
        torrent = self.findTorrent(torrent_id, self.active_torrents)
        self.active_torrents.remove(torrent)
        self.completed_torrents.append(torrent)
        self.saveTorrents()

    def insertTorrent(self, torrent: Torrent):
        self.paused_torrents.append(torrent)
        self.saveTorrents()

    def addTorrent(self, file_path: str):
        # Fake torrent data
        torrent_decoder = TorrentDecoder(file_path)
        metadata = torrent_decoder.decode()
        print(metadata)
        torrent = Torrent.from_dict(
            {
                "torrent_id": metadata["torrent_id"],
                "file_name": metadata["name"],
                "pieces": metadata["pieces"],
                "total_size": metadata["size"],
                "downloaded_pieces": 0,
                "tracker_url": metadata["tracker_url"],
            },
            self.program.configs,
            self,
        )
        self.insertTorrent(torrent)

    def loadTorrents(self):
        try:
            with open(torrent_file_path, "r") as f:
                torrents = json.load(f)
                self.active_torrents = [
                    Torrent.from_dict(torrent, self.program.configs, self)
                    for torrent in torrents["active"]
                ]
                self.completed_torrents = [
                    Torrent.from_dict(torrent, self.program.configs, self)
                    for torrent in torrents["completed"]
                ]
                self.paused_torrents = [
                    Torrent.from_dict(torrent, self.program.configs, self)
                    for torrent in torrents["paused"]
                ]
            for torrent in self.active_torrents:
                torrent.startDownload()
        except FileNotFoundError:
            pass

    def pauseAllDownloads(self):
        for torrent in self.active_torrents:
            torrent.stopDownload()

    def stop(self):
        self.pauseAllDownloads()
        self.saveTorrents()
        self.seeding_pieces_manager.stop()

    def getAllTorrents(self):
        return self.active_torrents + self.completed_torrents + self.paused_torrents


# Dòng dưới dùng để testing thôi nhen ...
if __name__ == "__main__":
    download_manager = TorrentManager("downloads")
    print(download_manager.active_torrents)
    print(download_manager.completed_torrents)
    print(download_manager.paused_torrents)
    download_manager.saveTorrents()
