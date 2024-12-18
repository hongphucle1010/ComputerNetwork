#!/bin/bash

# Step 1: Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check your Python environment."
    exit 1
fi

# Step 2: Create directories
echo "Creating directories..."
mkdir -p torrents downloads pieces logs

# Step 3: Create configs.json
echo "Creating configs.json..."
cat <<EOF > configs.json
{
    "tracker_url": "http://103.82.133.50:3000",
    "download_dir": "downloads",
    "max_connections": 100,
    "refresh_interval": 5,
    "port": 6881
}
EOF

# Step 4: Confirm completion
echo "Setup completed successfully!"
