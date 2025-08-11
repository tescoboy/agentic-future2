#!/usr/bin/env python3
"""Simple HTTP server for Railway deployment - built-in Python only."""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class SimpleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to avoid noise
        pass
    
    def do_GET(self):
        try:
            if self.path == "/health":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"ok": True, "mode": "production"}
                self.wfile.write(json.dumps(response).encode())
                self.wfile.flush()
                
            elif self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "message": "Signals Agent API", 
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
                self.wfile.flush()
                
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Not found"}
                self.wfile.write(json.dumps(response).encode())
                self.wfile.flush()
                
        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Internal server error"}
            self.wfile.write(json.dumps(response).encode())
            self.wfile.flush()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting simple HTTP server on port {port}")
    
    try:
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        print(f"Server started successfully at http://0.0.0.0:{port}")
        print(f"Health check available at: http://0.0.0.0:{port}/health")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start server: {e}")
        exit(1)
