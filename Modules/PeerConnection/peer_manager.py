from Modules.PeerConnection.peer import Peer
import requests
from collections import deque
import threading
from log import download_logger


class PeerManager:
    def __init__(self, torrent, max_connections: int = 10):
        self.active_download_indexes = []
        self.max_connections = max_connections
        self.connectionQueue = deque()
        self.torrent = torrent
        self.stop_triggered = False

    def fetchPeers(self, files: list[str]):
        try:
            response = requests.get(
                f"{self.torrent.tracker_url}/api/find-available-peers/{self.torrent.torrent_id}"
            )
            peers = response.json()
            for obj in peers:
                filename = obj["filename"]
                if filename not in files:
                    continue
                index = -1
                for piece in obj["pieces"]:
                    index += 1
                    if piece["ip"] is None:
                        continue
                    peer = Peer(piece["peerId"], piece["ip"], piece["port"])
                    self.connectionQueue.append(
                        (
                            peer,
                            self.torrent.convert_filename_index_to_piece_index[
                                filename
                            ][index],
                        )
                    )
            download_logger.logger.info(f"Fetched {len(peers)} peers.")
        except Exception as e:
            # print(f"Error fetching peers: {e}")
            download_logger.logger.error(f"Error fetching peers: {e}")

    def stopDownload(self):
        print("Stopping download...")
        self.stop_triggered = True

    def startDownload(self):
        if self.torrent.downloaded_path:
            self.stopDownload()
            return
        if self.torrent.isComplete() and not self.torrent.downloaded_path:
            self.torrent.mergePieces()
            self.stopDownload()
            return
        while not self.stop_triggered and not self.torrent.isComplete():
            # Lock for thread-safe operations on shared resources
            lock = threading.Lock()

            # Push peers from connectionQueue to active_download_indexes
            while (
                len(self.active_download_indexes) < self.max_connections
                and self.connectionQueue
            ):
                with lock:  # Ensure thread safety while accessing the queue
                    peer, index = self.connectionQueue.popleft()
                    if not self.torrent.pieces[index].downloaded:
                        self.active_download_indexes.append((peer, index))

            # Download pieces from peers using threads
            threads = []
            for peer, index in list(
                self.active_download_indexes
            ):  # Iterate over a copy to avoid modifying the list during iteration

                def download_wrapper(peer, index):
                    try:
                        download_logger.logger.info(
                            f"Downloading piece {index} from peer {peer}"
                        )
                        peer.downloadPieces(self.torrent.pieces[index])
                        if self.torrent.pieces[
                            index
                        ].verifyDownload():  # Verify piece integrity
                            with lock:
                                self.torrent.downloaded_pieces += 1
                        with lock:
                            self.active_download_indexes.remove(
                                (peer, index)
                            )  # Mark index as completed
                    except Exception as e:
                        # print(f"Error downloading piece {index} from peer {peer}: {e}")
                        download_logger.logger.error(
                            f"Error downloading piece {index} from peer {peer}: {e}"
                        )

                thread = threading.Thread(target=download_wrapper, args=(peer, index))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

            if (
                self.connectionQueue == deque([])
                and len(self.active_download_indexes) == 0
            ):
                if not self.torrent.isComplete():
                    print("Download stopped. No more peers available.")
                else:
                    print("Download complete.")
                self.stopDownload()
                self.torrent.stopPeer()
