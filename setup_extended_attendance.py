#!/usr/bin/env python3
"""
Setup script for Extended Attendance System
Creates database and installs extended attendance modules with real data
"""

import xmlrpc.client
import time
import sys

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_EMAIL = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'
MASTER_PASSWORD = 'minhng.info'

def create_database():
    """Create a new database with demo data"""
    print("Creating database...")
    
    try:
        # Connect to database management
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Create database
        db_service.create_database(
            MASTER_PASSWORD,
            ODOO_DB,
            True,  # demo data
            'en_US',  # language
            ADMIN_PASSWORD,
            ADMIN_EMAIL,
            'US'  # country
        )
        
        print(f"✅ Database '{ODOO_DB}' created successfully")
        return True
        
    except Exception as e:
        if "already exists" in str(e):
            print(f"✅ Database '{ODOO_DB}' already exists")
            return True
        else:
            print(f"❌ Failed to create database: {e}")
            return False

def connect_to_odoo():
    """Connect to Odoo and authenticate"""
    print("Connecting to Odoo...")
    
    try:
        # Connect to common service
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        # Authenticate
        uid = common.authenticate(ODOO_DB, ADMIN_EMAIL, ADMIN_PASSWORD, {})
        
        if uid:
            print(f"✅ Connected to Odoo, UID: {uid}")
            
            # Connect to object service
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            return uid, models
        else:
            print("❌ Authentication failed")
            return None, None
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def install_modules(uid, models):
    """Install required modules"""
    print("Installing modules...")
    
    try:
        # Update module list
        models.execute_kw(ODOO_DB, uid, ADMIN_PASSWORD, 'ir.module.module', 'update_list', [])
        
        # Install base attendance module
        attendance_module = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'hr_attendance']]]
        )
        
        if attendance_module:
            models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [attendance_module]
            )
            print("✅ HR Attendance module installed")
        
        # Install extended attendance module
        extended_module = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'extended_attendance']]]
        )
        
        if extended_module:
            models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [extended_module]
            )
            print("✅ Extended Attendance module installed")
        else:
            print("⚠️  Extended Attendance module not found")
        
        # Install attendance export module
        export_module = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'attendance_export']]]
        )
        
        if export_module:
            models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [export_module]
            )
            print("✅ Attendance Export module installed")
        else:
            print("⚠️  Attendance Export module not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Module installation failed: {e}")
        return False

def create_sample_data(uid, models):
    """Create sample locations and person types"""
    print("Creating sample data...")
    
    try:
        # Create attendance locations
        locations_data = [
            {
                'name': 'Main Entrance',
                'code': 'MAIN_ENT',
                'building': 'Main Building',
                'floor': 'Ground Floor',
                'capacity': 0,
                'description': 'Main entrance checkpoint'
            },
            {
                'name': 'Reception',
                'code': 'RECEPTION',
                'building': 'Main Building',
                'floor': 'Ground Floor',
                'capacity': 10,
                'description': 'Reception area'
            },
            {
                'name': 'Office Floor 1',
                'code': 'OFFICE_1',
                'building': 'Main Building',
                'floor': '1st Floor',
                'capacity': 50,
                'description': 'First floor office area'
            },
            {
                'name': 'Conference Room A',
                'code': 'CONF_A',
                'building': 'Main Building',
                'floor': '2nd Floor',
                'capacity': 20,
                'description': 'Large conference room'
            },
            {
                'name': 'Cafeteria',
                'code': 'CAFETERIA',
                'building': 'Main Building',
                'floor': 'Ground Floor',
                'capacity': 100,
                'description': 'Employee cafeteria'
            }
        ]
        
        # Check if attendance.location model exists
        try:
            for location in locations_data:
                location_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'attendance.location', 'create',
                    [location]
                )
                print(f"✅ Created location: {location['name']}")
        except Exception as e:
            print(f"⚠️  Could not create locations (model may not exist): {e}")
        
        # Create person types
        person_types_data = [
            {
                'name': 'Administrator',
                'code': 'ADMIN',
                'default_access_level': 'full',
                'is_system': True,
                'description': 'System administrators with full access'
            },
            {
                'name': 'Employee',
                'code': 'EMP',
                'default_access_level': 'standard',
                'is_system': False,
                'description': 'Regular employees'
            },
            {
                'name': 'Student',
                'code': 'STU',
                'default_access_level': 'basic',
                'is_system': False,
                'description': 'Students and interns'
            },
            {
                'name': 'Guest',
                'code': 'GST',
                'default_access_level': 'restricted',
                'is_system': False,
                'description': 'Visitors and guests'
            }
        ]
        
        # Check if person.type model exists
        try:
            for person_type in person_types_data:
                type_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'person.type', 'create',
                    [person_type]
                )
                print(f"✅ Created person type: {person_type['name']}")
        except Exception as e:
            print(f"⚠️  Could not create person types (model may not exist): {e}")
        
        print("✅ Sample data creation completed")
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Extended Attendance System...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Wait for database to be ready
    print("Waiting for database to be ready...")
    time.sleep(5)
    
    # Step 2: Connect to Odoo
    uid, models = connect_to_odoo()
    if not uid:
        sys.exit(1)
    
    # Step 3: Install modules
    if not install_modules(uid, models):
        print("⚠️  Some modules failed to install, continuing...")
    
    # Wait for modules to install
    print("Waiting for modules to install...")
    time.sleep(10)
    
    # Step 4: Create sample data
    create_sample_data(uid, models)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print(f"📍 Odoo URL: {ODOO_URL}")
    print(f"🗄️  Database: {ODOO_DB}")
    print(f"👤 Username: {ADMIN_EMAIL}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print("\nNext steps:")
    print("1. Open Odoo in browser and verify modules are installed")
    print("2. Run the frontend to connect to real backend data")
    print("=" * 50)

if __name__ == "__main__":
    main()
