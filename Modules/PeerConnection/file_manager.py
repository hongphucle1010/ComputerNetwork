class FileManager:
    def __init__(self, torrent):
        self.filePath = "pieces"
        self.torrent = torrent

    def savePieces(self):
        print("Saving pieces...")

    def assembleFile(self, torrent):
        print("Assembling file...")
