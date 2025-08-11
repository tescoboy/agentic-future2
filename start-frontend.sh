#!/bin/bash

# Signals Agent Frontend Starter Script
# This script can be run from any directory and will automatically navigate to the frontend directory

echo "🚀 Starting Signals Agent Frontend..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Check if package.json exists
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

echo "📍 Navigating to frontend directory: $FRONTEND_DIR"
cd "$FRONTEND_DIR"

echo "🔧 Starting development server..."
npm run dev:direct
