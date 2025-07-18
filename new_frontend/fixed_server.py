#!/usr/bin/env python3
"""
Fixed HTTP server for Odoo frontend with proper session management
"""

import http.server
import socketserver
import json
import xmlrpc.client
import os

# Configuration
PORT = 8080
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'attendance_test'
ODOO_USERNAME = 'bishantad@gmail.com'
ODOO_PASSWORD = '12345'

# Global connection state
connection_state = {
    'uid': None,
    'models': None,
    'common': None,
    'connected': False
}

class FixedOdooHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Serve static files"""
        if self.path == '/':
            self.path = '/index.html'
        
        # Remove query parameters
        if '?' in self.path:
            self.path = self.path.split('?')[0]
        
        file_path = self.path.lstrip('/')
        if not file_path:
            file_path = 'index.html'
        
        # Security check
        if '..' in file_path:
            self.send_error(403, "Forbidden")
            return
        
        try:
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
                
                # Serve file
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, f"File not found: {file_path}")
        except Exception as e:
            print(f"Error serving file: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle API requests"""
        if not self.path.startswith('/api/'):
            self.send_error(405, "Method not allowed")
            return
        
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            # Route request
            if self.path == '/api/connect':
                response = self.handle_connect(request_data)
            elif self.path == '/api/call':
                response = self.handle_call(request_data)
            else:
                response = {'success': False, 'error': 'Unknown endpoint'}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"API Error: {e}")
            error_response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_connect(self, request_data):
        """Connect to Odoo"""
        global connection_state
        
        try:
            url = request_data.get('url', ODOO_URL)
            db = request_data.get('db', ODOO_DB)
            username = request_data.get('username', ODOO_USERNAME)
            password = request_data.get('password', ODOO_PASSWORD)
            
            print(f"🔌 Connecting to Odoo: {url}, DB: {db}, User: {username}")
            
            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            
            if uid:
                models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                
                # Update global state
                connection_state.update({
                    'uid': uid,
                    'models': models,
                    'common': common,
                    'connected': True
                })
                
                print(f"✅ Connected successfully, UID: {uid}")
                return {'success': True, 'uid': uid}
            else:
                connection_state['connected'] = False
                return {'success': False, 'error': 'Authentication failed'}
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            connection_state['connected'] = False
            return {'success': False, 'error': str(e)}
    
    def handle_call(self, request_data):
        """Handle Odoo API calls"""
        global connection_state
        
        try:
            if not connection_state['connected'] or not connection_state['uid']:
                return {'success': False, 'error': 'Not connected to Odoo'}
            
            model = request_data.get('model')
            method = request_data.get('method')
            args = request_data.get('args', [])
            kwargs = request_data.get('kwargs', {})
            
            if not model or not method:
                return {'success': False, 'error': 'Missing model or method'}
            
            print(f"📡 API Call: {model}.{method}({args}, {kwargs})")
            
            # Make the call
            result = connection_state['models'].execute_kw(
                ODOO_DB, connection_state['uid'], ODOO_PASSWORD,
                model, method, args, kwargs
            )
            
            print(f"✅ API Call successful, result: {type(result)} with {len(result) if isinstance(result, list) else 'N/A'} items")
            return {'success': True, 'result': result}
            
        except Exception as e:
            print(f"❌ API Call error: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Start the server"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"🚀 Starting fixed Odoo frontend server")
    print(f"📁 Serving files from: {script_dir}")
    print(f"🌐 Server URL: http://localhost:{PORT}")
    print(f"📡 Odoo URL: {ODOO_URL}")
    print(f"🗄️  Database: {ODOO_DB}")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), FixedOdooHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
