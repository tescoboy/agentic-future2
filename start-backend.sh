#!/bin/bash

# Signals Agent Backend Starter Script
# This script can be run from any directory and will automatically navigate to the backend directory

echo "🚀 Starting Signals Agent Backend..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/signals-agent"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

# Check if simple_app.py exists
if [ ! -f "$BACKEND_DIR/simple_app.py" ]; then
    echo "❌ Error: simple_app.py not found in backend directory"
    exit 1
fi

echo "📍 Navigating to backend directory: $BACKEND_DIR"
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "🚀 Starting FastAPI server..."
uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload
