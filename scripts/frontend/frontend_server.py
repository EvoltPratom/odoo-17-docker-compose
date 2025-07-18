#!/usr/bin/env python3
"""
Simple HTTP server to serve the new_frontend_v2 and provide API proxy to Odoo
"""

import http.server
import socketserver
import json
import urllib.parse
import xmlrpc.client
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
ODOO_URL = "http://localhost:10017"
ODOO_DB = "extended_attendance"
ODOO_USERNAME = "admin@demo.com"
ODOO_PASSWORD = "admin"

class OdooAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        frontend_dir = Path(__file__).parent.parent.parent / "new_frontend_v2"
        os.chdir(frontend_dir)
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(405, "Method Not Allowed")
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def handle_api_request(self):
        try:
            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

            if not uid:
                self.send_error_response("Authentication failed")
                return

            # Handle different API endpoints
            if self.path == '/api/connect':
                self.handle_connect(models, uid)
            elif self.path == '/api/attendance/person-types':
                self.handle_person_types(models, uid)
            elif self.path == '/api/attendance/locations':
                self.handle_locations(models, uid)
            elif self.path == '/api/attendance/persons':
                self.handle_persons(models, uid)
            elif self.path == '/api/attendance/check-in':
                self.handle_check_in(models, uid)
            elif self.path == '/api/attendance/persons' and self.command == 'POST':
                self.handle_create_person(models, uid)
            elif self.path == '/api/attendance/current':
                self.handle_current_attendance(models, uid)
            elif self.path == '/api/attendance/check-out':
                self.handle_check_out(models, uid)
            else:
                self.send_error_response("Endpoint not found")

        except Exception as e:
            self.send_error_response(str(e))

    def handle_connect(self, models, uid):
        """Handle connection request from frontend"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Since we already authenticated to get here, just return success
            # Return empty string for URL so frontend uses relative paths
            self.send_json_response({
                'success': True,
                'uid': uid,
                'session_id': 'proxy_session',
                'url': '',  # Use relative paths
                'message': 'Connected via proxy server'
            })

        except Exception as e:
            self.send_error_response(str(e))

    def handle_person_types(self, models, uid):
        try:
            person_types = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'person.type', 'search_read',
                [[]], {'fields': ['name', 'code', 'description', 'default_access_level', 'active', 'is_system']}
            )
            
            data = []
            for pt in person_types:
                # Count persons of this type
                person_count = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'extended.attendance.person', 'search_count',
                    [[('person_type_id', '=', pt['id'])]]
                )
                
                data.append({
                    'id': pt['id'],
                    'name': pt['name'],
                    'code': pt['code'],
                    'description': pt['description'] or '',
                    'access_level': pt['default_access_level'],
                    'default_access_level': pt['default_access_level'],
                    'active': pt['active'],
                    'is_system': pt['is_system'],
                    'person_count': person_count
                })
            
            self.send_json_response({'success': True, 'data': data})
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_locations(self, models, uid):
        try:
            locations = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'attendance.location', 'search_read',
                [[('active', '=', True)]],
                {'fields': ['name', 'code', 'capacity', 'current_occupancy', 'building', 'floor', 'active',
                           'parent_location_id'], 'order': 'sequence, name'}
            )
            
            # Build hierarchy information manually
            location_map = {loc['id']: loc for loc in locations}

            def calculate_level(loc_id, visited=None):
                if visited is None:
                    visited = set()
                if loc_id in visited:
                    return 0  # Prevent infinite recursion
                visited.add(loc_id)

                loc = location_map.get(loc_id)
                if not loc or not loc['parent_location_id']:
                    return 0
                return 1 + calculate_level(loc['parent_location_id'][0], visited)

            def build_path(loc_id, visited=None):
                if visited is None:
                    visited = set()
                if loc_id in visited:
                    return ""
                visited.add(loc_id)

                loc = location_map.get(loc_id)
                if not loc:
                    return ""
                if not loc['parent_location_id']:
                    return loc['name']
                parent_path = build_path(loc['parent_location_id'][0], visited)
                return f"{parent_path} / {loc['name']}" if parent_path else loc['name']

            data = []
            for loc in locations:
                level = calculate_level(loc['id'])
                path = build_path(loc['id'])

                data.append({
                    'id': loc['id'],
                    'name': loc['name'],
                    'code': loc['code'],
                    'capacity': loc['capacity'],
                    'current_occupancy': loc['current_occupancy'],
                    'building': loc['building'] or '',
                    'floor': loc['floor'] or '',
                    'active': loc['active'],
                    'parent_location_id': loc['parent_location_id'][0] if loc['parent_location_id'] else None,
                    'parent_location_name': loc['parent_location_id'][1] if loc['parent_location_id'] else None,
                    'level': level,
                    'location_path': path
                })

            # Sort by level and name for hierarchical display
            data.sort(key=lambda x: (x['level'], x['name']))
            
            self.send_json_response({'success': True, 'data': data})
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_persons(self, models, uid):
        try:
            persons = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'search_read',
                [[]], 
                {'fields': ['name', 'person_id', 'person_type_id', 'email', 'phone', 'active']}
            )
            
            data = []
            for person in persons:
                # Get person type info
                person_type = {'name': '', 'code': ''}
                if person['person_type_id']:
                    pt_info = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'person.type', 'read',
                        [person['person_type_id'][0]], {'fields': ['name', 'code']}
                    )
                    if pt_info:
                        person_type = {'name': pt_info[0]['name'], 'code': pt_info[0]['code']}
                
                # Check current attendance status
                current_attendance = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'extended.attendance.record', 'search_read',
                    [[('person_id', '=', person['id']), ('state', '=', 'checked_in')]],
                    {'fields': ['location_id'], 'limit': 1}
                )
                
                is_checked_in = bool(current_attendance)
                current_location = None
                if current_attendance and current_attendance[0]['location_id']:
                    loc_info = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'attendance.location', 'read',
                        [current_attendance[0]['location_id'][0]], {'fields': ['name', 'code']}
                    )
                    if loc_info:
                        current_location = {'name': loc_info[0]['name'], 'code': loc_info[0]['code']}
                
                data.append({
                    'id': person['id'],
                    'name': person['name'],
                    'person_id': person['person_id'],
                    'person_type': person_type,
                    'is_checked_in': is_checked_in,
                    'current_location': current_location,
                    'email': person['email'] or '',
                    'phone': person['phone'] or '',
                    'active': person['active']
                })
            
            self.send_json_response({'success': True, 'data': data})
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_check_in(self, models, uid):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            person_identifier = data.get('person_identifier')
            location_code = data.get('location_code')
            
            if not person_identifier or not location_code:
                self.send_error_response('person_identifier and location_code are required')
                return
            
            # Find person
            person_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'search',
                [[('person_id', '=', person_identifier)]]
            )
            
            if not person_ids:
                self.send_error_response(f'Person not found with identifier: {person_identifier}')
                return
            
            # Find location
            location_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'attendance.location', 'search',
                [[('code', '=', location_code)]]
            )
            
            if not location_ids:
                self.send_error_response(f'Location not found with code: {location_code}')
                return
            
            # Check if person is already checked in somewhere else
            person_id = person_ids[0]
            location_id = location_ids[0]

            # Check current status
            existing_checkin = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.record', 'search_read',
                [[('person_id', '=', person_id), ('check_out', '=', False)]],
                {'fields': ['location_id'], 'limit': 1}
            )

            is_transfer = bool(existing_checkin)
            previous_location = existing_checkin[0]['location_id'][1] if existing_checkin else None

            # Create attendance record using the person's method
            attendance_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'create_attendance',
                [person_id, location_id, 'check_in']
            )

            # Get the created attendance record
            attendance = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.record', 'read',
                [attendance_id], {'fields': ['person_name', 'location_name', 'check_in', 'state']}
            )[0]

            # Create appropriate message
            if is_transfer:
                message = f'Successfully transferred {attendance["person_name"]} from {previous_location} to {attendance["location_name"]}'
            else:
                message = f'Successfully checked in {attendance["person_name"]} at {attendance["location_name"]}'

            self.send_json_response({
                'success': True,
                'message': message,
                'data': {
                    'id': attendance_id,
                    'person_name': attendance['person_name'],
                    'location_name': attendance['location_name'],
                    'check_in': attendance['check_in'],
                    'state': attendance['state'],
                    'is_transfer': is_transfer,
                    'previous_location': previous_location
                }
            })
            
        except Exception as e:
            self.send_error_response(str(e))

    def handle_create_person(self, models, uid):
        """Handle creating a new person"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Create the person record
            person_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'create',
                [{
                    'name': data.get('name'),
                    'person_id': data.get('person_id'),
                    'person_type_id': int(data.get('person_type_id')),
                    'email': data.get('email', ''),
                    'phone': data.get('phone', ''),
                    'active': True
                }]
            )

            # Get the created person record
            person = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'read',
                [person_id], {'fields': ['name', 'person_id', 'person_type_id', 'email', 'phone', 'active']}
            )[0]

            self.send_json_response({
                'success': True,
                'message': f'Person {person["name"]} created successfully',
                'data': {
                    'id': person_id,
                    'name': person['name'],
                    'person_id': person['person_id'],
                    'person_type_id': person['person_type_id'][0] if person['person_type_id'] else None,
                    'email': person['email'],
                    'phone': person['phone'],
                    'active': person['active']
                }
            })

        except Exception as e:
            self.send_error_response(str(e))

    def handle_check_out(self, models, uid):
        """Handle checking out a person"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            person_identifier = data.get('person_identifier')

            if not person_identifier:
                self.send_error_response('person_identifier is required')
                return

            # Find person
            person_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'search',
                [[('person_id', '=', person_identifier)]]
            )

            if not person_ids:
                self.send_error_response(f'Person not found with identifier: {person_identifier}')
                return

            # Check out using the person's method
            person_id = person_ids[0]

            attendance_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'create_attendance',
                [person_id, 0, 'check_out']  # location_id=0 for check_out
            )

            # Get the updated attendance record
            attendance = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.record', 'read',
                [attendance_id], {'fields': ['person_name', 'location_name', 'check_out', 'state']}
            )[0]

            self.send_json_response({
                'success': True,
                'message': f'Successfully checked out {attendance["person_name"]}',
                'data': {
                    'id': attendance_id,
                    'person_name': attendance['person_name'],
                    'location_name': attendance['location_name'],
                    'check_out': attendance['check_out'],
                    'state': attendance['state']
                }
            })

        except Exception as e:
            self.send_error_response(str(e))

    def handle_current_attendance(self, models, uid):
        """Handle getting current attendance records"""
        try:
            # Get all current attendance records (checked in) with hierarchy info
            current_records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.record', 'search_read',
                [[('state', '=', 'checked_in')]],
                {'fields': ['person_id', 'location_id', 'check_in', 'person_name', 'location_name',
                           'auto_action', 'notes'], 'order': 'person_name, check_in'}
            )

            data = []
            for record in current_records:
                data.append({
                    'id': record['id'],
                    'person_id': record['person_id'][0] if record['person_id'] else None,
                    'person_name': record['person_name'],
                    'location_id': record['location_id'][0] if record['location_id'] else None,
                    'location_name': record['location_name'],
                    'check_in': record['check_in'],
                    'state': 'checked_in',
                    'auto_action': record.get('auto_action', 'manual'),
                    'notes': record.get('notes', ''),
                    'is_auto': record.get('auto_action', 'manual') != 'manual'
                })

            self.send_json_response({
                'success': True,
                'data': data,
                'count': len(data)
            })

        except Exception as e:
            self.send_error_response(str(e))

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, error_message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': error_message}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    print(f"🚀 Starting Frontend Server on port {PORT}")
    print(f"📁 Serving files from: new_frontend_v2/")
    print(f"🔗 Proxying API calls to: {ODOO_URL}")
    print(f"🌐 Access the frontend at: http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), OdooAPIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
