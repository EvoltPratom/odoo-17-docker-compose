#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend and proxy API calls to Odoo
"""

import http.server
import socketserver
import json
import urllib.parse
import xmlrpc.client
from datetime import datetime, timedelta
import os

# Configuration
FRONTEND_PORT = 8081
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ODOO_USERNAME = 'admin@demo.com'
ODOO_PASSWORD = 'admin'

# Global session storage (in production, use proper session management)
class OdooSession:
    def __init__(self):
        self.uid = None
        self.models = None
        self.common = None
        self.is_connected = False

    def connect(self, url, db, username, password):
        try:
            self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(db, username, password, {})

            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                self.is_connected = True
                return True
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def is_authenticated(self):
        return self.is_connected and self.uid and self.models

# Global session instance
odoo_session = OdooSession()

class OdooProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Don't set directory in __init__, we'll handle it differently
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        """Handle GET requests for static files"""
        if self.path == '/':
            self.path = '/index.html'

        # Remove query parameters
        if '?' in self.path:
            self.path = self.path.split('?')[0]

        try:
            # Serve files from current directory
            file_path = self.path.lstrip('/')
            if not file_path:
                file_path = 'index.html'

            # Security check - don't allow directory traversal
            if '..' in file_path:
                self.send_error(403, "Forbidden")
                return

            # Check if file exists
            if os.path.exists(file_path):
                # Determine content type
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                else:
                    content_type = 'application/octet-stream'

                # Read and serve file
                with open(file_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, f"File not found: {file_path}")

        except Exception as e:
            print(f"Error serving file: {e}")
            self.send_error(500, f"Internal server error: {e}")

    def do_POST(self):
        """Handle POST requests for API calls"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(405, "Method not allowed")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def handle_api_request(self):
        """Handle API requests and proxy them to Odoo"""
        try:
            # Parse the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Route the request
            if self.path == '/api/connect':
                response = self.handle_connect(request_data)
            elif self.path == '/api/call':
                response = self.handle_odoo_call(request_data)
            else:
                response = {'success': False, 'error': 'Unknown API endpoint'}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"API Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def handle_connect(self, request_data):
        """Handle connection to Odoo"""
        try:
            url = request_data.get('url', ODOO_URL)
            db = request_data.get('db', ODOO_DB)
            username = request_data.get('username', ODOO_USERNAME)
            password = request_data.get('password', ODOO_PASSWORD)

            print(f"Connecting to Odoo: {url}, DB: {db}, User: {username}")

            # Use global session
            if odoo_session.connect(url, db, username, password):
                print(f"Connected successfully, UID: {odoo_session.uid}")
                return {'success': True, 'uid': odoo_session.uid}
            else:
                return {'success': False, 'error': 'Authentication failed'}

        except Exception as e:
            print(f"Connection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_odoo_call(self, request_data):
        """Handle Odoo API calls"""
        try:
            if not odoo_session.is_authenticated():
                return {'success': False, 'error': 'Not connected to Odoo'}

            model = request_data['model']
            method = request_data['method']
            args = request_data.get('args', [])
            kwargs = request_data.get('kwargs', {})

            print(f"Odoo API Call: {model}.{method}({args}, {kwargs})")

            # Make the call to Odoo using global session
            result = odoo_session.models.execute_kw(
                ODOO_DB, odoo_session.uid, ODOO_PASSWORD,
                model, method, args, kwargs
            )

            return {'success': True, 'result': result}

        except Exception as e:
            print(f"Odoo call error: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Start the server"""
    print(f"🚀 Starting frontend server on port {FRONTEND_PORT}")
    print(f"📡 Proxying API calls to Odoo at {ODOO_URL}")
    print(f"🌐 Open your browser to: http://localhost:{FRONTEND_PORT}")
    print("=" * 50)
    
    with socketserver.TCPServer(("", FRONTEND_PORT), OdooProxyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
