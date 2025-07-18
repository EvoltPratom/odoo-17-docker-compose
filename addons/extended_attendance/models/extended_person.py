from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json


class ExtendedPerson(models.Model):
    _name = 'extended.attendance.person'
    _description = 'Extended Person for Attendance'
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        string='Full Name',
        required=True,
        help='Full name of the person'
    )
    
    first_name = fields.Char(
        string='First Name',
        help='First name'
    )
    
    last_name = fields.Char(
        string='Last Name',
        help='Last name'
    )
    
    person_type_id = fields.Many2one(
        'person.type',
        string='Person Type',
        required=True,
        help='Type of person (Employee, Student, Guest, etc.)'
    )
    
    # Identification
    person_id = fields.Char(
        string='Person ID',
        required=True,
        help='Unique identifier for the person (employee ID, student ID, etc.)'
    )
    
    barcode = fields.Char(
        string='Barcode',
        help='Barcode for attendance scanning'
    )
    
    rfid_tag = fields.Char(
        string='RFID Tag',
        help='RFID tag identifier'
    )
    
    qr_code = fields.Char(
        string='QR Code',
        help='QR code for mobile attendance'
    )
    
    # Contact Information
    email = fields.Char(
        string='Email',
        help='Email address'
    )
    
    phone = fields.Char(
        string='Phone',
        help='Phone number'
    )
    
    mobile = fields.Char(
        string='Mobile',
        help='Mobile phone number'
    )
    
    # Address
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    
    # Status and Dates
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this person will be hidden'
    )
    
    start_date = fields.Date(
        string='Start Date',
        help='Date when the person started (employment, enrollment, etc.)'
    )
    
    end_date = fields.Date(
        string='End Date',
        help='Date when the person ended (resignation, graduation, etc.)'
    )
    
    # Photo
    image = fields.Image(
        string='Photo',
        help='Photo of the person'
    )
    
    image_medium = fields.Image(
        string='Medium Photo',
        related='image',
        max_width=128,
        max_height=128,
        store=True
    )
    
    image_small = fields.Image(
        string='Small Photo',
        related='image',
        max_width=64,
        max_height=64,
        store=True
    )
    
    # Access Control
    access_level = fields.Selection([
        ('basic', 'Basic Access'),
        ('standard', 'Standard Access'),
        ('full', 'Full Access'),
        ('restricted', 'Restricted Access')
    ], string='Access Level', default='basic')
    
    allowed_location_ids = fields.Many2many(
        'attendance.location',
        string='Allowed Locations',
        help='Locations this person can access (empty = all allowed)'
    )
    
    requires_approval = fields.Boolean(
        string='Requires Approval',
        help='Whether this person requires approval for attendance'
    )
    
    # HR Employee Link (for existing employees)
    employee_id = fields.Many2one(
        'hr.employee',
        string='HR Employee',
        help='Link to existing HR employee record'
    )
    
    # Custom Fields Storage
    custom_fields_json = fields.Text(
        string='Custom Fields JSON',
        help='JSON storage for custom fields'
    )
    
    # Statistics
    attendance_count = fields.Integer(
        string='Attendance Count',
        compute='_compute_attendance_stats',
        help='Total number of attendance records'
    )
    
    last_attendance = fields.Datetime(
        string='Last Attendance',
        compute='_compute_attendance_stats',
        help='Last attendance record'
    )
    
    is_checked_in = fields.Boolean(
        string='Currently Checked In',
        compute='_compute_attendance_stats',
        store=True,
        help='Whether the person is currently checked in'
    )
    
    current_location_id = fields.Many2one(
        'attendance.location',
        string='Current Location',
        compute='_compute_attendance_stats',
        help='Current location if checked in'
    )

    @api.depends()  # Simplified - no dependencies for now
    def _compute_attendance_stats(self):
        """Compute attendance statistics"""
        for record in self:
            attendances = self.env['extended.attendance.record'].search([
                ('person_id', '=', record.id)
            ], order='check_in desc', limit=1)
            
            record.attendance_count = self.env['extended.attendance.record'].search_count([
                ('person_id', '=', record.id)
            ])
            
            if attendances:
                record.last_attendance = attendances[0].check_in
                record.is_checked_in = not attendances[0].check_out
                record.current_location_id = attendances[0].location_id if record.is_checked_in else False
            else:
                record.last_attendance = False
                record.is_checked_in = False
                record.current_location_id = False

    @api.constrains('person_id')
    def _check_person_id_unique(self):
        """Ensure person IDs are unique"""
        for record in self:
            if self.search_count([('person_id', '=', record.person_id), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Person ID must be unique. ID "%s" already exists.') % record.person_id)

    @api.constrains('barcode')
    def _check_barcode_unique(self):
        """Ensure barcodes are unique if provided"""
        for record in self:
            if record.barcode and self.search_count([('barcode', '=', record.barcode), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Barcode must be unique. Barcode "%s" already exists.') % record.barcode)

    @api.constrains('rfid_tag')
    def _check_rfid_unique(self):
        """Ensure RFID tags are unique if provided"""
        for record in self:
            if record.rfid_tag and self.search_count([('rfid_tag', '=', record.rfid_tag), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('RFID tag must be unique. Tag "%s" already exists.') % record.rfid_tag)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate date ranges"""
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('Start date cannot be after end date.'))

    @api.model
    def create(self, vals):
        """Override create to handle custom fields and defaults"""
        # Set default access level from person type
        if 'person_type_id' in vals and 'access_level' not in vals:
            person_type = self.env['person.type'].browse(vals['person_type_id'])
            vals['access_level'] = person_type.default_access_level

        # Set requires_approval from person type
        if 'person_type_id' in vals and 'requires_approval' not in vals:
            person_type = self.env['person.type'].browse(vals['person_type_id'])
            vals['requires_approval'] = person_type.requires_approval
        
        return super().create(vals)

    def get_custom_field_value(self, field_name):
        """Get value of a custom field"""
        self.ensure_one()
        if not self.custom_fields_json:
            return None
        
        try:
            custom_fields = json.loads(self.custom_fields_json)
            return custom_fields.get(field_name)
        except (json.JSONDecodeError, TypeError):
            return None

    def set_custom_field_value(self, field_name, value):
        """Set value of a custom field"""
        self.ensure_one()
        
        try:
            custom_fields = json.loads(self.custom_fields_json) if self.custom_fields_json else {}
        except (json.JSONDecodeError, TypeError):
            custom_fields = {}
        
        custom_fields[field_name] = value
        self.custom_fields_json = json.dumps(custom_fields)

    def check_location_access(self, location):
        """Check if person has access to a specific location"""
        self.ensure_one()
        
        # Check if person is active
        if not self.active:
            return False, _('Person is inactive')
        
        # Check if person has ended
        if self.end_date and fields.Date.today() > self.end_date:
            return False, _('Person access has expired')
        
        # Check location access permissions
        if not location.check_access_permission(self):
            return False, _('Person type not allowed at this location')
        
        # Check if person has specific location restrictions
        if self.allowed_location_ids and location not in self.allowed_location_ids:
            return False, _('Person not authorized for this location')
        
        # Check if location is currently operating
        if not location.is_operating_now():
            return False, _('Location is not currently operating')
        
        return True, _('Access granted')

    def create_attendance_record(self, location, check_in_time=None, device=None, auto_action='manual'):
        """Create an attendance record for this person with hierarchical logic"""
        self.ensure_one()

        # Check access permissions
        can_access, message = self.check_location_access(location)
        if not can_access:
            raise UserError(message)

        # Check if already checked in at this exact location
        existing_at_location = self.env['extended.attendance.record'].search([
            ('person_id', '=', self.id),
            ('location_id', '=', location.id),
            ('check_out', '=', False)
        ])

        if existing_at_location:
            raise UserError(_('Person is already checked in at %s.') % location.name)

        # Hierarchical logic: Auto check-in to parent locations if needed
        created_records = []

        # Get all parent locations that need check-in
        parent_locations = location.get_all_parent_locations()
        parent_locations.reverse()  # Start from root

        for parent in parent_locations:
            # Check if already checked in to this parent
            existing_parent = self.env['extended.attendance.record'].search([
                ('person_id', '=', self.id),
                ('location_id', '=', parent.id),
                ('check_out', '=', False)
            ])

            if not existing_parent:
                # Auto check-in to parent location
                parent_data = {
                    'person_id': self.id,
                    'location_id': parent.id,
                    'check_in': check_in_time or fields.Datetime.now(),
                    'auto_action': 'auto_checkin',
                    'notes': f'Auto checked-in when accessing {location.name}'
                }
                if device:
                    parent_data['device_id'] = device.id

                parent_record = self.env['extended.attendance.record'].create(parent_data)
                created_records.append(parent_record.id)

        # Create attendance record for the target location
        attendance_data = {
            'person_id': self.id,
            'location_id': location.id,
            'check_in': check_in_time or fields.Datetime.now(),
            'auto_action': auto_action,
        }

        if device:
            attendance_data['device_id'] = device.id

        record = self.env['extended.attendance.record'].create(attendance_data)
        created_records.append(record.id)

        return record.id

    def create_attendance(self, location_id, action='check_in'):
        """Create attendance record - API compatible method"""
        self.ensure_one()

        if action == 'check_in':
            # Get location object for check-in
            location = self.env['attendance.location'].browse(location_id)
            if not location.exists():
                raise UserError(_('Location not found'))
            return self.create_attendance_record(location)
        elif action == 'check_out':
            # Handle hierarchical check out
            return self.hierarchical_checkout()
        else:
            raise UserError(_('Invalid action. Use "check_in" or "check_out"'))

    def transfer_location(self, new_location_id):
        """Transfer person from current location to a new location"""
        self.ensure_one()

        # Check if person is currently checked in
        current_attendance = self.env['extended.attendance.record'].search([
            ('person_id', '=', self.id),
            ('check_out', '=', False)
        ], limit=1)

        if not current_attendance:
            raise UserError(_('Person %s is not currently checked in. Please check in first.') % self.name)

        # Get new location
        new_location = self.env['attendance.location'].browse(new_location_id)
        if not new_location.exists():
            raise UserError(_('New location not found'))

        # Check if already at the same location
        if current_attendance.location_id.id == new_location_id:
            raise UserError(_('Person is already at %s.') % new_location.name)

        # Close current attendance and create new one
        current_attendance.write({'check_out': fields.Datetime.now()})
        return self.create_attendance_record(new_location)

    def hierarchical_checkout(self, location=None):
        """Perform hierarchical checkout - if location specified, checkout from that location and all children"""
        self.ensure_one()

        if location:
            # Check out from specific location and all its children
            target_location = self.env['attendance.location'].browse(location) if isinstance(location, int) else location

            # Get all child locations
            child_locations = target_location.get_all_child_locations()
            all_locations = [target_location] + child_locations

            # Check out from all these locations
            checkout_time = fields.Datetime.now()
            checked_out_records = []

            for loc in all_locations:
                active_records = self.env['extended.attendance.record'].search([
                    ('person_id', '=', self.id),
                    ('location_id', '=', loc.id),
                    ('check_out', '=', False)
                ])

                for record in active_records:
                    record.write({
                        'check_out': checkout_time,
                        'auto_action': 'auto_checkout' if record.location_id != target_location else 'manual',
                        'notes': f'Auto checked-out when leaving {target_location.name}' if record.location_id != target_location else record.notes
                    })
                    checked_out_records.append(record.id)

            if checked_out_records:
                return checked_out_records[0]  # Return the main record
            else:
                raise UserError(_('No active attendance record found for %s') % target_location.name)
        else:
            # Complete checkout - checkout from all locations
            all_active = self.env['extended.attendance.record'].search([
                ('person_id', '=', self.id),
                ('check_out', '=', False)
            ])

            if not all_active:
                raise UserError(_('No active attendance records found for check out'))

            checkout_time = fields.Datetime.now()
            for record in all_active:
                record.write({
                    'check_out': checkout_time,
                    'auto_action': 'manual'
                })

            return all_active[0].id

    def action_check_in(self):
        """Action to check in the person"""
        self.ensure_one()
        if self.is_checked_in:
            raise UserError(_('Person %s is already checked in.') % self.name)

        # Get default location or let user choose
        default_location = self.env['attendance.location'].search([('code', '=', 'MAIN_ENT')], limit=1)
        if not default_location:
            default_location = self.env['attendance.location'].search([], limit=1)

        if not default_location:
            raise UserError(_('No attendance location found. Please create at least one location.'))

        return self.create_attendance_record(default_location)

    def action_check_out(self):
        """Action to check out the person"""
        self.ensure_one()
        if not self.is_checked_in:
            raise UserError(_('Person %s is not checked in.') % self.name)

        # Find the current attendance record
        current_attendance = self.env['extended.attendance.record'].search([
            ('person_id', '=', self.id),
            ('check_out', '=', False)
        ], limit=1)

        if not current_attendance:
            raise UserError(_('No active attendance record found for %s.') % self.name)

        current_attendance.write({'check_out': fields.Datetime.now()})
        return True

    def action_view_attendance(self):
        """Action to view attendance records for this person"""
        self.ensure_one()
        return {
            'name': f'Attendance - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'extended.attendance.record',
            'view_mode': 'tree,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }

    @api.model
    def search_by_identifier(self, identifier):
        """Search person by any identifier (person_id, barcode, rfid_tag, qr_code)"""
        domain = [
            '|', '|', '|',
            ('person_id', '=', identifier),
            ('barcode', '=', identifier),
            ('rfid_tag', '=', identifier),
            ('qr_code', '=', identifier)
        ]
        return self.search(domain, limit=1)
