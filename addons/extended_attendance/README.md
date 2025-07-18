# Extended Attendance System

A comprehensive attendance management system for Odoo 17 that extends the standard HR attendance module to support multiple locations and different person types.

## Features

### 🏢 Multi-Location Support
- **Multiple Locations**: Track attendance across different locations within a single premise
- **Location Hierarchy**: Organize locations in a hierarchical structure (buildings, floors, rooms)
- **Operating Hours**: Set specific operating hours for each location
- **Capacity Management**: Monitor current occupancy vs. maximum capacity
- **Access Control**: Restrict access to specific locations based on person types

### 👥 Flexible Person Types
- **Dynamic Person Types**: Create custom person types (employees, students, guests, admins, etc.)
- **Access Levels**: Configure different access levels (basic, standard, full, restricted)
- **Custom Fields**: Add custom fields specific to each person type
- **System Protection**: Prevent deletion of critical person types (admin, owner)
- **Approval Workflows**: Require approval for certain person types

### 📱 Device Integration
- **Multiple Device Types**: Support for RFID readers, biometric scanners, QR code scanners, mobile apps
- **Device Management**: Track and manage attendance devices per location
- **Real-time Sync**: Monitor device synchronization status

### 🔐 Advanced Security
- **Role-based Access**: Three-tier security model (User, Officer, Manager)
- **Permission Controls**: Granular permissions for different operations
- **Location Restrictions**: Limit person access to specific locations
- **Approval Workflows**: Built-in approval system for sensitive operations

### 📊 Comprehensive Reporting
- **Real-time Dashboard**: Current attendance status across all locations
- **Historical Reports**: Detailed attendance history with filtering options
- **Analytics**: Pivot tables and graphs for attendance analysis
- **Export Capabilities**: Export data in various formats

### 🔌 REST API
- **Complete API Coverage**: Full REST API for all operations
- **External Integration**: Easy integration with external systems
- **Mobile App Support**: API designed for mobile application development
- **Webhook Support**: Real-time notifications for attendance events

## Installation

1. **Copy the Module**:
   ```bash
   cp -r addons/extended_attendance /path/to/your/odoo/addons/
   ```

2. **Update Apps List**:
   - Go to Apps menu in Odoo
   - Click "Update Apps List"

3. **Install the Module**:
   - Search for "Extended Attendance System"
   - Click Install

4. **Configure Security Groups**:
   - Assign users to appropriate groups:
     - **Attendance User**: Basic attendance operations
     - **Attendance Officer**: Manage attendance for others
     - **Attendance Manager**: Full system configuration

## Quick Start

### 1. Set Up Person Types
```python
# Default person types are created automatically:
# - Administrator (ADMIN) - System protected
# - Owner (OWNER) - System protected  
# - Employee (EMP)
# - Student (STU)
# - Guest (GST)

# Create custom person types via UI or API
```

### 2. Configure Locations
```python
# Default locations are created:
# - Main Entrance (MAIN_ENT)
# - Reception (RECEPTION)
# - Office Area (OFFICE)
# - Library (LIBRARY)
# - Hall A (HALL_A)

# Add your own locations via UI or API
```

### 3. Add Persons
```python
# Create persons through the UI or API
# Each person needs:
# - Name and Person ID
# - Person Type
# - Identification method (barcode, RFID, QR code)
```

### 4. Start Tracking Attendance
```python
# Use the API or UI to record attendance
# People can check in/out at different locations
```

## API Usage

### Authentication
```python
import requests

# Authenticate with Odoo
auth_data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "your_database",
        "login": "username",
        "password": "password"
    }
}
response = requests.post("http://localhost:8069/web/session/authenticate", json=auth_data)
```

### Person Types API
```python
# Get all person types
GET /api/attendance/person-types

# Create person type
POST /api/attendance/person-types
{
    "name": "Contractor",
    "code": "CONT",
    "description": "External contractors",
    "default_access_level": "restricted"
}
```

### Locations API
```python
# Get all locations
GET /api/attendance/locations

# Create location
POST /api/attendance/locations
{
    "name": "Conference Room A",
    "code": "CONF_A",
    "building": "Main Building",
    "floor": "2nd Floor",
    "capacity": 50
}
```

### Persons API
```python
# Get all persons
GET /api/attendance/persons

# Create person
POST /api/attendance/persons
{
    "name": "John Doe",
    "person_id": "EMP123",
    "person_type_id": 1,
    "email": "john.doe@company.com",
    "barcode": "EMP123_BC"
}

# Search person by identifier
POST /api/attendance/persons/search
{
    "identifier": "EMP123"  # Can be person_id, barcode, RFID, or QR code
}
```

### Attendance API
```python
# Check in
POST /api/attendance/check-in
{
    "person_identifier": "EMP123",
    "location_code": "MAIN_ENT",
    "device_id": "SCANNER_001"
}

# Check out
POST /api/attendance/check-out
{
    "person_identifier": "EMP123"
}

# Get current attendance
GET /api/attendance/current

# Get attendance records
GET /api/attendance/records?date_from=2024-01-01&date_to=2024-01-31

# Generate report
POST /api/attendance/report
{
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "location_code": "OFFICE"
}
```

## Testing

Run the included test script to verify API functionality:

```bash
python3 test_extended_attendance_api.py
```

The test script will:
- Authenticate with Odoo
- Test all API endpoints
- Create sample data
- Verify functionality
- Generate reports

## Configuration

### Person Type Configuration
- **Access Levels**: Define what each person type can access
- **Custom Fields**: Add type-specific fields (student ID, company, etc.)
- **Duration Limits**: Set maximum attendance duration
- **Approval Requirements**: Require approval for certain types

### Location Configuration
- **Operating Hours**: Set when locations are available
- **Capacity Limits**: Define maximum occupancy
- **Access Restrictions**: Limit access by person type
- **Device Assignment**: Assign attendance devices to locations

### Security Configuration
- **User Groups**: Assign appropriate security groups
- **Access Rules**: Configure record-level security
- **API Permissions**: Control API access by user role

## Use Cases

### 🏫 Schools
- **Students**: Track student attendance in classrooms, library, labs
- **Teachers**: Monitor teacher presence and location
- **Visitors**: Manage guest access with approval workflows
- **Multiple Buildings**: Handle campus-wide attendance tracking

### 🏢 Offices
- **Employees**: Standard employee attendance tracking
- **Contractors**: Temporary access with restrictions
- **Visitors**: Guest management with escort requirements
- **Multiple Floors**: Department-specific attendance

### 🏥 Healthcare
- **Staff**: Track medical staff across departments
- **Patients**: Monitor patient location for safety
- **Visitors**: Controlled visitor access with time limits
- **Emergency**: Real-time occupancy for emergency procedures

### 🏭 Manufacturing
- **Workers**: Track presence in different production areas
- **Safety**: Ensure proper personnel in restricted areas
- **Shifts**: Manage multiple shift patterns
- **Compliance**: Maintain attendance records for audits

## Support

For issues, questions, or contributions:
1. Check the documentation
2. Run the test script to verify setup
3. Review the API endpoints
4. Check Odoo logs for errors

## License

This module is licensed under LGPL-3.
