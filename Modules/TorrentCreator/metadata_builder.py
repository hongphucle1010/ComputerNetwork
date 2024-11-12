class MetadataBuilder:
    def __init__(self, tracker_url, file_path, piece_size):
        self.tracker_url = tracker_url
        self.file_path = file_path
        self.piece_size = piece_size
        self.pieces = []
        self.piece_hashes = []

    def set_file_info(self):
        pass
    
    def build_metadata(self):
        pass
