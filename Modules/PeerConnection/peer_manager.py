from Modules.PeerConnection.peer import Peer
import requests
from collections import deque
import threading
import time


class PeerManager:
    def __init__(self, torrent, max_connections: int = 10):
        self.active_download_indexes = []
        self.max_connections = max_connections
        self.connectionQueue = deque()
        self.peerList = []
        self.torrent = torrent
        self.stop_triggered = False

    def fetchPeers(self):
        response = requests.get(
            f"{self.torrent.tracker_url}/api/find-available-peers/{self.torrent.torrent_id}"
        )
        peers = response.json()
        index = -1
        for obj in peers:
            index += 1
            # Check if obj is {} (empty)
            if not obj:
                self.peerList.append(None)
                continue
            peer = Peer(obj["peerId"], obj["ip"], obj["port"])
            self.connectionQueue.append((peer, index))
            self.peerList.append(peer)

    def stopDownload(self):
        print("Stopping download...")
        self.stop_triggered = True

    # def startDownload(self):
    # while not self.stop_triggered and not self.torrent.isComplete():

    def startDownload(self):
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
                        self.active_download_indexes.append(index)

            # Download pieces from peers using threads
            threads = []
            for index in list(
                self.active_download_indexes
            ):  # Iterate over a copy to avoid modifying the list during iteration
                peer: Peer = self.peerList[index]
                if peer is None:
                    continue

                def download_wrapper(index):
                    try:
                        peer.downloadPieces(self.torrent.pieces[index])
                        if self.torrent.pieces[
                            index
                        ].verifyDownload():  # Verify piece integrity
                            with lock:
                                self.torrent.downloaded_pieces += 1
                        with lock:
                            self.active_download_indexes.remove(
                                index
                            )  # Mark index as completed
                    except Exception as e:
                        print(f"Error downloading piece {index} from peer {peer}: {e}")

                thread = threading.Thread(target=download_wrapper, args=(index,))
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
