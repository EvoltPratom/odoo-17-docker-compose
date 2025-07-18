from odoo import models, fields, api, _
from datetime import datetime, timedelta


class AttendanceExportWizard(models.TransientModel):
    _name = 'attendance.export.wizard'
    _description = 'Attendance Export Wizard'

    name = fields.Char('Export Name', required=True, 
                       default=lambda self: f'Export {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    export_path = fields.Char('Export Path', required=True, 
                              default='/tmp/attendance_exports',
                              help='Directory path where JSON files will be saved')
    date_from = fields.Date('Date From', required=True,
                           default=lambda self: fields.Date.today() - timedelta(days=30))
    date_to = fields.Date('Date To', required=True,
                         default=lambda self: fields.Date.today())
    employee_ids = fields.Many2many('hr.employee', string='Employees',
                                   help='Leave empty to export all employees')
    auto_export = fields.Boolean('Auto Export', default=False,
                                help='Automatically export when attendance records are created/updated')

    def action_export(self):
        """Create export configuration and export data"""
        export_config = self.env['hr.attendance.export'].create({
            'name': self.name,
            'export_path': self.export_path,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': [(6, 0, self.employee_ids.ids)],
            'auto_export': self.auto_export,
        })
        
        # Export data
        result = export_config.export_attendance_data()
        
        # Return to export configuration if successful
        if result.get('type') == 'ir.actions.client':
            return {
                'type': 'ir.actions.act_window',
                'name': _('Attendance Export'),
                'view_mode': 'form',
                'res_model': 'hr.attendance.export',
                'res_id': export_config.id,
                'target': 'current',
            }
        
        return result
