#!/bin/bash
# Imou Gateway v2.0.0 Startup Script

echo "Starting Imou Gateway v2.0.0..."
cd "$(dirname "$0")"

# Create database folder if not exists
mkdir -p database
mkdir -p images

# Run the Flask app
python app.py
