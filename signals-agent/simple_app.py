#!/usr/bin/env python3
"""Simple FastAPI app for Railway deployment - bulletproof health check."""

import os

# Create FastAPI app immediately - this must work
try:
    from fastapi import FastAPI
    app = FastAPI()
except ImportError:
    # Fallback if FastAPI is not available (shouldn't happen on Railway)
    print("Warning: FastAPI not available, using minimal fallback")
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"ok": True, "mode": "production"}
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"message": "Signals Agent API", "status": "running"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Not found"}
                self.wfile.write(json.dumps(response).encode())
    
    # Create a minimal app-like object for fallback
    class MinimalApp:
        def __init__(self):
            self.handler = SimpleHandler
    
    app = MinimalApp()

# Health endpoint at the very top - must respond instantly
@app.get("/health")
async def health():
    """Health check endpoint that returns HTTP 200 when application is live and ready."""
    return {"ok": True, "mode": "production"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Signals Agent API", "status": "running"}

# Only call uvicorn.run inside if __name__ == "__main__"
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=False)
