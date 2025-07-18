{
    'name': 'Attendance Export',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Export attendance data to JSON files',
    'description': """
This module provides functionality to export attendance data from the Odoo attendance module to JSON files.
Features:
- Export attendance records to JSON
- Configurable export location
- Manual and automatic export options
    """,
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_export_views.xml',
        'views/hr_attendance_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
