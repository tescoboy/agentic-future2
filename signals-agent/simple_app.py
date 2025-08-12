#!/usr/bin/env python3
"""Simple Hello World server for Railway deployment."""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true, "mode": "production"}')
        elif self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Hello World!')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Hello World server on port {port}")
    
    server = HTTPServer(('0.0.0.0', port), HelloHandler)
    print(f"Server started at http://0.0.0.0:{port}")
    server.serve_forever()
