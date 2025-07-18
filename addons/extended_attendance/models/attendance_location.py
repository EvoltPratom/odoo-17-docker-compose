from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AttendanceLocation(models.Model):
    _name = 'attendance.location'
    _description = 'Attendance Location'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(
        string='Location Name',
        required=True,
        help='Name of the attendance location (e.g., Main Entrance, Library, Hall A)'
    )
    
    code = fields.Char(
        string='Location Code',
        required=True,
        help='Unique code for the location (e.g., MAIN, LIB, HALL_A)'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this location'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order locations'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this location will be hidden'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for UI display'
    )
    
    # Location hierarchy
    parent_location_id = fields.Many2one(
        'attendance.location',
        string='Parent Location',
        help='Parent location for hierarchical organization'
    )

    child_location_ids = fields.One2many(
        'attendance.location',
        'parent_location_id',
        string='Child Locations'
    )
    
    location_path = fields.Char(
        string='Location Path',
        compute='_compute_location_path',
        store=True,
        help='Full path of the location hierarchy'
    )
    
    # Physical details
    building = fields.Char(
        string='Building',
        help='Building name or identifier'
    )
    
    floor = fields.Char(
        string='Floor',
        help='Floor number or identifier'
    )
    
    room_number = fields.Char(
        string='Room Number',
        help='Room or area number'
    )
    
    capacity = fields.Integer(
        string='Capacity',
        help='Maximum capacity of this location'
    )
    
    # Geographic coordinates
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS latitude coordinate'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS longitude coordinate'
    )
    
    # Access control
    requires_permission = fields.Boolean(
        string='Requires Permission',
        default=False,
        help='Whether access to this location requires special permission'
    )
    
    allowed_person_type_ids = fields.Many2many(
        'person.type',
        string='Allowed Person Types',
        help='Person types allowed to access this location (empty = all allowed)'
    )
    
    # Operating hours
    has_operating_hours = fields.Boolean(
        string='Has Operating Hours',
        default=False,
        help='Whether this location has specific operating hours'
    )
    
    operating_hours_ids = fields.One2many(
        'attendance.location.hours',
        'location_id',
        string='Operating Hours'
    )
    
    # Statistics
    attendance_count = fields.Integer(
        string='Attendance Count',
        compute='_compute_attendance_count',
        help='Total number of attendance records for this location'
    )
    
    current_occupancy = fields.Integer(
        string='Current Occupancy',
        compute='_compute_current_occupancy',
        store=True,
        help='Current number of people checked in at this location'
    )
    
    # Device integration
    device_ids = fields.One2many(
        'attendance.device',
        'location_id',
        string='Attendance Devices'
    )

    @api.depends('name', 'parent_location_id.location_path')
    def _compute_location_path(self):
        """Compute the full path of the location hierarchy"""
        for record in self:
            if record.parent_location_id:
                record.location_path = f"{record.parent_location_id.location_path} / {record.name}"
            else:
                record.location_path = record.name

    @api.depends()  # Simplified - no dependencies for now
    def _compute_attendance_count(self):
        """Compute total attendance records for this location"""
        for record in self:
            try:
                record.attendance_count = self.env['extended.attendance.record'].search_count([
                    ('location_id', '=', record.id)
                ])
            except KeyError:
                # Model not loaded yet during installation
                record.attendance_count = 0

    @api.depends()  # Simplified - no dependencies for now
    def _compute_current_occupancy(self):
        """Compute current occupancy (people currently checked in)"""
        for record in self:
            try:
                # Count people who are currently checked in at this location
                record.current_occupancy = self.env['extended.attendance.record'].search_count([
                    ('location_id', '=', record.id),
                    ('check_out', '=', False)
                ])
            except KeyError:
                # Model not loaded yet during installation
                record.current_occupancy = 0

    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure location codes are unique"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Location code must be unique. Code "%s" already exists.') % record.code)

    @api.constrains('parent_location_id')
    def _check_parent_recursion(self):
        """Prevent recursive parent relationships"""
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive location hierarchies.'))

    @api.constrains('capacity', 'current_occupancy')
    def _check_capacity(self):
        """Check if current occupancy exceeds capacity"""
        for record in self:
            if record.capacity > 0 and record.current_occupancy > record.capacity:
                # This is a warning, not a hard constraint
                pass

    def action_view_attendance(self):
        """Action to view attendance records for this location"""
        self.ensure_one()
        return {
            'name': f'Attendance - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'extended.attendance.record',
            'view_mode': 'tree,form',
            'domain': [('location_id', '=', self.id)],
            'context': {'default_location_id': self.id},
        }

    def action_view_current_occupancy(self):
        """Action to view current occupancy for this location"""
        self.ensure_one()
        return {
            'name': f'Current Occupancy - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'extended.attendance.record',
            'view_mode': 'tree,form',
            'domain': [('location_id', '=', self.id), ('check_out', '=', False)],
            'context': {'default_location_id': self.id},
        }

    def check_access_permission(self, person):
        """Check if a person has permission to access this location"""
        self.ensure_one()

        # If no specific person types are defined, allow all
        if not self.allowed_person_type_ids:
            return True

        # Check if person's type is in allowed types
        return person.person_type_id in self.allowed_person_type_ids

    def is_operating_now(self):
        """Check if the location is currently operating"""
        self.ensure_one()
        
        if not self.has_operating_hours:
            return True
        
        from datetime import datetime
        now = datetime.now()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        current_time = now.time()
        
        operating_hours = self.operating_hours_ids.filtered(
            lambda h: h.weekday == str(current_weekday)
        )
        
        if not operating_hours:
            return False
        
        for hours in operating_hours:
            if hours.time_from <= current_time <= hours.time_to:
                return True
        
        return False

    @api.model
    def create_default_locations(self):
        """Create default locations if they don't exist"""
        default_locations = [
            {
                'name': 'Main Entrance',
                'code': 'MAIN_ENT',
                'description': 'Primary entrance to the building',
                'sequence': 1,
                'color': 1
            },
            {
                'name': 'Reception',
                'code': 'RECEPTION',
                'description': 'Reception area',
                'sequence': 2,
                'color': 2
            },
            {
                'name': 'Office Area',
                'code': 'OFFICE',
                'description': 'General office workspace',
                'sequence': 10,
                'color': 3
            }
        ]
        
        for location_data in default_locations:
            existing = self.search([('code', '=', location_data['code'])])
            if not existing:
                self.create(location_data)


class LocationOperatingHours(models.Model):
    _name = 'location.hours'
    _description = 'Location Operating Hours'
    _order = 'weekday, time_from'

    location_id = fields.Many2one(
        'attendance.location',
        string='Location',
        required=True,
        ondelete='cascade'
    )
    
    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', required=True)
    
    time_from = fields.Float(
        string='From',
        required=True,
        help='Start time (24-hour format)'
    )
    
    time_to = fields.Float(
        string='To',
        required=True,
        help='End time (24-hour format)'
    )
    
    @api.constrains('time_from', 'time_to')
    def _check_times(self):
        """Validate time ranges"""
        for record in self:
            if record.time_from >= record.time_to:
                raise ValidationError(_('Start time must be before end time.'))


class AttendanceDevice(models.Model):
    _name = 'attendance.device'
    _description = 'Attendance Device'
    _rec_name = 'name'

    name = fields.Char(
        string='Device Name',
        required=True,
        help='Name of the attendance device'
    )

    device_id = fields.Char(
        string='Device ID',
        required=True,
        help='Unique identifier for the device'
    )

    location_id = fields.Many2one(
        'attendance.location',
        string='Location',
        required=True,
        help='Location where this device is installed'
    )
    
    device_type = fields.Selection([
        ('rfid', 'RFID Reader'),
        ('biometric', 'Biometric Scanner'),
        ('qr', 'QR Code Scanner'),
        ('manual', 'Manual Entry'),
        ('mobile', 'Mobile App'),
    ], string='Device Type', required=True)
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    last_sync = fields.Datetime(
        string='Last Sync',
        help='Last time the device synchronized data'
    )
    
    @api.constrains('device_id')
    def _check_device_id_unique(self):
        """Ensure device IDs are unique"""
        for record in self:
            if self.search_count([('device_id', '=', record.device_id), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Device ID must be unique. ID "%s" already exists.') % record.device_id)


class AttendanceLocationHours(models.Model):
    """Operating hours for attendance locations"""
    _name = 'attendance.location.hours'
    _description = 'Attendance Location Operating Hours'
    _order = 'location_id, day_of_week, time_from'

    location_id = fields.Many2one(
        'attendance.location',
        string='Location',
        required=True,
        ondelete='cascade'
    )

    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', required=True)

    time_from = fields.Float(
        string='From',
        required=True,
        help='Start time (24-hour format)'
    )

    time_to = fields.Float(
        string='To',
        required=True,
        help='End time (24-hour format)'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )
