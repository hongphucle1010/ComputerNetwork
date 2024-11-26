import json
from typing import TYPE_CHECKING, List
from Modules.PeerConnection.torrent import Torrent
from Modules.PeerConnection.piece import Piece
from Modules.PeerConnection.seeding_pieces_manager import SeedingPiecesManager
from Modules.PeerConnection.torrent_decoder import TorrentDecoder
import os

if TYPE_CHECKING:
    from program import Program

torrent_dir = "torrents"
torrent_file_path = f"{torrent_dir}/torrents.json"

# Create a timer to measure the time taken to download a torrent

import time



class TorrentManager:
    def __init__(self, download_dir: str, program: "Program"):
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

    def findTorrent(self, torrent_id: str, list_torrents: List["Torrent"]) -> "Torrent":
        for torrent in list_torrents:
            if torrent.torrent_id == torrent_id:
                return torrent
        return None

    def removeTorrent(self, torrent_id: str):
        print("Removing torrent...", torrent_id)
        try:
            torrent = self.findTorrent(torrent_id, self.active_torrents)
            if torrent is not None:
                self.active_torrents.remove(torrent)
                torrent.stopDownloadFromTorrentManager()
                torrent.delete()
                return
            torrent = self.findTorrent(torrent_id, self.completed_torrents)
            if torrent is not None:
                self.completed_torrents.remove(torrent)
                torrent.delete()
                return
            torrent = self.findTorrent(torrent_id, self.paused_torrents)
            if torrent is not None:
                self.paused_torrents.remove(torrent)
                torrent.delete()
                return
            print("Torrent not found")
        except ValueError:
            print("Torrent not found")
            return
        finally:
            self.saveTorrents()

    def pauseDownload(self, torrent_id: str):
        print("Pausing download...")
        torrent = self.findTorrent(torrent_id, self.active_torrents)
        if torrent is None:
            print("Torrent not found")
            return
        self.active_torrents.remove(torrent)
        self.paused_torrents.append(torrent)
        torrent.stopDownloadFromTorrentManager()
        self.saveTorrents()

    def resumeDownload(self, torrent_id: str):
        print("Resuming download...")
        torrent = self.findTorrent(torrent_id, self.paused_torrents)
        if torrent is None:
            print("Torrent not found")
            return
        self.paused_torrents.remove(torrent)
        torrent.startDownload()
        self.active_torrents.append(torrent)
        self.saveTorrents()

    def completeDownload(self, torrent_id: str):
        print("Completing download...")
        torrent = self.findTorrent(torrent_id, self.active_torrents)
        if torrent is None:
            print("Torrent not found")
            return
        self.active_torrents.remove(torrent)
        self.completed_torrents.append(torrent)
        end_time = time.time()
        download_time = end_time - self.timer
        print(f"Download time: {download_time}")
        self.saveTorrents()

    def insertTorrent(self, torrent: "Torrent"):
        self.active_torrents.append(torrent)
        self.timer = time.time()
        torrent.startDownload()
        self.saveTorrents()

    def addTorrent(
        self,
        file_path: str,
        downloaded_path: List[str] = [],
        is_called_by_gui: bool = False,
    ):
        # Fake torrent data
        torrent_decoder = TorrentDecoder(file_path)
        metadata = torrent_decoder.decode()
        files = []
        pieces = []

        selected_files = []  # To store files selected via GUI

        if is_called_by_gui:
            # GUI logic for selecting files
            from tkinter import Toplevel, Label, Button, Checkbutton, IntVar

            gui_window = Toplevel()
            gui_window.title("Select Files to Download")
            gui_window.geometry("400x300")

            Label(
                gui_window, text="Select files to download:", font=("Arial", 12)
            ).pack(pady=10)

            file_vars = []  # To hold IntVars for checkboxes

            # Create checkboxes for each file
            for idx, file in enumerate(metadata["files"]):
                var = IntVar()
                file_vars.append(var)
                Checkbutton(gui_window, text=file["filename"], variable=var).pack(
                    anchor="w", padx=20
                )

            def on_confirm():
                nonlocal selected_files
                selected_files = [
                    metadata["files"][i]["filename"]
                    for i, var in enumerate(file_vars)
                    if var.get() == 1
                ]
                gui_window.destroy()

            Button(gui_window, text="Confirm", command=on_confirm).pack(pady=10)

            gui_window.transient()  # Set as a modal window
            gui_window.grab_set()
            gui_window.wait_window()

            # Filter pieces based on selected files
            for file in metadata["files"]:
                if file["filename"] in selected_files:
                    files.append(file["filename"])
                    for piece in file["pieces"]:
                        pieces.append(
                            Piece(
                                piece["index"],
                                piece["hash"],
                                piece["size"],
                                None,
                                file["filename"],
                            )
                        )
        else:
            # CLI Logic
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
                            None,
                            file["filename"],
                        )
                    )

        torrent = Torrent(
            metadata["torrent_id"],
            files,
            pieces,  # Initialize empty list
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

    def revealDownloadedFile(self, torrent_id: str):
        torrent = self.findTorrent(torrent_id, self.completed_torrents)
        if torrent is None:
            print("Torrent not found")
            return
        torrent.open()

    def pauseAllDownloads(self):
        for torrent in self.active_torrents:
            torrent.stopDownloadFromTorrentManager()

    def stop(self):
        self.pauseAllDownloads()
        self.saveTorrents()
        self.seeding_pieces_manager.stop()

    def getAllTorrents(self) -> List[dict]:
        torrents = self.getTorrentList()
        return [torrent.to_announcer_dict() for torrent in torrents]

    def getTorrentList(self) -> List["Torrent"]:
        return self.active_torrents + self.completed_torrents + self.paused_torrents

    def getTorrentList_StringType(self) -> List[str]:
        list = []
        for torrent in self.active_torrents:
            list.append(str(torrent) + " - Active")
        for torrent in self.completed_torrents:
            list.append(str(torrent) + " - Completed")
        for torrent in self.paused_torrents:
            list.append(str(torrent) + " - Paused")
        return list

    def printAllTorrents(self):
        print("Active torrents:")
        for torrent in self.active_torrents:
            print(
                f"{torrent.torrent_name} - {torrent.torrent_id} - {torrent.progress()}"
            )
        print("Completed torrents:")
        for torrent in self.completed_torrents:
            print(
                f"{torrent.torrent_name} - {torrent.torrent_id} - {torrent.progress()}"
            )
        print("Paused torrents:")
        for torrent in self.paused_torrents:
            print(
                f"{torrent.torrent_name} - {torrent.torrent_id} - {torrent.progress()}"
            )


# Dòng dưới dùng để testing thôi nhen ...
if __name__ == "__main__":
    download_manager = TorrentManager("downloads")
    print(download_manager.active_torrents)
    print(download_manager.completed_torrents)
    print(download_manager.paused_torrents)
    download_manager.saveTorrents()
