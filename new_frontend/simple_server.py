#!/usr/bin/env python3
"""
Simple HTTP server for the frontend
Run this from the new_frontend directory
"""

import http.server
import socketserver
import os
import sys

PORT = 8080

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"🚀 Starting simple frontend server on port {PORT}")
    print(f"📁 Serving files from: {script_dir}")
    print(f"🌐 Open your browser to: http://localhost:{PORT}")
    print("=" * 50)
    print("⚠️  Note: This serves static files only.")
    print("   For full API functionality, use server.py instead.")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
