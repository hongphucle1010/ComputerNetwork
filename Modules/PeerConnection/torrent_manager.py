import json
from Modules.PeerConnection.torrent import Torrent
from Modules.PeerConnection.piece import Piece
from Modules.PeerConnection.seeding_pieces_manager import SeedingPiecesManager
from Modules.PeerConnection.torrent_decoder import TorrentDecoder
import os

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
        self.active_torrents.append(torrent)
        torrent.startDownload()
        self.saveTorrents()

    def addTorrent(self, file_path: str, downloaded_path: list[str] = []):
        # Fake torrent data
        torrent_decoder = TorrentDecoder(file_path)
        metadata = torrent_decoder.decode()
        print(metadata)
        """
        metadata = {'files': [{'filename': 'Hoa don.pdf', 'pieces': [{'hash': 'ec49ec89ef6ba6a01b345a57ac9feeffdf361783', 'index': 0, 'size': 524288}], 'size': 73911}, {'filename': 'ĐATH-CNPM-TN03_2-BKBotScheduler.pdf', 'pieces': [{'hash': '1635a0b9de963d7404896d2d32779d4ac0b6644e', 'index': 0, 'size': 524288}, {'hash': '38f0b9e6d660f7aca7db4a07455e7d1d587182f3', 'index': 1, 'size': 524288}, {'hash': '62e6c5665d29cf24e35cb067e581d2f0089a5bf9', 'index': 2, 'size': 524288}, {'hash': 'e7b49334d51c6c387c7c99cbf5844f6304c7600a', 'index': 3, 'size': 524288}, {'hash': 'a1b91dfc52a06bca7175140f61140e67ceb21309', 'index': 4, 'size': 524288}, {'hash': '0cf43c62967320a879529d83b3dd2b2b17899fa6', 'index': 5, 'size': 524288}], 'size': 3010320}], 'piece_size': 524288, 'torrent_id': '673b276120485a379060b014', 'tracker_url': 'http://localhost:3000'}
        """
        files = []
        pieces = []
        # Extract metadata into files
        for file in metadata["files"]:
            files.append(file["filename"])
            # Check if users want to download this file
            want_to_download = (
                (
                    input(f"Do you want to download {file['filename']}? (y/n): ")
                    .lower()
                    .strip()
                    == "y"
                )
                if not downloaded_path
                else True
            )
            if not want_to_download:
                continue
            for piece in file["pieces"]:
                pieces.append(
                    Piece(
                        piece["index"],
                        piece["hash"],
                        piece["size"],
                        metadata["torrent_id"],
                        file["filename"],
                    )
                )
        torrent = Torrent(
            metadata["torrent_id"],
            files,
            pieces,
            metadata["piece_size"],
            metadata["tracker_url"],
            self.program.configs,
            self,
            downloaded_path,
            os.path.basename(file_path),
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
        torrents = self.active_torrents + self.completed_torrents + self.paused_torrents
        return [torrent.to_announcer_dict() for torrent in torrents]


# Dòng dưới dùng để testing thôi nhen ...
if __name__ == "__main__":
    download_manager = TorrentManager("downloads")
    print(download_manager.active_torrents)
    print(download_manager.completed_torrents)
    print(download_manager.paused_torrents)
    download_manager.saveTorrents()
