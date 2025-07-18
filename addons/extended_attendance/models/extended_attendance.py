from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class ExtendedAttendanceRecord(models.Model):
    _name = 'extended.attendance.record'
    _description = 'Extended Attendance Record'
    _order = 'check_in desc'
    _rec_name = 'display_name'

    # Core fields
    person_id = fields.Many2one(
        'extended.attendance.person',
        string='Person',
        required=True,
        help='Person who attended'
    )
    
    location_id = fields.Many2one(
        'attendance.location',
        string='Location',
        required=True,
        help='Location where attendance was recorded'
    )
    
    check_in = fields.Datetime(
        string='Check In',
        required=True,
        default=fields.Datetime.now,
        help='Check-in time'
    )
    
    check_out = fields.Datetime(
        string='Check Out',
        help='Check-out time'
    )
    
    # Device information
    device_id = fields.Many2one(
        'attendance.device',
        string='Device',
        help='Device used for attendance recording'
    )

    # Action tracking
    auto_action = fields.Selection([
        ('manual', 'Manual'),
        ('auto_checkin', 'Auto Check-in'),
        ('auto_checkout', 'Auto Check-out'),
    ], string='Action Type', default='manual', required=True,
       help='Whether this action was manual or automatic')

    notes = fields.Text(
        string='Notes',
        help='Additional notes about this attendance record'
    )

    # Computed fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    worked_hours = fields.Float(
        string='Worked Hours',
        compute='_compute_worked_hours',
        store=True,
        help='Number of hours between check-in and check-out'
    )
    
    duration_display = fields.Char(
        string='Duration',
        compute='_compute_duration_display',
        help='Human-readable duration'
    )
    
    # Status fields
    state = fields.Selection([
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('overtime', 'Overtime'),
        ('incomplete', 'Incomplete')
    ], string='Status', compute='_compute_state', store=True)
    
    is_overtime = fields.Boolean(
        string='Is Overtime',
        compute='_compute_overtime',
        store=True,
        help='Whether this attendance exceeds normal working hours'
    )
    
    # Additional information
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this attendance record'
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        help='User who approved this attendance record'
    )
    
    approval_date = fields.Datetime(
        string='Approval Date',
        help='Date when this record was approved'
    )
    
    # Related fields for easy access
    person_type_id = fields.Many2one(
        'person.type',
        string='Person Type',
        related='person_id.person_type_id',
        store=True
    )
    
    person_name = fields.Char(
        string='Person Name',
        related='person_id.name',
        store=True
    )
    
    location_name = fields.Char(
        string='Location Name',
        related='location_id.name',
        store=True
    )

    @api.depends('person_id.name', 'location_id.name', 'check_in')
    def _compute_display_name(self):
        """Compute display name for the record"""
        for record in self:
            if record.person_id and record.location_id:
                check_in_str = record.check_in.strftime('%Y-%m-%d %H:%M') if record.check_in else 'N/A'
                record.display_name = f"{record.person_id.name} @ {record.location_id.name} ({check_in_str})"
            else:
                record.display_name = "Attendance Record"

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        """Compute worked hours"""
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                record.worked_hours = delta.total_seconds() / 3600.0
            else:
                record.worked_hours = 0.0

    @api.depends('worked_hours', 'check_in', 'check_out')
    def _compute_duration_display(self):
        """Compute human-readable duration"""
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                record.duration_display = f"{hours}h {minutes}m"
            elif record.check_in:
                # Currently checked in - show elapsed time
                delta = datetime.now() - record.check_in.replace(tzinfo=None)
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                record.duration_display = f"{hours}h {minutes}m (ongoing)"
            else:
                record.duration_display = "N/A"

    @api.depends('check_in', 'check_out', 'worked_hours')
    def _compute_state(self):
        """Compute attendance state"""
        for record in self:
            if not record.check_out:
                record.state = 'checked_in'
            elif record.worked_hours > 0:
                # Check if it's overtime (more than 8 hours)
                if record.worked_hours > 8:
                    record.state = 'overtime'
                else:
                    record.state = 'checked_out'
            else:
                record.state = 'incomplete'

    @api.depends('worked_hours', 'person_id.person_type_id.max_duration_hours')
    def _compute_overtime(self):
        """Compute if this is overtime"""
        for record in self:
            max_hours = record.person_id.person_type_id.max_duration_hours
            if max_hours > 0 and record.worked_hours > max_hours:
                record.is_overtime = True
            else:
                record.is_overtime = False

    @api.constrains('check_in', 'check_out')
    def _check_dates(self):
        """Validate check-in and check-out times"""
        for record in self:
            if record.check_out and record.check_in and record.check_out <= record.check_in:
                raise ValidationError(_('Check-out time must be after check-in time.'))

    @api.constrains('person_id', 'check_in', 'location_id')
    def _check_overlapping_attendance(self):
        """Prevent duplicate attendance records at the same location"""
        for record in self:
            if not record.check_out:  # Only check for open records
                # Only prevent overlapping at the SAME location (not different locations)
                overlapping = self.search([
                    ('person_id', '=', record.person_id.id),
                    ('location_id', '=', record.location_id.id),  # Same location only
                    ('id', '!=', record.id),
                    ('check_out', '=', False)
                ])
                if overlapping:
                    raise ValidationError(_('Person %s is already checked in at %s.') %
                                        (record.person_id.name, record.location_id.name))

    def action_check_out(self, check_out_time=None):
        """Check out the person"""
        self.ensure_one()
        
        if self.check_out:
            raise UserError(_('This attendance record is already checked out.'))
        
        check_out_time = check_out_time or fields.Datetime.now()
        
        # Validate check-out time
        if check_out_time <= self.check_in:
            raise UserError(_('Check-out time must be after check-in time.'))
        
        self.write({'check_out': check_out_time})
        
        return True

    def action_approve(self):
        """Approve the attendance record"""
        self.ensure_one()
        
        if not self.env.user.has_group('extended_attendance.group_attendance_manager'):
            raise UserError(_('Only attendance managers can approve records.'))
        
        self.write({
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        return True

    @api.model
    def create_check_in(self, person_identifier, location_code, device_id=None, check_in_time=None):
        """Create a check-in record using identifiers"""
        # Find person
        person = self.env['extended.attendance.person'].search_by_identifier(person_identifier)
        if not person:
            raise UserError(_('Person not found with identifier: %s') % person_identifier)
        
        # Find location
        location = self.env['attendance.location'].search([('code', '=', location_code)], limit=1)
        if not location:
            raise UserError(_('Location not found with code: %s') % location_code)
        
        # Find device if provided
        device = None
        if device_id:
            device = self.env['attendance.device'].search([('device_id', '=', device_id)], limit=1)
        
        # Create attendance record
        return person.create_attendance_record(location, check_in_time, device)

    @api.model
    def create_check_out(self, person_identifier, check_out_time=None):
        """Create a check-out for the person's latest check-in"""
        # Find person
        person = self.env['extended.attendance.person'].search_by_identifier(person_identifier)
        if not person:
            raise UserError(_('Person not found with identifier: %s') % person_identifier)
        
        # Find latest open attendance record
        attendance = self.search([
            ('person_id', '=', person.id),
            ('check_out', '=', False)
        ], order='check_in desc', limit=1)
        
        if not attendance:
            raise UserError(_('No open attendance record found for %s') % person.name)
        
        attendance.action_check_out(check_out_time)
        return attendance

    @api.model
    def get_current_attendance(self, location_code=None):
        """Get current attendance (people currently checked in)"""
        domain = [('check_out', '=', False)]
        
        if location_code:
            location = self.env['attendance.location'].search([('code', '=', location_code)], limit=1)
            if location:
                domain.append(('location_id', '=', location.id))
        
        return self.search(domain)

    @api.model
    def get_attendance_report(self, date_from, date_to, location_code=None, person_type_code=None):
        """Generate attendance report for a date range"""
        domain = [
            ('check_in', '>=', date_from),
            ('check_in', '<=', date_to)
        ]
        
        if location_code:
            location = self.env['attendance.location'].search([('code', '=', location_code)], limit=1)
            if location:
                domain.append(('location_id', '=', location.id))

        if person_type_code:
            person_type = self.env['person.type'].search([('code', '=', person_type_code)], limit=1)
            if person_type:
                domain.append(('person_type_id', '=', person_type.id))
        
        records = self.search(domain, order='check_in desc')
        
        # Calculate statistics
        total_records = len(records)
        total_hours = sum(records.mapped('worked_hours'))
        avg_hours = total_hours / total_records if total_records > 0 else 0
        
        return {
            'records': records,
            'statistics': {
                'total_records': total_records,
                'total_hours': total_hours,
                'average_hours': avg_hours,
                'date_from': date_from,
                'date_to': date_to
            }
        }


# Extend the original hr.attendance model to maintain compatibility
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    # Link to extended attendance record
    extended_record_id = fields.Many2one(
        'extended.attendance.record',
        string='Extended Record',
        help='Link to extended attendance record'
    )
    
    # Location information
    location_id = fields.Many2one(
        'attendance.location',
        string='Location',
        help='Location where attendance was recorded'
    )

    @api.model
    def create(self, vals):
        """Override create to potentially create extended record"""
        record = super().create(vals)
        
        # If employee has an extended person record, create extended attendance
        if record.employee_id:
            extended_person = self.env['extended.attendance.person'].search([
                ('employee_id', '=', record.employee_id.id)
            ], limit=1)
            
            if extended_person:
                # Create extended attendance record
                extended_vals = {
                    'person_id': extended_person.id,
                    'location_id': vals.get('location_id') or self._get_default_location().id,
                    'check_in': record.check_in,
                    'check_out': record.check_out,
                }
                
                extended_record = self.env['extended.attendance.record'].create(extended_vals)
                record.extended_record_id = extended_record.id
        
        return record

    def _get_default_location(self):
        """Get default location for HR attendance records"""
        default_location = self.env['attendance.location'].search([
            ('code', '=', 'MAIN_ENT')
        ], limit=1)

        if not default_location:
            # Create a default location if it doesn't exist
            default_location = self.env['attendance.location'].create({
                'name': 'Main Entrance',
                'code': 'MAIN_ENT',
                'description': 'Default location for HR attendance'
            })
        
        return default_location
