from piece import Piece


class Peer:
    def __init__(self, peer_id, ip, port):
        self.peer_id = peer_id
        self.ip = ip
        self.port = port

    def downloadPieces(self, piece: Piece):
        print(f"Downloading piece {piece.index} from {self.ip}:{self.port}")
        print("Piece downloaded successfully")
        piece.setData(b"Piece data")  # Fake piece data
        