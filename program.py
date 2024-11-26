import socket
from typing import TYPE_CHECKING
from configuration import Configuration
from announcer import Announcer
from Modules.PeerConnection.torrent_manager import TorrentManager
from Modules.TorrentCreator.torrent_creator import TorrentCreator
from log import announcer_logger, download_logger, seeding_logger

if TYPE_CHECKING:
    from Modules.PeerConnection.torrent_manager import TorrentManager


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Try to connect to an external host to get the LAN IP
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        try:
            # If that fails, use gethostbyname to get the IP
            IP = socket.gethostbyname(socket.gethostname())
        except Exception:
            # If all methods fail, default to localhost
            IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class Program:
    def __init__(self, is_open_with_new_terminal: bool = True):
        self.ip = get_lan_ip()
        self.configs = Configuration()
        self.port = self.configs.port
        self.announcer = Announcer(self.configs, self.ip, self)
        self.torrent_manager: "TorrentManager" = TorrentManager(
            self.configs.download_dir, self
        )
        if is_open_with_new_terminal:
            announcer_logger.open_terminal()
            download_logger.open_terminal()
            seeding_logger.open_terminal()
        self.announcer.start()

    def start(self):
        try:
            option = -1
            while option != 0:
                print("=" * 20)
                print("1. Create Torrent")
                print("2. Add Torrent")
                print("3. Resume Torrent")
                print("4. Remove Torrent")
                print("5. Pause Torrent")
                print("6. Show Torrents")
                print("7. Reveal the torrent downloaded files")
                print("0. Exit")
                try:
                    option = int(input("Select an option: "))
                    print("-" * 20)
                    if option == 1:
                        self.createTorrent()
                    elif option == 2:
                        self.addTorrent()
                    elif option == 3:
                        self.resumeTorrent()
                    elif option == 4:
                        self.removeTorrent()
                    elif option == 5:
                        self.pauseTorrent()
                    elif option == 6:
                        self.showTorrents()
                    elif option == 7:
                        self.revealTorrentFiles()
                    elif option == 0:
                        print("Exiting program...")
                    else:
                        print("Invalid option. Please try again.")
                except Exception as e:
                    print(f"Incorrect input. Error: {e}")
                    # Print traceback
                    import traceback

                    traceback.print_exc()
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
        self.torrent_manager.stop()
        announcer_logger.clear()
        download_logger.clear()
        seeding_logger.clear()
        exit(0)

    def addTorrent(self):
        print("Add torrent...")
        file_path = input("Enter file path: ")
        self.torrent_manager.addTorrent(file_path=file_path, downloaded_path=[])

    def removeTorrent(self):
        print("Removing torrent...")
        torrent_id = input("Enter torrent ID: ")
        self.torrent_manager.removeTorrent(torrent_id)

    def revealTorrentFiles(self):
        print("Revealing downloaded files...")
        torrent_id = input("Enter torrent ID: ")
        self.torrent_manager.revealDownloadedFile(torrent_id)

    def resumeTorrent(self):
        print("Resume torrent...")
        torrent_id = input("Enter torrent ID: ")
        self.torrent_manager.resumeDownload(torrent_id)

    def pauseTorrent(self):
        print("Pause torrent...")
        torrent_id = input("Enter torrent ID: ")
        self.torrent_manager.pauseDownload(torrent_id)

    def showTorrents(self):
        self.torrent_manager.printAllTorrents()

    def createTorrent(self):
        print("Creating torrent...")
        num_files = int(input("Enter the number of files to add to the torrent:"))
        file_paths = []
        for i in range(num_files):
            file_path = input(f"Enter file path {i + 1}: ")
            file_paths.append(file_path)
        piece_size = int(input("Enter piece size (in KB): ")) * 1024
        torrent_name = input("Enter torrent name: ")
        torrent_creator = TorrentCreator(
            file_paths, self.configs.tracker_url, piece_size
        )
        try:
            def progress_monitor():
                while torrent_creator.progress < 100:
                    print(f"Progress: {torrent_creator.progress:.2f}%")
                    time.sleep(1)
                print("Torrent creation completed.")

            import threading
            import time

            progress_thread = threading.Thread(target=progress_monitor)
            progress_thread.start()

            torrent_creator.create(f"torrents/{torrent_name}.torrent")
            progress_thread.join()

            if_not_add = (
                input("Add torrent to seeding list? (y/n): ").lower().strip() == "n"
            )
            if not if_not_add:
                self.torrent_manager.addTorrent(
                    file_path=f"torrents/{torrent_name}.torrent", downloaded_path=file_paths
                )
        except KeyboardInterrupt:
            torrent_creator.stop()
            print("Torrent creation has been stopped by user.")
