import threading
import time
import schedule
import requests
from configuration import Configuration


class Announcer:
    def __init__(self, configs: Configuration, ip: str):
        self.configs = configs
        self.ip = ip
        self.thread = None
        self.stop_triggered = False

    def announce(self):
        # Send put request to tracker_url with ip, peer_id and port
        response = requests.put(
            self.configs.tracker_url + "/api/announce",
            json={
                "peerId": self.configs.peer_id,
                "ip": self.ip,
                "port": self.configs.port,
                "torrents": [
                    {"torrentId": "6734f7a6d04a4e80469e5d32", "pieceIndexes": [1]}
                ],
            },
        )
        if response.status_code == 200:
            # print("Announce successful")
            pass
        else:
            print("Announce failed")

    def announce_every_interval(self):
        while not self.stop_triggered:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.announce()
        schedule.every(self.configs.refresh_interval).seconds.do(self.announce)
        if self.thread is None:
            self.thread = threading.Thread(target=self.announce_every_interval)
            self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.stop_triggered = True
            self.thread.join()
            self.thread = None
            self.stop_triggered = False


if __name__ == "__main__":
    announcer = Announcer("http://localhost:3000", "peer_id", "localhost", 3)
    announcer.start()
    time.sleep(10)
    announcer.stop()
