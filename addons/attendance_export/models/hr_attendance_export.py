import json
import os
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrAttendanceExport(models.Model):
    _name = 'hr.attendance.export'
    _description = 'Attendance Export Configuration'
    _order = 'create_date desc'

    name = fields.Char('Export Name', required=True)
    export_path = fields.Char('Export Path', required=True, 
                              default='/tmp/attendance_exports', 
                              help='Directory path where JSON files will be saved')
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', 
                                   help='Leave empty to export all employees')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('exported', 'Exported'),
        ('error', 'Error')
    ], default='draft', string='Status')
    export_file = fields.Char('Export File', readonly=True)
    last_export_date = fields.Datetime('Last Export Date', readonly=True)
    auto_export = fields.Boolean('Auto Export', default=False,
                                help='Automatically export when attendance records are created/updated')

    @api.model
    def create_export_directory(self, path):
        """Create export directory if it doesn't exist"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            raise UserError(_('Cannot create export directory: %s') % str(e))

    def export_attendance_data(self):
        """Export attendance data to JSON file"""
        self.ensure_one()
        
        # Validate dates
        if self.date_from > self.date_to:
            raise UserError(_('Date From cannot be greater than Date To'))
        
        # Create export directory
        self.create_export_directory(self.export_path)
        
        # Build domain for attendance records
        domain = [
            ('check_in', '>=', self.date_from),
            ('check_in', '<=', self.date_to)
        ]
        
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        
        # Fetch attendance records
        attendance_records = self.env['hr.attendance'].search(domain)
        
        # Prepare data for export
        export_data = {
            'export_info': {
                'export_name': self.name,
                'export_date': datetime.now().isoformat(),
                'date_from': self.date_from.isoformat(),
                'date_to': self.date_to.isoformat(),
                'total_records': len(attendance_records),
                'exported_by': self.env.user.name,
            },
            'attendance_records': []
        }
        
        for record in attendance_records:
            attendance_data = {
                'id': record.id,
                'employee_id': record.employee_id.id,
                'employee_name': record.employee_id.name,
                'employee_code': record.employee_id.barcode or '',
                'check_in': record.check_in.isoformat() if record.check_in else None,
                'check_out': record.check_out.isoformat() if record.check_out else None,
                'worked_hours': record.worked_hours,
                'overtime_hours': getattr(record, 'overtime_hours', 0),
                'department': record.employee_id.department_id.name if record.employee_id.department_id else '',
                'job_position': record.employee_id.job_id.name if record.employee_id.job_id else '',
                'create_date': record.create_date.isoformat(),
                'write_date': record.write_date.isoformat(),
            }
            export_data['attendance_records'].append(attendance_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'attendance_export_{timestamp}.json'
        file_path = os.path.join(self.export_path, filename)
        
        try:
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Update record
            self.write({
                'state': 'exported',
                'export_file': filename,
                'last_export_date': datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Export Successful'),
                    'message': _('Attendance data exported to: %s') % file_path,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.write({'state': 'error'})
            raise UserError(_('Export failed: %s') % str(e))

    def action_export(self):
        """Action to export attendance data"""
        return self.export_attendance_data()

    def action_reset_to_draft(self):
        """Reset export to draft state"""
        self.write({'state': 'draft'})


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def create(self, vals_list):
        """Override create to trigger auto export"""
        records = super().create(vals_list)
        self._trigger_auto_export()
        return records

    def write(self, vals):
        """Override write to trigger auto export"""
        result = super().write(vals)
        self._trigger_auto_export()
        return result

    def _trigger_auto_export(self):
        """Trigger automatic export if enabled"""
        auto_exports = self.env['hr.attendance.export'].search([
            ('auto_export', '=', True),
            ('state', '=', 'draft')
        ])
        
        for export_config in auto_exports:
            # Check if current record falls within export date range
            current_date = fields.Date.today()
            if export_config.date_from <= current_date <= export_config.date_to:
                try:
                    export_config.export_attendance_data()
                except Exception:
                    # Log error but don't break the attendance creation/update
                    pass
