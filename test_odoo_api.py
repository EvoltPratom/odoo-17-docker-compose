#!/usr/bin/env python3
"""
Enhanced test script to interact with Odoo API and explore attendance functionality
"""

import xmlrpc.client
import json
from datetime import datetime, timedelta
import pprint

# Odoo connection parameters
URL = 'http://localhost:10017'
DB = 'test_attendance'  # Change this to your actual database name
USERNAME = 'admin'
PASSWORD = 'admin'  # Change this to your actual password

# Pretty printer for better output
pp = pprint.PrettyPrinter(indent=2)

def create_database():
    """Create a new database"""
    try:
        db_service = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/db')
        # Create database
        db_service.create_database('admin', DB, True, 'en_US', PASSWORD)
        print(f"Database '{DB}' created successfully")
        return True
    except Exception as e:
        print(f"Database creation failed or already exists: {e}")
        return False

def connect_to_odoo():
    """Connect to Odoo and authenticate"""
    try:
        # Common endpoint for authentication
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        
        # Authenticate
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if uid:
            print(f"Successfully authenticated as user ID: {uid}")
            return uid, common
        else:
            print("Authentication failed")
            return None, None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None, None

def install_modules(uid, common):
    """Install required modules"""
    try:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Install hr_attendance module
        module_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search', 
                                      [[['name', '=', 'hr_attendance']]])
        if module_ids:
            models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', 
                            [module_ids])
            print("HR Attendance module installed")
        
        # Install our custom attendance_export module
        module_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search', 
                                      [[['name', '=', 'attendance_export']]])
        if module_ids:
            models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', 
                            [module_ids])
            print("Attendance Export module installed")
        
        return True
    except Exception as e:
        print(f"Module installation failed: {e}")
        return False

def create_test_data(uid, common):
    """Create test employees and attendance records"""
    try:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Create test employees
        employees = []
        for i in range(3):
            employee_data = {
                'name': f'Test Employee {i+1}',
                'barcode': f'EMP{i+1:03d}',
                'work_email': f'employee{i+1}@test.com',
            }
            employee_id = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'create', [employee_data])
            employees.append(employee_id)
            print(f"Created employee: {employee_data['name']}")
        
        # Create test attendance records
        base_date = datetime.now() - timedelta(days=7)
        for i, employee_id in enumerate(employees):
            for day in range(7):
                check_in = base_date + timedelta(days=day, hours=8, minutes=i*10)
                check_out = check_in + timedelta(hours=8)
                
                attendance_data = {
                    'employee_id': employee_id,
                    'check_in': check_in.strftime('%Y-%m-%d %H:%M:%S'),
                    'check_out': check_out.strftime('%Y-%m-%d %H:%M:%S'),
                }
                
                attendance_id = models.execute_kw(DB, uid, PASSWORD, 'hr.attendance', 'create', [attendance_data])
                print(f"Created attendance record for employee {employee_id}, day {day+1}")
        
        return True
    except Exception as e:
        print(f"Test data creation failed: {e}")
        return False

def test_export_functionality(uid, common):
    """Test the attendance export functionality"""
    try:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Create an export configuration
        export_config = {
            'name': 'Test Export',
            'export_path': '/tmp/attendance_exports',
            'date_from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'date_to': datetime.now().strftime('%Y-%m-%d'),
            'auto_export': False,
        }
        
        export_id = models.execute_kw(DB, uid, PASSWORD, 'hr.attendance.export', 'create', [export_config])
        print(f"Created export configuration with ID: {export_id}")
        
        # Execute the export
        result = models.execute_kw(DB, uid, PASSWORD, 'hr.attendance.export', 'action_export', [export_id])
        print(f"Export executed successfully: {result}")
        
        return True
    except Exception as e:
        print(f"Export test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Starting Odoo Attendance Export Test")
    print("=" * 50)
    
    # Create database
    print("\n1. Creating database...")
    create_database()
    
    # Connect to Odoo
    print("\n2. Connecting to Odoo...")
    uid, common = connect_to_odoo()
    if not uid:
        print("Failed to connect to Odoo")
        return
    
    # Install modules
    print("\n3. Installing modules...")
    if install_modules(uid, common):
        print("Modules installed successfully")
    
    # Create test data
    print("\n4. Creating test data...")
    if create_test_data(uid, common):
        print("Test data created successfully")
    
    # Test export functionality
    print("\n5. Testing export functionality...")
    if test_export_functionality(uid, common):
        print("Export test completed successfully")
    
    print("\n" + "=" * 50)
    print("Test completed! You can now access Odoo at http://localhost:10017")
    print(f"Database: {DB}")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")

if __name__ == "__main__":
    main()
