#!/bin/bash

###############################################################################
# Manual Start Script
# Run the video server manually (useful for testing)
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting Jetson Camera Server..."
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run the installation script first:"
    echo "  ./scripts/install.sh"
    exit 1
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Check if dependencies are installed
if ! python -c "import fastapi" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r "$PROJECT_DIR/requirements.txt"
fi

# Start server
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

cd "$PROJECT_DIR"
python server.py
