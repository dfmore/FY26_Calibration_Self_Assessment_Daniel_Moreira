#!/usr/bin/env python3
"""
Local Development Server
Serves the index.html from the project root (same as GitHub Pages)
"""
import http.server
import socketserver
from pathlib import Path

# Set the directory to serve (project root, like GitHub Pages)
PORT = 8080
DIRECTORY = Path('.').resolve()

# Create a custom handler that serves from the specified directory
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

# Start the server
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"Serving from: {DIRECTORY}")
    print(f"\nOpen http://localhost:{PORT}/ in your browser")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()

