#!/usr/bin/env python3
"""
Script to create a demo database and test data for the attendance system
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime, timedelta

# Configuration
ODOO_URL = 'http://localhost:10017'
DB_NAME = 'attendance_demo'
ADMIN_PASSWORD = 'admin'
MASTER_PASSWORD = 'admin'  # Default master password

def wait_for_odoo():
    """Wait for Odoo to be ready"""
    print("Waiting for Odoo to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{ODOO_URL}/web/database/manager", timeout=5)
            if response.status_code == 200:
                print("✅ Odoo is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"⏳ Waiting... ({i+1}/30)")
        time.sleep(2)
    return False

def create_database():
    """Create a new database"""
    print(f"Creating database '{DB_NAME}'...")
    
    # Prepare the form data for database creation
    data = {
        'master_pwd': MASTER_PASSWORD,
        'name': DB_NAME,
        'lang': 'en_US',
        'password': ADMIN_PASSWORD,
        'phone': '',
        'country_code': 'US',
        'demo': 'true',  # Include demo data
        'company_name': 'Demo Company',
        'email': 'admin@demo.com'
    }
    
    try:
        response = requests.post(f"{ODOO_URL}/web/database/create", data=data, timeout=60)
        if response.status_code == 200:
            print("✅ Database created successfully!")
            return True
        else:
            print(f"❌ Failed to create database: {response.status_code}")
            print(response.text[:500])
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating database: {e}")
        return False

def authenticate():
    """Authenticate with Odoo"""
    print("Authenticating with Odoo...")
    
    session = requests.Session()
    
    # Get session info
    response = session.post(f"{ODOO_URL}/web/session/authenticate", json={
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': DB_NAME,
            'login': 'admin',
            'password': ADMIN_PASSWORD
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('result') and result['result'].get('uid'):
            print("✅ Authentication successful!")
            return session
    
    print("❌ Authentication failed")
    return None

def install_modules(session):
    """Install required modules"""
    print("Installing HR Attendance module...")
    
    # Search for the module
    response = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'model': 'ir.module.module',
            'method': 'search_read',
            'args': [[['name', '=', 'hr_attendance']]],
            'kwargs': {'fields': ['id', 'name', 'state']}
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        modules = result.get('result', [])
        if modules:
            module_id = modules[0]['id']
            state = modules[0]['state']
            
            if state == 'installed':
                print("✅ HR Attendance module already installed!")
                return True
            elif state == 'uninstalled':
                # Install the module
                install_response = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'model': 'ir.module.module',
                        'method': 'button_immediate_install',
                        'args': [[module_id]],
                        'kwargs': {}
                    }
                })
                
                if install_response.status_code == 200:
                    print("✅ HR Attendance module installed!")
                    return True
    
    print("❌ Failed to install HR Attendance module")
    return False

def create_employees(session):
    """Create sample employees"""
    print("Creating sample employees...")
    
    employees = [
        {'name': 'John Doe', 'barcode': 'EMP001', 'work_email': 'john@demo.com'},
        {'name': 'Jane Smith', 'barcode': 'EMP002', 'work_email': 'jane@demo.com'},
        {'name': 'Bob Johnson', 'barcode': 'EMP003', 'work_email': 'bob@demo.com'},
    ]
    
    created_employees = []
    
    for emp_data in employees:
        response = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'hr.employee',
                'method': 'create',
                'args': [emp_data],
                'kwargs': {}
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                created_employees.append(result['result'])
                print(f"✅ Created employee: {emp_data['name']}")
    
    return created_employees

def create_attendance_records(session, employee_ids):
    """Create sample attendance records"""
    print("Creating sample attendance records...")
    
    # Create records for the last 7 days
    for i, emp_id in enumerate(employee_ids):
        for day in range(7):
            date_offset = day
            check_in_time = datetime.now() - timedelta(days=date_offset, hours=24-8, minutes=i*5)
            check_out_time = check_in_time + timedelta(hours=8, minutes=30)
            
            attendance_data = {
                'employee_id': emp_id,
                'check_in': check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'check_out': check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            response = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': 'hr.attendance',
                    'method': 'create',
                    'args': [attendance_data],
                    'kwargs': {}
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    print(f"✅ Created attendance record for employee {emp_id}, day {day+1}")

def main():
    """Main setup function"""
    print("🚀 Setting up Odoo Attendance Demo")
    print("=" * 50)
    
    # Wait for Odoo to be ready
    if not wait_for_odoo():
        print("❌ Odoo is not ready. Please check if it's running.")
        return
    
    # Create database
    if not create_database():
        print("❌ Failed to create database. Check if it already exists.")
        # Try to continue anyway
    
    # Wait a bit for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(10)
    
    # Authenticate
    session = authenticate()
    if not session:
        print("❌ Setup failed at authentication step")
        return
    
    # Install modules
    if not install_modules(session):
        print("❌ Failed to install modules")
        return
    
    # Create employees
    employee_ids = create_employees(session)
    if not employee_ids:
        print("❌ Failed to create employees")
        return
    
    # Create attendance records
    create_attendance_records(session, employee_ids)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print(f"📊 Database: {DB_NAME}")
    print(f"🌐 Access Odoo at: {ODOO_URL}")
    print(f"👤 Username: admin")
    print(f"🔒 Password: {ADMIN_PASSWORD}")
    print(f"🎯 Custom Frontend: http://localhost:8080")
    print("\nYou can now use the attendance system!")

if __name__ == "__main__":
    main()
