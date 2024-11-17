from program import Program
import sys
from Modules.TorrentCreator.torrent_creator import TorrentCreator

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            # Read file help.txt and print its contents
            with open("help.txt", "r") as f:
                print(f.read())
        elif sys.argv[1] == "--version" or sys.argv[1] == "-v":
            print("Version 1.0")
            
    else:
        program = Program()
        program.start()
