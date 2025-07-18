# Odoo 17 Attendance Export System

This setup provides a complete Odoo 17 environment with a custom attendance export module that allows you to export attendance data to JSON files.

## 🚀 Quick Start

### 1. Start the Services

```bash
# Start Odoo and PostgreSQL containers
docker compose up -d

# Check if services are running
docker compose ps
```

### 2. Access Odoo Web Interface

1. Open your browser and go to: **http://localhost:10017**
2. You'll be redirected to the database manager
3. Create a new database:
   - **Database Name**: `attendance_db` (or any name you prefer)
   - **Email**: `admin@example.com`
   - **Password**: `admin` (or your preferred password)
   - **Language**: English
   - **Demo Data**: You can check this for sample data

### 3. Install Required Modules

Once logged in to your Odoo instance:

1. Go to **Apps** menu
2. Search for "Attendance" and install **Attendance** module
3. Search for "Attendance Export" and install **Attendance Export** module (our custom module)

## 📊 Using the Attendance Export Module

### Features

- **Export attendance data to JSON files**
- **Configurable export paths and date ranges**
- **Employee filtering options**
- **Manual and automatic export modes**
- **Export history tracking**

### Manual Export via Wizard

1. Go to **Attendance** → **Attendance Export** → **Export Wizard**
2. Configure your export:
   - **Export Name**: Give your export a meaningful name
   - **Export Path**: Directory where JSON files will be saved (default: `/tmp/attendance_exports`)
   - **Date From/To**: Select date range for export
   - **Employees**: Select specific employees or leave empty for all
   - **Auto Export**: Enable for automatic exports when attendance records change

3. Click **Export** to generate the JSON file

### Export Configurations

1. Go to **Attendance** → **Attendance Export** → **Export Configurations**
2. Create reusable export configurations
3. Execute exports manually or set up automatic exports

### JSON Export Format

The exported JSON file contains:

```json
{
  "export_info": {
    "export_name": "Export Name",
    "export_date": "2024-01-15T10:30:00",
    "date_from": "2024-01-01",
    "date_to": "2024-01-15",
    "total_records": 50,
    "exported_by": "Administrator"
  },
  "attendance_records": [
    {
      "id": 1,
      "employee_id": 1,
      "employee_name": "John Doe",
      "employee_code": "EMP001",
      "check_in": "2024-01-15T08:00:00",
      "check_out": "2024-01-15T17:00:00",
      "worked_hours": 8.0,
      "overtime_hours": 0.0,
      "department": "Sales",
      "job_position": "Sales Manager",
      "create_date": "2024-01-15T08:00:00",
      "write_date": "2024-01-15T17:00:00"
    }
  ]
}
```

## 🛠️ Development & Customization

### Module Structure

```
addons/attendance_export/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── hr_attendance_export.py
├── wizard/
│   ├── __init__.py
│   └── attendance_export_wizard.py
├── views/
│   ├── attendance_export_views.xml
│   └── hr_attendance_views.xml
└── security/
    └── ir.model.access.csv
```

### Key Models

1. **hr.attendance.export**: Main export configuration model
2. **attendance.export.wizard**: Wizard for quick exports
3. **hr.attendance**: Extended to support auto-export triggers

### Customizing Export Location

You can customize where files are exported by:

1. **Via UI**: Change the "Export Path" in the export configuration
2. **Via Code**: Modify the default path in the model definition
3. **Via Environment**: Set environment variables in docker-compose.yml

### Adding Custom Fields

To add more fields to the export:

1. Edit `hr_attendance_export.py`
2. Modify the `attendance_data` dictionary in `export_attendance_data()` method
3. Add your custom fields to the export

## 🔧 Configuration

### Docker Compose Services

- **Odoo**: Runs on port 10017 (web) and 20017 (longpolling)
- **PostgreSQL**: Database backend
- **Volumes**: 
  - `./addons`: Custom modules
  - `./etc`: Configuration files
  - `./postgresql`: Database data

### Environment Variables

You can customize the setup by modifying `docker-compose.yml`:

```yaml
environment:
  - HOST=db
  - USER=odoo
  - PASSWORD=odoo17@2023
  - EXPORT_PATH=/custom/export/path  # Custom export path
```

## 📁 File Locations

### Inside Container

- **Export files**: `/tmp/attendance_exports/` (default)
- **Odoo config**: `/etc/odoo/odoo.conf`
- **Custom modules**: `/mnt/extra-addons/`

### Host System

- **Export files**: Mounted volume or container path
- **Custom modules**: `./addons/`
- **Configuration**: `./etc/`

## 🔍 Monitoring & Troubleshooting

### Check Container Logs

```bash
# View Odoo logs
docker compose logs odoo17 -f

# View database logs
docker compose logs db -f
```

### Common Issues

1. **Module not found**: Ensure the module is in the `addons` folder and restart Odoo
2. **Permission errors**: Check file permissions for export directory
3. **Database connection**: Ensure PostgreSQL is running and accessible

### Testing the Setup

Use the provided test script to verify everything is working:

```bash
python3 check_odoo.py
```

## 🎯 Next Steps

1. **Set up employee data**: Create employees in HR module
2. **Configure attendance tracking**: Set up attendance rules and policies
3. **Test exports**: Create test attendance records and export them
4. **Automate exports**: Set up scheduled exports or real-time sync
5. **Custom integrations**: Extend the module for your specific needs

## 📋 API Usage

For programmatic access, you can use Odoo's XML-RPC API:

```python
import xmlrpc.client

# Connect to Odoo
url = 'http://localhost:10017'
db = 'your_database'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Create export configuration
export_config = {
    'name': 'API Export',
    'export_path': '/tmp/api_exports',
    'date_from': '2024-01-01',
    'date_to': '2024-01-31',
}

export_id = models.execute_kw(db, uid, password, 'hr.attendance.export', 'create', [export_config])

# Execute export
models.execute_kw(db, uid, password, 'hr.attendance.export', 'action_export', [export_id])
```

## 🤝 Support

For issues or questions:

1. Check the container logs for error messages
2. Verify module installation and dependencies
3. Review the export configuration settings
4. Test with sample data first

---

**Happy attendance tracking! 🎉**
