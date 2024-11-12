import socket
from configuration import Configuration
from announcer import Announcer
from Modules.PeerConnection.seeding_pieces_manager import SeedingPiecesManager
from Modules.PeerConnection.download_torrent_manager import DownloadTorrentManager


class Program:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.configs = Configuration()
        self.port = self.configs.port
        self.announcer = Announcer(self.configs.tracker_url, self.configs.peer_id)
        self.seeding_pieces_manager = SeedingPiecesManager()
        self.download_torrent_manager = DownloadTorrentManager(
            self.configs.download_dir, self
        )

    def start(self):
        option = -1
        while option != 0:
            print("1. Create Torrent")
            print("2. Download Torrent")
            print("0. Exit")
            option = int(input("Select an option: "))
            if option == 1:
                print("Creating torrent...")
            elif option == 2:
                print("Downloading torrent...")
            elif option == 0:
                print("Exiting program...")
            else:
                print("Invalid option. Please try again.")
        print("Program exited.")

    def shutdown(self):
        print("Shutting down program...")
        exit(0)

    def addTorrent(self, torrent):
        print("Adding torrent...")

    def removeTorrent(self, torrent):
        print("Removing torrent...")

    def downloadTorrent(self):
        print("Downloading torrent...")

    def seedingTorrent(self):
        print("Seeding torrent...")
