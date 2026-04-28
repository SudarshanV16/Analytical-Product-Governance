#!/bin/bash
echo "==================================================="
echo "      UNIVERSAL BI GOVERNANCE HUB BOOTSTRAP"
echo "==================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker is not running! Please open Docker Desktop and try again."
  exit 1
fi

echo "[1/4] Building Docker Container..."
docker build -t bi-gov-hub .

echo "[2/4] Initializing Mock Database..."
# This runs the python script INSIDE docker, but saves the .db file back to your Mac folder!
docker run --rm -v "$(pwd):/app" bi-gov-hub python app/init_db.py

echo "[3/4] Opening Web Browser..."
# Increased sleep to 6 seconds so the container has time to start
(sleep 6 && open http://localhost:8501 || xdg-open http://localhost:8501) &

echo "[4/4] Launching Application Server..."
echo "(Press CTRL+C in this terminal to safely shut down the app)"
echo ""
# Runs the container and mounts the current directory
docker run --rm -p 8501:8501 -v "$(pwd):/app" bi-gov-hub