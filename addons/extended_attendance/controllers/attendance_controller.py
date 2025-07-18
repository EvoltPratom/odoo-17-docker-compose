from odoo import http
from odoo.http import request
import json


class AttendanceController(http.Controller):
    """Simple HTTP API controller for Extended Attendance module"""

    def _json_response(self, data):
        """Helper method to return JSON response"""
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/person-types', type='http', auth='public', methods=['GET'], csrf=False)
    def get_person_types(self, **kwargs):
        """Get all person types (legacy endpoint)"""
        return self.get_attendance_person_types(**kwargs)

    @http.route('/api/attendance/person-types', type='http', auth='public', methods=['GET'], csrf=False)
    def get_attendance_person_types(self, **kwargs):
        """Get all person types"""
        try:
            person_types = request.env['person.type'].sudo().search([])
            data = []

            for person_type in person_types:
                # Count persons of this type
                person_count = request.env['extended.attendance.person'].sudo().search_count([
                    ('person_type_id', '=', person_type.id)
                ])

                data.append({
                    'id': person_type.id,
                    'name': person_type.name,
                    'code': person_type.code,
                    'description': person_type.description or '',
                    'access_level': person_type.access_level,
                    'default_access_level': person_type.access_level,
                    'active': person_type.active,
                    'is_system': person_type.code in ['ADMIN', 'OWNER'],
                    'person_count': person_count
                })

            return self._json_response({
                'success': True,
                'data': data,
                'count': len(data)
            })

        except Exception as e:
            return self._json_response({
                'success': False,
                'error': str(e)
            })

    @http.route('/api/locations', type='http', auth='public', methods=['GET'], csrf=False)
    def get_locations(self, **kwargs):
        """Get all locations (legacy endpoint)"""
        return self.get_attendance_locations(**kwargs)

    @http.route('/api/attendance/locations', type='http', auth='public', methods=['GET'], csrf=False)
    def get_attendance_locations(self, **kwargs):
        """Get all locations"""
        try:
            locations = request.env['attendance.location'].sudo().search([('active', '=', True)])
            data = []

            for location in locations:
                data.append({
                    'id': location.id,
                    'name': location.name,
                    'code': location.code,
                    'capacity': location.capacity,
                    'current_occupancy': location.current_occupancy,
                    'building': location.building or '',
                    'floor': location.floor or '',
                    'active': location.active
                })

            return self._json_response({
                'success': True,
                'data': data,
                'count': len(data)
            })

        except Exception as e:
            return self._json_response({
                'success': False,
                'error': str(e)
            })



    @http.route('/api/attendance/persons', type='http', auth='public', methods=['GET'], csrf=False)
    def get_attendance_persons(self, **kwargs):
        """Get all extended persons"""
        try:
            persons = request.env['extended.attendance.person'].sudo().search([])
            data = []

            for person in persons:
                # Check if person is currently checked in
                current_attendance = request.env['extended.attendance'].sudo().search([
                    ('person_id', '=', person.id),
                    ('state', '=', 'checked_in')
                ], limit=1)

                is_checked_in = bool(current_attendance)
                current_location = None
                if current_attendance and current_attendance.location_id:
                    current_location = {
                        'name': current_attendance.location_id.name,
                        'code': current_attendance.location_id.code
                    }

                data.append({
                    'id': person.id,
                    'name': person.name,
                    'person_id': person.person_id,
                    'person_type': {
                        'name': person.person_type_id.name if person.person_type_id else '',
                        'code': person.person_type_id.code if person.person_type_id else ''
                    },
                    'is_checked_in': is_checked_in,
                    'current_location': current_location,
                    'email': person.email or '',
                    'phone': person.phone or '',
                    'active': person.active
                })

            return self._json_response({
                'success': True,
                'data': data,
                'count': len(data)
            })

        except Exception as e:
            return self._json_response({
                'success': False,
                'error': str(e)
            })

    @http.route('/api/attendance/check-in', type='http', auth='public', methods=['POST'], csrf=False)
    def attendance_check_in(self, **kwargs):
        """Check in a person"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            person_identifier = data.get('person_identifier')
            location_code = data.get('location_code')

            if not person_identifier or not location_code:
                return self._json_response({
                    'success': False,
                    'error': 'person_identifier and location_code are required'
                })

            # Find person
            person = request.env['extended.attendance.person'].sudo().search([
                ('person_id', '=', person_identifier)
            ], limit=1)

            if not person:
                return self._json_response({
                    'success': False,
                    'error': f'Person not found with identifier: {person_identifier}'
                })

            # Find location
            location = request.env['attendance.location'].sudo().search([
                ('code', '=', location_code)
            ], limit=1)

            if not location:
                return self._json_response({
                    'success': False,
                    'error': f'Location not found with code: {location_code}'
                })

            # Create attendance record
            attendance = person.create_attendance(location.id, 'check_in')

            return self._json_response({
                'success': True,
                'message': f'Successfully checked in {person.name} at {location.name}',
                'data': {
                    'id': attendance.id,
                    'person_name': attendance.person_name,
                    'location_name': attendance.location_name,
                    'check_in': attendance.check_in.isoformat() if attendance.check_in else None,
                    'state': attendance.state,
                }
            })

        except Exception as e:
            return self._json_response({
                'success': False,
                'error': str(e)
            })

    @http.route('/api/status', type='http', auth='public', methods=['GET'], csrf=False)
    def api_status(self, **kwargs):
        """Simple API status endpoint"""
        return self._json_response({
            'success': True,
            'message': 'Extended Attendance API is running',
            'version': '1.0',
            'endpoints': [
                'GET /api/status',
                'GET /api/person-types',
                'GET /api/locations',
                'GET /api/attendance/person-types',
                'GET /api/attendance/locations',
                'GET /api/attendance/persons',
                'POST /api/attendance/check-in'
            ]
        })
