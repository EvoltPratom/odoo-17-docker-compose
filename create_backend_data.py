#!/usr/bin/env python3
"""
Simple script to create backend data for the frontend
Uses existing Odoo models and creates minimal custom data
"""

import xmlrpc.client
import time

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_EMAIL = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'

def connect_to_odoo():
    """Connect to Odoo and authenticate"""
    print("🔗 Connecting to Odoo...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ADMIN_EMAIL, ADMIN_PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed")
            return None, None
        
        print(f"✅ Connected, UID: {uid}")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def create_employees_with_types(uid, models):
    """Create employees with different types"""
    print("👥 Creating employees with types...")
    
    employees_data = [
        {
            'name': 'John Admin',
            'work_email': 'john.admin@company.com',
            'employee_type': 'employee',
            'category_ids': [(6, 0, [])],  # Empty categories for now
        },
        {
            'name': 'Jane Manager',
            'work_email': 'jane.manager@company.com', 
            'employee_type': 'employee',
        },
        {
            'name': 'Bob Student',
            'work_email': 'bob.student@company.com',
            'employee_type': 'employee',
        },
        {
            'name': 'Alice Guest',
            'work_email': 'alice.guest@company.com',
            'employee_type': 'employee',
        }
    ]
    
    created_employees = []
    
    for emp_data in employees_data:
        try:
            # Check if employee already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'hr.employee', 'search',
                [[['work_email', '=', emp_data['work_email']]]]
            )
            
            if not existing:
                emp_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'hr.employee', 'create',
                    [emp_data]
                )
                print(f"✅ Created employee: {emp_data['name']} (ID: {emp_id})")
                created_employees.append(emp_id)
            else:
                print(f"✅ Employee already exists: {emp_data['name']}")
                created_employees.append(existing[0])
                
        except Exception as e:
            print(f"❌ Failed to create employee {emp_data['name']}: {e}")
    
    return created_employees

def create_departments_as_locations(uid, models):
    """Create departments that can serve as locations"""
    print("🏢 Creating departments as locations...")
    
    departments_data = [
        {
            'name': 'Main Entrance',
            'complete_name': 'Main Entrance',
        },
        {
            'name': 'Reception',
            'complete_name': 'Reception Area',
        },
        {
            'name': 'Office Floor 1',
            'complete_name': 'Office Floor 1',
        },
        {
            'name': 'Conference Room A',
            'complete_name': 'Conference Room A',
        },
        {
            'name': 'Cafeteria',
            'complete_name': 'Cafeteria',
        }
    ]
    
    created_departments = []
    
    for dept_data in departments_data:
        try:
            # Check if department already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'hr.department', 'search',
                [[['name', '=', dept_data['name']]]]
            )
            
            if not existing:
                dept_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'hr.department', 'create',
                    [dept_data]
                )
                print(f"✅ Created department/location: {dept_data['name']} (ID: {dept_id})")
                created_departments.append(dept_id)
            else:
                print(f"✅ Department/location already exists: {dept_data['name']}")
                created_departments.append(existing[0])
                
        except Exception as e:
            print(f"❌ Failed to create department {dept_data['name']}: {e}")
    
    return created_departments

def create_sample_attendance_records(uid, models, employee_ids):
    """Create some sample attendance records"""
    print("📝 Creating sample attendance records...")
    
    if not employee_ids:
        print("❌ No employees available for attendance records")
        return
    
    import datetime
    
    # Create some check-ins for today
    today = datetime.datetime.now()
    
    for i, emp_id in enumerate(employee_ids[:2]):  # Just first 2 employees
        try:
            # Create a check-in record
            attendance_data = {
                'employee_id': emp_id,
                'check_in': today.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Check if attendance already exists for today
            existing = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'hr.attendance', 'search',
                [[
                    ['employee_id', '=', emp_id],
                    ['check_in', '>=', today.strftime('%Y-%m-%d 00:00:00')],
                    ['check_out', '=', False]
                ]]
            )
            
            if not existing:
                att_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'hr.attendance', 'create',
                    [attendance_data]
                )
                print(f"✅ Created attendance record for employee {emp_id} (ID: {att_id})")
            else:
                print(f"✅ Attendance record already exists for employee {emp_id}")
                
        except Exception as e:
            print(f"❌ Failed to create attendance for employee {emp_id}: {e}")

def main():
    print("🚀 Creating Backend Data for Frontend...")
    print("=" * 60)
    
    # Connect to Odoo
    uid, models = connect_to_odoo()
    if not uid:
        return
    
    # Create employees with different types
    employee_ids = create_employees_with_types(uid, models)
    
    # Create departments as locations
    department_ids = create_departments_as_locations(uid, models)
    
    # Create sample attendance records
    create_sample_attendance_records(uid, models, employee_ids)
    
    print("\n" + "=" * 60)
    print("🎉 Backend data creation completed!")
    print("📍 Odoo URL: http://localhost:10017")
    print("🗄️  Database: extended_attendance")
    print("👤 Username: admin@demo.com")
    print("🔑 Password: admin")
    print("\n✅ Your backend now has:")
    print("   - Sample employees (different types)")
    print("   - Departments as locations")
    print("   - Sample attendance records")
    print("\n🔄 Your frontend can now use:")
    print("   - hr.employee model for people")
    print("   - hr.department model for locations")
    print("   - hr.attendance model for check-ins/outs")
    print("=" * 60)

if __name__ == "__main__":
    main()
