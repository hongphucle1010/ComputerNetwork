from Modules.PeerConnection.peer import Peer
import requests
from collections import deque
import threading
from log import download_logger
import time
from Modules.PeerConnection.piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Modules.PeerConnection.torrent import Torrent


class PeerManager:
    BLOCK_PERIOD = 30  # Block peers for 300 seconds (5 minutes)

    def __init__(self, torrent: "Torrent", max_connections: int = 100):
        self.active_download: list[tuple[Peer, int]] = []
        self.max_connections = max_connections
        self.connectionQueue = deque()
        self.torrent = torrent
        self.stop_triggered = False
        self.temporary_blocklist = (
            {}
        )  # Dict of peer IDs and their unblock times

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
                    unblock_time = self.temporary_blocklist.get(piece["peerId"])
                    if unblock_time is not None:
                        if time.time() < unblock_time:
                            continue  # Peer is still blocked
                        else:
                            del self.temporary_blocklist[piece["peerId"]]  # Remove expired block
                    peer = Peer(piece["peerId"], piece["ip"], piece["port"])
                    piece_index = self.torrent.convert_filename_index_to_piece_index[
                        filename
                    ][index]
                    self.connectionQueue.append(
                        (
                            peer,
                            piece_index,
                        )
                    )
            download_logger.logger.info(f"Fetched {len(peers)} peers.")
        except Exception as e:
            # print(f"Error fetching peers: {e}")
            download_logger.logger.error(f"Error fetching peers: {e}")

    # In case cannot connect to the peer to download the piece, program will connect to another peer to download the piece.
    # First, connect to tracker to get the list of peers that have the piece.
    def fetchPeersWithPiece(self, piece: Piece):
        try:
            piece_index = self.torrent.convert_filename_index_to_piece_index[
                piece.file_name
            ][piece.index]
            response = requests.get(
                f"{self.torrent.tracker_url}/api/find-piece-peers?torrentId={piece.torrent.torrent_id}&pieceIndex={piece.index}&filename={piece.file_name}"
            )
            peers = response.json()
            for obj in peers:
                unblock_time = self.temporary_blocklist.get(obj["peerId"])
                if unblock_time is not None:
                    if time.time() < unblock_time:
                        continue  # Peer is still blocked
                    else:
                        del self.temporary_blocklist[obj["peerId"]]  # Remove expired block
                peer = Peer(obj["peerId"], obj["ip"], obj["port"])
                self.connectionQueue.append(
                    (
                        peer,
                        piece_index,
                    )
                )
            download_logger.logger.info(
                f"Fetched {len(peers)} peers for piece {piece_index}."
            )
        except Exception as e:
            download_logger.logger.error(
                f"Error fetching peers for piece {piece_index}: {e}"
            )

    def stopDownload(self):
        print("Stopping download...")
        self.stop_triggered = True
        # Stop all active peers
        for peer, index in self.active_download:
            peer.stop()
        # Clear temporary blocklist
        while self.active_download:
            time.sleep(1)  # Wait for ongoing downloads to finish
        self.temporary_blocklist.clear()
        self.stop_triggered = False

    def startDownload(self):
        if self.torrent.downloaded_path:
            print(
                f"Download {self.torrent.torrent_name} already complete at {self.torrent.downloaded_path}"
            )
            self.torrent.stopDownloadFromPeer()
            return
        if self.torrent.isComplete() and not self.torrent.downloaded_path:
            self.torrent.stopDownloadFromPeer()
            return

        lock = threading.Lock()
        semaphore = threading.Semaphore(self.max_connections)
        threads = []

        def download_wrapper(peer: Peer, index: int):
            try:
                download_logger.logger.info(
                    f"Downloading piece {index} from peer {peer.peer_id}"
                )
                # Check if the piece is already downloaded
                if self.torrent.pieces[index].downloaded:
                    return
                peer.downloadPieces(self.torrent.pieces[index])
                # Verify the downloaded piece, if not correct, fetch another peer to download
                download_logger.logger.info(
                    f"Updating piece {index} status after download from peer {peer.peer_id}"
                )
                if (
                    not self.torrent.pieces[index].downloaded
                    and not self.stop_triggered
                ):
                    # Add the peer to the temporary blocklist with an unblock time
                    with lock:
                        unblock_time = time.time() + self.BLOCK_PERIOD
                        self.temporary_blocklist[peer.peer_id] = unblock_time
                        self.fetchPeersWithPiece(self.torrent.pieces[index])
                else:
                    download_logger.logger.info(
                        f"Piece {index} downloaded successfully from peer {peer.peer_id}"
                    )

            except Exception as e:
                download_logger.logger.error(
                    f"Error downloading piece {index} from peer {peer.peer_id}: {e}"
                )
            finally:
                semaphore.release()
                # Remove the use of lock here to prevent deadlocks
                if (peer, index) in self.active_download:
                    with lock:
                        self.active_download.remove((peer, index))
                    download_logger.logger.info(
                        f"Removed peer {peer.peer_id} from active downloads for piece {index}"
                    )
                download_logger.logger.info(
                    f"Released semaphore, current value: {semaphore._value}"
                )

        while not self.stop_triggered and not self.torrent.isComplete():
            while self.connectionQueue:
                peer, index = self.connectionQueue.popleft()
                if not self.torrent.pieces[index].downloaded:
                    semaphore.acquire()
                    if self.stop_triggered:
                        semaphore.release()
                        break
                    download_logger.logger.info(
                        f"Acquired semaphore, current value: {semaphore._value}"
                    )
                    with lock:
                        self.active_download.append((peer, index))
                        download_logger.logger.info(
                            f"Added peer {peer.peer_id} to active downloads for piece {index}"
                        )
                    thread = threading.Thread(
                        target=download_wrapper, args=(peer, index)
                    )
                    threads.append(thread)
                    thread.start()

            threads = [t for t in threads if t.is_alive()]

            if not self.connectionQueue and not self.active_download:
                if not self.torrent.isComplete():
                    print("No more peers available. Retrying...")
                    time.sleep(5)  # Wait before retrying
                    self.fetchPeers(self.torrent.files)
                    continue  # Retry fetching peers
                else:
                    print("Download complete.")
                    break

            time.sleep(0.1)

        for thread in threads:
            thread.join()

        self.torrent.stopDownloadFromPeer()
        print("Download stopped.")
