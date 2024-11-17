import json
import requests
import socket

configs_file = "configs.json"


class Configuration:
    def __init__(self):
        self.peer_id = None
        self.load()

    def load(self):
        with open(configs_file, "r") as f:
            data = json.load(f)
            self.tracker_url = data["tracker_url"]
            self.download_dir = data["download_dir"]
            self.max_connections = data["max_connections"]
            self.refresh_interval = data["refresh_interval"]
            self.port = data["port"]
            if "peer_id" in data:
                self.peer_id = data["peer_id"]
        if self.peer_id is None:
            self.registerPeer()

    def save(self):
        with open(configs_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self):
        return {
            "tracker_url": self.tracker_url,
            "peer_id": self.peer_id,
            "download_dir": self.download_dir,
            "max_connections": self.max_connections,
            "refresh_interval": self.refresh_interval,
            "port": self.port,
        }

    def save(self):
        with open(configs_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def registerPeer(self):
        response = requests.post(
            f"{self.tracker_url}/api/register-peer",
            json={"ip": socket.gethostbyname(socket.gethostname()), "port": self.port},
        )
        self.peer_id = response.json()["insertedId"]
        self.save()
        return response.json()["insertedId"]


# Dòng dưới dùng để testing thôi nhen ...
if __name__ == "__main__":
    config = Configuration()
    print(config.to_dict())
    config.save()
    print("Configuration saved.")
