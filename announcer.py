class Announcer:
    def __init__(self, tracker_url, peer_id):
        self.tracker_url = tracker_url
        self.peer_id = peer_id

    def announce(self):
        print("Announcing to tracker...")
