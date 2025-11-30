#!/bin/bash
# Start the gallery viewer with auto-generated data

cd "$(dirname "$0")"

echo "Generating viewer data..."
python generate_viewer_data.py

echo ""
echo "Starting HTTP server on port 8000..."
echo "Open http://localhost:8000/viewer.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python server.py
