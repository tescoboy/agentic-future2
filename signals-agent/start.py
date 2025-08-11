#!/usr/bin/env python3
"""Simple startup script for Railway deployment."""

import os
import sys
import subprocess
import time

def main():
    print("🚀 Starting Signals Agent...")
    
    # Check if we're in the right directory
    if not os.path.exists("simple_app.py"):
        print("❌ simple_app.py not found. Current directory:", os.getcwd())
        print("📁 Files in current directory:", os.listdir("."))
        sys.exit(1)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        print("✅ Required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        sys.exit(1)
    
    # Get port from environment
    port = os.getenv("PORT", "8000")
    print(f"🌐 Will start on port: {port}")
    print(f"🔗 Health check will be at: http://0.0.0.0:{port}/")
    
    # Start the server
    print("🚀 Starting uvicorn server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "simple_app:app", 
            "--host", "0.0.0.0", 
            "--port", port,
            "--log-level", "info"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
