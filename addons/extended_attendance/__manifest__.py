{
    'name': 'Extended Attendance System',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Extended attendance system with multiple locations and person types',
    'description': """
Extended Attendance System
==========================

This module extends the standard Odoo attendance module to support:

Features:
---------
* Multiple attendance locations within a single premise
* Different person types (employees, students, guests, admins, etc.)
* Dynamic person type management
* Location-based attendance tracking
* Extended person profiles with custom fields
* REST API for external integrations
* Comprehensive reporting and analytics

Use Cases:
----------
* Schools with multiple buildings/rooms
* Offices with different departments/floors
* Events with multiple venues
* Any organization needing location-specific attendance

HTTP API Endpoints:
------------------
* Person Types: Create, read, update, delete person types
* Locations: Manage attendance locations
* Persons: Unified person management
* Attendance: Location-aware attendance tracking
    """,
    'depends': ['hr_attendance', 'hr', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/person_types_data.xml',

        'views/person_type_views.xml',
        'views/attendance_location_views.xml',
        'views/extended_person_views.xml',
        'views/extended_attendance_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],
    },
}
