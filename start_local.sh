#!/bin/bash
echo "==================================================="
echo "   UNIVERSAL BI GOVERNANCE HUB BOOTSTRAP"
echo "==================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker is not running! Please open Docker Desktop and try again."
  exit 1
fi

echo "[1/3] Building Docker Container..."
docker build -t bi-gov-hub .

echo "[2/3] Opening Web Browser..."
# Background process to open browser after 3 seconds
(sleep 3 && open http://localhost:8501 || xdg-open http://localhost:8501) &

echo "[3/3] Launching Application Server..."
echo "(Press CTRL+C in this terminal to safely shut down the app)"
echo ""
# Runs the container and mounts the current directory
docker run --rm -p 8501:8501 -v "$(pwd):/app" bi-gov-hub