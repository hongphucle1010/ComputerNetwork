@echo off

REM Step 1: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Please check your Python environment.
    exit /b 1
)

REM Step 2: Create directories
echo Creating directories...
mkdir torrents
mkdir downloads
mkdir pieces

REM Step 3: Create configs.json
echo Creating configs.json...
(
echo {
echo     "tracker_url": "http://localhost:3000",
echo     "download_dir": "downloads",
echo     "max_connections": 100,
echo     "refresh_interval": 5,
echo     "port": 6881
echo }
) > configs.json

REM Step 4: Confirm completion
echo Setup completed successfully!
pause
