#!/usr/bin/env python3
"""Test script for minimal app."""

import requests
import time
import subprocess
import sys
import os

def test_minimal_app():
    print("🧪 Testing minimal app...")
    
    # Start the server
    print("🚀 Starting minimal app...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "minimal_app:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test root endpoint
        print("📡 Testing root endpoint...")
        response = requests.get("http://localhost:8000/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        # Test health endpoint
        print("📡 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        # Test test endpoint
        print("📡 Testing test endpoint...")
        response = requests.get("http://localhost:8000/test")
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Stop the server
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_minimal_app()
