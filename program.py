import socket
from configuration import Configuration
from announcer import Announcer
from Modules.PeerConnection.seeding_pieces_manager import SeedingPiecesManager
from Modules.PeerConnection.torrent_manager import TorrentManager


class Program:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.configs = Configuration()
        self.port = self.configs.port
        self.announcer = Announcer(self.configs, self.ip)
        self.seeding_pieces_manager = SeedingPiecesManager()
        self.torrent_manager = TorrentManager(self.configs.download_dir, self)
        self.announcer.start()

    def start(self):
        try:
            option = -1
            while option != 0:
                print("1. Create Torrent")
                print("2. Add Torrent")
                print("3. Resume Torrent")
                print("0. Exit")
                option = int(input("Select an option: "))
                if option == 1:
                    print("Creating torrent...")
                elif option == 2:
                    print("Add torrent...")
                    file_path = input("Enter file path: ")
                    self.torrent_manager.addTorrent(file_path=file_path)
                elif option == 3:
                    print("Resume torrent...")
                    self.torrent_manager.resumeDownload("6734f7a6d04a4e80469e5d32")
                elif option == 0:
                    print("Exiting program...")
                else:
                    print("Invalid option. Please try again.")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.shutdown()
            print("Program exited.")

    def shutdown(self):
        print("Shutting down program...")
        self.announcer.stop()
        exit(0)

    def addTorrent(self, torrent):
        print("Adding torrent...")

    def removeTorrent(self, torrent):
        print("Removing torrent...")

    def downloadTorrent(self):
        print("Downloading torrent...")

    def seedingTorrent(self):
        print("Seeding torrent...")
