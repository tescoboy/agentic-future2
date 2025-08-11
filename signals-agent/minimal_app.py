#!/usr/bin/env python3
"""Minimal FastAPI app for Railway deployment - no complex dependencies."""

import os
from datetime import datetime

# Try to import FastAPI, but provide fallback if not available
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    print("Warning: FastAPI not available, using minimal fallback")
    FASTAPI_AVAILABLE = False

# Create FastAPI app if available
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Signals Agent API - Minimal",
        description="Minimal API for Railway deployment",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint for health checks."""
        return {
            "message": "Signals Agent API - Minimal",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    @app.get("/health", tags=["Health"])
    async def health():
        """Health check endpoint for Railway - must return HTTP 200 quickly."""
        return {"ok": True, "mode": "production"}
    
    @app.get("/test", tags=["Test"])
    async def test():
        """Test endpoint."""
        return {
            "message": "API is working!",
            "timestamp": datetime.now().isoformat()
        }
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        print(f"Starting minimal FastAPI app on port {port}")
        uvicorn.run("minimal_app:app", host="0.0.0.0", port=port, reload=False)

else:
    # Fallback: Simple HTTP server without FastAPI
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"ok": True, "mode": "production"}
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "message": "Signals Agent API - Minimal (Fallback)",
                    "status": "running",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Not found"}
                self.wfile.write(json.dumps(response).encode())
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
    
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8000))
        print(f"Starting fallback HTTP server on port {port}")
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        print(f"Server started at http://0.0.0.0:{port}")
        server.serve_forever()
