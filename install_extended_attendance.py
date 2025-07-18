#!/usr/bin/env python3
"""
Install Extended Attendance Module via API
"""

import xmlrpc.client
import time

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_EMAIL = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'

def install_modules():
    """Install the extended attendance modules"""
    try:
        print("🔗 Connecting to Odoo...")
        
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ADMIN_EMAIL, ADMIN_PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ Connected, UID: {uid}")
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Update module list first
        print("📋 Updating module list...")
        models.execute_kw(ODOO_DB, uid, ADMIN_PASSWORD, 'ir.module.module', 'update_list', [])
        
        # Install base HR Attendance if not installed
        print("📦 Installing HR Attendance...")
        hr_attendance = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'hr_attendance']]]
        )
        
        if hr_attendance:
            module_state = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'read',
                [hr_attendance], {'fields': ['state']}
            )
            
            if module_state[0]['state'] != 'installed':
                models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [hr_attendance]
                )
                print("✅ HR Attendance installed")
            else:
                print("✅ HR Attendance already installed")
        
        # Install Extended Attendance
        print("🚀 Installing Extended Attendance...")
        extended_attendance = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'extended_attendance']]]
        )
        
        if extended_attendance:
            module_state = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'read',
                [extended_attendance], {'fields': ['state']}
            )
            
            if module_state[0]['state'] != 'installed':
                models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [extended_attendance]
                )
                print("✅ Extended Attendance installed")
            else:
                print("✅ Extended Attendance already installed")
        else:
            print("❌ Extended Attendance module not found")
            return False
        
        # Wait for installation
        print("⏳ Waiting for installation to complete...")
        time.sleep(10)
        
        # Create sample data
        print("📝 Creating sample locations...")
        try:
            # Create attendance locations
            location_data = {
                'name': 'Main Office',
                'code': 'MAIN_OFFICE',
                'building': 'Headquarters',
                'floor': 'Ground Floor',
                'capacity': 50,
                'description': 'Main office area'
            }
            
            location_id = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'attendance.location', 'create',
                [location_data]
            )
            print(f"✅ Created location: {location_data['name']} (ID: {location_id})")
            
        except Exception as e:
            print(f"⚠️  Could not create location: {e}")
        
        print("📝 Creating sample person types...")
        try:
            # Create person types
            person_type_data = {
                'name': 'Employee',
                'code': 'EMP',
                'default_access_level': 'standard',
                'is_system': False,
                'description': 'Regular employees'
            }
            
            person_type_id = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'person.type', 'create',
                [person_type_data]
            )
            print(f"✅ Created person type: {person_type_data['name']} (ID: {person_type_id})")
            
        except Exception as e:
            print(f"⚠️  Could not create person type: {e}")
        
        # Test if models are working
        print("🧪 Testing models...")
        try:
            locations = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'attendance.location', 'search_read', [],
                {'fields': ['name', 'code'], 'limit': 5}
            )
            print(f"✅ Found {len(locations)} locations")
            for loc in locations:
                print(f"   - {loc['name']} ({loc['code']})")
                
        except Exception as e:
            print(f"❌ Location model test failed: {e}")
        
        try:
            person_types = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'person.type', 'search_read', [],
                {'fields': ['name', 'code'], 'limit': 5}
            )
            print(f"✅ Found {len(person_types)} person types")
            for pt in person_types:
                print(f"   - {pt['name']} ({pt['code']})")
                
        except Exception as e:
            print(f"❌ Person type model test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def main():
    print("🚀 Installing Extended Attendance System...")
    print("=" * 50)
    
    if install_modules():
        print("\n" + "=" * 50)
        print("🎉 Installation completed!")
        print("📍 Odoo URL: http://localhost:10017")
        print("🗄️  Database: extended_attendance")
        print("👤 Username: admin@demo.com")
        print("🔑 Password: admin")
        print("\n✅ Your backend now has:")
        print("   - Attendance locations")
        print("   - Person types")
        print("   - Extended attendance tracking")
        print("\n🔄 Refresh your frontend to see real data!")
        print("=" * 50)
    else:
        print("\n❌ Installation failed. Check the errors above.")

if __name__ == "__main__":
    main()
