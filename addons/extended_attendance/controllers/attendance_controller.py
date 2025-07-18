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
        """Get all person types"""
        try:
            person_types = request.env['person.type'].sudo().search([])
            data = []

            for person_type in person_types:
                data.append({
                    'id': person_type.id,
                    'name': person_type.name,
                    'description': person_type.description or '',
                    'access_level': person_type.access_level,
                    'active': person_type.active
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
                'GET /api/locations'
            ]
        })
