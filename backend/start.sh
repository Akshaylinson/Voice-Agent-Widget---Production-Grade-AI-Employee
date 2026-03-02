#!/bin/bash

# Start FastAPI backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 5

# Serve widget files using Python HTTP server
cd /app/widget
python3 -m http.server 8080 &

# Keep container running
wait
