#!/bin/bash
# Quick Start Script for Jetson POS System

echo "========================================"
echo "  Jetson POS System - Quick Start"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    
    echo -e "${YELLOW}Installing dependencies...${NC}"
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ Setup complete!${NC}"
else
    echo -e "${GREEN}✓ Virtual environment found${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if YOLO model exists
if [ ! -f "yolov8n.pt" ]; then
    echo -e "${YELLOW}Downloading YOLO model (first time only)...${NC}"
    python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
fi

# Start server
echo ""
echo -e "${GREEN}Starting POS server...${NC}"
echo ""
echo "Access the POS system at:"
echo "  → http://localhost:8000/pos.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py
