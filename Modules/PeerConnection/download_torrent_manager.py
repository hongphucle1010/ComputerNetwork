import json
from Modules.PeerConnection.torrent import Torrent

torrent_dir = "torrents"
torrent_file_path = f"{torrent_dir}/torrents.json"


class DownloadTorrentManager:
    def __init__(self, download_dir: str, program):
        self.download_dir = download_dir
        self.active_torrents = []
        self.completed_torrents = []
        self.paused_torrents = []
        self.loadTorrents()
        self.program = program

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

    def startDownload(self, torrent: Torrent):
        print("Starting download...")
        self.active_torrents.append(torrent)
        self.saveTorrents()

    def pauseDownload(self, torrent: Torrent):
        print("Pausing download...")
        self.active_torrents.remove(torrent)
        self.paused_torrents.append(torrent)
        self.saveTorrents()

    def resumeDownload(self, torrent: Torrent):
        print("Resuming download...")
        self.paused_torrents.remove(torrent)
        self.active_torrents.append(torrent)
        self.saveTorrents()

    def completeDownload(self, torrent: Torrent):
        print("Completing download...")
        self.active_torrents.remove(torrent)
        self.completed_torrents.append(torrent)
        self.saveTorrents()

    def loadTorrents(self):
        try:
            with open(torrent_file_path, "r") as f:
                torrents = json.load(f)
                self.active_torrents = [
                    Torrent.from_dict(torrent) for torrent in torrents["active"]
                ]
                self.completed_torrents = [
                    Torrent.from_dict(torrent) for torrent in torrents["completed"]
                ]
                self.paused_torrents = [
                    Torrent.from_dict(torrent) for torrent in torrents["paused"]
                ]
        except FileNotFoundError:
            pass


# Dòng dưới dùng để testing thôi nhen ...
if __name__ == "__main__":
    download_manager = DownloadTorrentManager("downloads")
    print(download_manager.active_torrents)
    print(download_manager.completed_torrents)
    print(download_manager.paused_torrents)
    download_manager.saveTorrents()
