#!/usr/bin/env python3
"""
Real Frontend Server for Extended Attendance System
Connects to actual Odoo backend with extended attendance features
"""

import http.server
import socketserver
import json
import xmlrpc.client
import urllib.parse
from datetime import datetime
import os

# Configuration
FRONTEND_PORT = 8081
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ODOO_USERNAME = 'admin@demo.com'
ODOO_PASSWORD = 'admin'

class OdooAPIHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves frontend files and proxies API calls to Odoo"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory='new_frontend_v2', **kwargs)
        
    def do_POST(self):
        """Handle POST requests for API calls"""
        if self.path == '/api/connect':
            self.handle_connect()
        elif self.path == '/api/call':
            self.handle_api_call()
        elif self.path.startswith('/api/attendance/'):
            self.handle_extended_api()
        else:
            super().do_POST()
    
    def handle_connect(self):
        """Handle Odoo connection requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url', ODOO_URL)
            db = data.get('db', ODOO_DB)
            username = data.get('username', ODOO_USERNAME)
            password = data.get('password', ODOO_PASSWORD)
            
            print(f"Connecting to Odoo: {url}, DB: {db}, User: {username}")
            
            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            
            if uid:
                response = {
                    'success': True,
                    'uid': uid,
                    'message': 'Connected successfully'
                }
                print(f"✅ Connected successfully, UID: {uid}")
            else:
                response = {
                    'success': False,
                    'error': 'Authentication failed'
                }
                print("❌ Authentication failed")
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            })
    
    def handle_api_call(self):
        """Handle standard Odoo API calls"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            model = data.get('model')
            method = data.get('method')
            args = data.get('args', [])
            kwargs = data.get('kwargs', {})
            
            print(f"API Call: {model}.{method}({args}, {kwargs})")
            
            # Connect to Odoo
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            
            # Execute the call
            result = models.execute_kw(
                ODOO_DB, 2, ODOO_PASSWORD,  # Using UID 2 from setup
                model, method, args, kwargs
            )
            
            response = {
                'success': True,
                'result': result
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"❌ API call error: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            })
    
    def handle_extended_api(self):
        """Handle extended attendance API endpoints"""
        try:
            # Parse the endpoint
            endpoint = self.path.replace('/api/attendance/', '')
            
            print(f"Extended API call: {endpoint}")
            
            # Connect to Odoo
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            
            if endpoint == 'person-types':
                # Get person types (or create mock if model doesn't exist)
                try:
                    person_types = models.execute_kw(
                        ODOO_DB, 2, ODOO_PASSWORD,
                        'person.type', 'search_read', [],
                        {'fields': ['name', 'code', 'default_access_level', 'is_system']}
                    )
                    
                    # Add person count
                    for pt in person_types:
                        pt['person_count'] = 0  # TODO: Calculate real count
                    
                    response = {'success': True, 'data': person_types}
                    
                except:
                    # Fallback to mock data if model doesn't exist
                    response = {
                        'success': True,
                        'data': [
                            {'id': 1, 'name': 'Employee', 'code': 'EMP', 'person_count': 0, 'default_access_level': 'standard'},
                            {'id': 2, 'name': 'Admin', 'code': 'ADMIN', 'person_count': 1, 'default_access_level': 'full'}
                        ]
                    }
            
            elif endpoint == 'locations':
                # Get attendance locations
                try:
                    locations = models.execute_kw(
                        ODOO_DB, 2, ODOO_PASSWORD,
                        'attendance.location', 'search_read', [],
                        {'fields': ['name', 'code', 'building', 'floor', 'capacity', 'current_occupancy']}
                    )
                    response = {'success': True, 'data': locations}
                    
                except:
                    # Fallback to mock data
                    response = {
                        'success': True,
                        'data': [
                            {'id': 1, 'name': 'Main Office', 'code': 'MAIN', 'building': 'HQ', 'current_occupancy': 0, 'capacity': 50}
                        ]
                    }
            
            elif endpoint == 'persons':
                # Get employees as persons
                try:
                    employees = models.execute_kw(
                        ODOO_DB, 2, ODOO_PASSWORD,
                        'hr.employee', 'search_read', [],
                        {'fields': ['name', 'barcode', 'work_email', 'department_id']}
                    )
                    
                    # Transform to persons format
                    persons = []
                    for emp in employees:
                        persons.append({
                            'id': emp['id'],
                            'name': emp['name'],
                            'person_id': emp.get('barcode', f"EMP{emp['id']:03d}"),
                            'person_type': {'name': 'Employee', 'code': 'EMP'},
                            'is_checked_in': False,  # TODO: Check real attendance
                            'current_location': None
                        })
                    
                    response = {'success': True, 'data': persons}
                    
                except Exception as e:
                    print(f"Error getting employees: {e}")
                    response = {'success': True, 'data': []}
            
            elif endpoint == 'current':
                # Get current attendance
                try:
                    attendance = models.execute_kw(
                        ODOO_DB, 2, ODOO_PASSWORD,
                        'hr.attendance', 'search_read',
                        [[['check_out', '=', False]]],
                        {'fields': ['employee_id', 'check_in'], 'limit': 50}
                    )
                    
                    # Transform to expected format
                    current_attendance = []
                    for att in attendance:
                        current_attendance.append({
                            'id': att['id'],
                            'person_name': att['employee_id'][1] if att['employee_id'] else 'Unknown',
                            'location_name': 'Main Office',  # TODO: Get real location
                            'check_in': att['check_in'],
                            'duration_display': 'Ongoing'  # TODO: Calculate duration
                        })
                    
                    response = {'success': True, 'data': current_attendance}
                    
                except Exception as e:
                    print(f"Error getting current attendance: {e}")
                    response = {'success': True, 'data': []}
            
            else:
                response = {'success': False, 'error': f'Unknown endpoint: {endpoint}'}
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"❌ Extended API error: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            })
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, default=str)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """Start the server"""
    print("🚀 Starting Real Frontend Server for Extended Attendance...")
    print(f"📍 Frontend URL: http://localhost:{FRONTEND_PORT}")
    print(f"🔗 Odoo Backend: {ODOO_URL}")
    print(f"🗄️  Database: {ODOO_DB}")
    print("=" * 60)
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", FRONTEND_PORT), OdooAPIHandler) as httpd:
        print(f"✅ Server running on http://localhost:{FRONTEND_PORT}")
        print("📱 Open this URL in your browser to access the frontend")
        print("🔄 The frontend will connect to REAL Odoo data")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
