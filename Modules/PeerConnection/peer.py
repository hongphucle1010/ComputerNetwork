from Modules.PeerConnection.piece import Piece
import socket
from log import download_logger


class Peer:
    def __init__(self, peer_id, ip, port):
        self.peer_id = peer_id
        self.ip = ip
        self.port = port

    def downloadPieces(self, piece: Piece, timeout: int = 30):
        """
        Downloads the specified piece from the peer with a timeout.

        Args:
            piece (Piece): The piece to download.
            timeout (int): The timeout in seconds for socket operations.

        Raises:
            TimeoutError: If the download operation times out.
            Exception: For other socket-related issues.
        """
        try:
            # Create a socket and set a timeout
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(
                timeout
            )  # Set the timeout for all socket operations
            client_socket.connect((self.ip, self.port))

            # Send the fileName to the server
            client_socket.sendall(piece.getFileName().encode("utf-8"))

            # Receive the file data
            file_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                file_data += chunk

            # Save the file locally
            if file_data.startswith(b"ERROR"):
                download_logger.logger.error(file_data.decode("utf-8"))
            else:
                piece.setData(file_data)
                download_logger.logger.info(
                    f"Downloaded piece {piece.getFileName()} from {self.ip}:{self.port}"
                )
        except socket.timeout:
            download_logger.logger.warning(
                f"Download of piece {piece.getFileName()} from {self.ip}:{self.port} timed out."
            )
            raise TimeoutError(
                f"Timeout occurred while downloading piece {piece.getFileName()}"
            )
        except Exception as e:
            download_logger.logger.error(f"Error downloading piece: {e}")
        finally:
            client_socket.close()
