from Modules.PeerConnection.piece import Piece
import time
import socket


class Peer:
    def __init__(self, peer_id, ip, port):
        self.peer_id = peer_id
        self.ip = ip
        self.port = port

    def downloadPieces(self, piece: Piece):
        # Send request to peer to download piece
        try:
            # Create a socket and connect to the server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                print(file_data.decode("utf-8"))
            else:
                piece.setData(file_data)
                print(
                    f"Downloaded piece {piece.getFileName()} from {self.ip}:{self.port}"
                )
        except Exception as e:
            print(f"Error downloading piece: {e}")
        finally:
            client_socket.close()
