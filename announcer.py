import threading
import time
import schedule


class Announcer:
    def __init__(self, tracker_url, peer_id, ip, refresh_interval=300):
        self.tracker_url = tracker_url
        self.peer_id = peer_id
        self.refresh_interval = refresh_interval
        self.ip = ip
        self.thread = None
        self.stop_triggered = False

    def announce(self):
        print("Announcing to tracker with ip: ", self.ip)

    def announce_every_interval(self):
        while not self.stop_triggered:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.announce()
        schedule.every(self.refresh_interval).seconds.do(self.announce)
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
