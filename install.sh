pip install -r requirements.txt
mkdir torrents
mkdir downloads
mkdir pieces

echo '{
    "tracker_url": "http://localhost:3000",
    "peer_id": "6739aa0012fe9a48a2cbbcd9",
    "download_dir": "downloads",
    "max_connections": 100,
    "refresh_interval": 5,
    "port": 6881
}' >configs.json
