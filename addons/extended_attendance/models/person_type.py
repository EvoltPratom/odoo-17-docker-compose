from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PersonType(models.Model):
    _name = 'person.type'
    _description = 'Person Type for Extended Attendance'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(
        string='Type Name',
        required=True,
        help='Name of the person type (e.g., Employee, Student, Guest)'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for the person type (e.g., EMP, STU, GST)'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this person type'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order person types'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this person type will be hidden'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for UI display'
    )
    
    is_system = fields.Boolean(
        string='System Type',
        default=False,
        help='System types cannot be deleted (admin, owner)'
    )
    
    can_delete = fields.Boolean(
        string='Can Delete',
        compute='_compute_can_delete',
        help='Whether this type can be deleted'
    )
    
    person_count = fields.Integer(
        string='Person Count',
        compute='_compute_person_count',
        help='Number of persons with this type'
    )
    
    # Configuration fields
    requires_approval = fields.Boolean(
        string='Requires Approval',
        default=False,
        help='Whether persons of this type require approval before access'
    )
    
    default_access_level = fields.Selection([
        ('basic', 'Basic Access'),
        ('standard', 'Standard Access'),
        ('full', 'Full Access'),
        ('restricted', 'Restricted Access')
    ], string='Default Access Level', default='basic')
    
    max_duration_hours = fields.Float(
        string='Max Duration (Hours)',
        help='Maximum allowed duration for attendance (0 = no limit)'
    )
    
    # Custom fields configuration
    custom_field_ids = fields.One2many(
        'extended.attendance.custom.field',
        'person_type_id',
        string='Custom Fields'
    )

    @api.depends('is_system', 'person_count')
    def _compute_can_delete(self):
        """Compute whether this person type can be deleted"""
        for record in self:
            # System types (admin, owner) cannot be deleted
            # Types with existing persons cannot be deleted
            record.can_delete = not record.is_system and record.person_count == 0

    @api.depends()
    def _compute_person_count(self):
        """Compute the number of persons with this type"""
        for record in self:
            # This will be implemented when we create the person model
            record.person_count = self.env['extended.attendance.person'].search_count([
                ('person_type_id', '=', record.id)
            ])

    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure person type codes are unique"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Person type code must be unique. Code "%s" already exists.') % record.code)

    @api.constrains('name')
    def _check_name_unique(self):
        """Ensure person type names are unique"""
        for record in self:
            if self.search_count([('name', '=', record.name), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Person type name must be unique. Name "%s" already exists.') % record.name)

    def unlink(self):
        """Override unlink to prevent deletion of system types and types with persons"""
        for record in self:
            if record.is_system:
                raise UserError(_('Cannot delete system person type "%s". System types are protected.') % record.name)
            
            if record.person_count > 0:
                raise UserError(_('Cannot delete person type "%s" because it has %d associated persons. '
                                'Please reassign or delete the persons first.') % (record.name, record.person_count))
        
        return super().unlink()

    def action_view_persons(self):
        """Action to view persons of this type"""
        self.ensure_one()
        return {
            'name': f'Persons - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'extended.attendance.person',
            'view_mode': 'tree,form',
            'domain': [('person_type_id', '=', self.id)],
            'context': {'default_person_type_id': self.id},
        }

    @api.model
    def create_default_types(self):
        """Create default person types if they don't exist"""
        default_types = [
            {
                'name': 'Administrator',
                'code': 'ADMIN',
                'description': 'System administrators with full access',
                'sequence': 1,
                'is_system': True,
                'default_access_level': 'full',
                'color': 1
            },
            {
                'name': 'Owner',
                'code': 'OWNER',
                'description': 'Organization owners with full access',
                'sequence': 2,
                'is_system': True,
                'default_access_level': 'full',
                'color': 2
            },
            {
                'name': 'Employee',
                'code': 'EMP',
                'description': 'Regular employees',
                'sequence': 10,
                'default_access_level': 'standard',
                'color': 3
            },
            {
                'name': 'Student',
                'code': 'STU',
                'description': 'Students',
                'sequence': 20,
                'default_access_level': 'basic',
                'color': 4
            },
            {
                'name': 'Guest',
                'code': 'GST',
                'description': 'Temporary guests',
                'sequence': 30,
                'requires_approval': True,
                'default_access_level': 'restricted',
                'max_duration_hours': 8.0,
                'color': 5
            }
        ]
        
        for type_data in default_types:
            existing = self.search([('code', '=', type_data['code'])])
            if not existing:
                self.create(type_data)


class CustomField(models.Model):
    _name = 'extended.attendance.custom.field'
    _description = 'Custom Fields for Person Types'
    _order = 'sequence, name'

    name = fields.Char(
        string='Field Name',
        required=True,
        help='Name of the custom field'
    )
    
    technical_name = fields.Char(
        string='Technical Name',
        required=True,
        help='Technical name for the field (used in code)'
    )
    
    field_type = fields.Selection([
        ('char', 'Text'),
        ('text', 'Long Text'),
        ('integer', 'Number'),
        ('float', 'Decimal'),
        ('boolean', 'Checkbox'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('selection', 'Selection'),
    ], string='Field Type', required=True, default='char')
    
    required = fields.Boolean(
        string='Required',
        default=False
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    
    person_type_id = fields.Many2one(
        'extended.attendance.person.type',
        string='Person Type',
        required=True,
        ondelete='cascade'
    )
    
    selection_options = fields.Text(
        string='Selection Options',
        help='For selection fields, enter options separated by newlines'
    )
    
    help_text = fields.Text(
        string='Help Text',
        help='Help text to display for this field'
    )

    @api.constrains('technical_name')
    def _check_technical_name(self):
        """Validate technical name format"""
        import re
        for record in self:
            if not re.match(r'^[a-z][a-z0-9_]*$', record.technical_name):
                raise ValidationError(_('Technical name must start with a letter and contain only lowercase letters, numbers, and underscores.'))
