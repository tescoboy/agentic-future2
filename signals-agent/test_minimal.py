#!/usr/bin/env python3
"""Test the minimal app locally."""

import subprocess
import time
import requests
import sys

def test_minimal_app():
    """Test the minimal app locally."""
    print("🧪 Testing minimal app...")
    
    # Start the server
    print("🚀 Starting minimal app...")
    process = subprocess.Popen([
        sys.executable, "minimal_app.py"
    ], cwd=".")
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        print("🔍 Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health response: {response.status_code} - {response.json()}")
        
        # Test root endpoint
        print("🔍 Testing / endpoint...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Root response: {response.status_code} - {response.json()}")
        
        # Test test endpoint
        print("🔍 Testing /test endpoint...")
        response = requests.get("http://localhost:8000/test", timeout=5)
        print(f"✅ Test response: {response.status_code} - {response.json()}")
        
        print("🎉 All tests passed!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_minimal_app()
