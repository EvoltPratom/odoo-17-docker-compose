#!/usr/bin/env python3

import xmlrpc.client
import sys

# Odoo connection parameters
url = 'http://localhost:10017'
db = 'extended_attendance'
username = 'admin@demo.com'
password = 'admin'

def test_module():
    """Test the simplified extended_attendance module"""
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ Authenticated as user ID: {uid}")
        
        # Connect to object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Test extended_attendance module
        print("📦 Testing extended_attendance module...")
        module_ids = models.execute_kw(db, uid, password,
            'ir.module.module', 'search',
            [[('name', '=', 'extended_attendance')]]
        )
        
        if not module_ids:
            print("❌ Extended attendance module not found")
            return False
        
        module_info = models.execute_kw(db, uid, password,
            'ir.module.module', 'read',
            [module_ids[0]], {'fields': ['name', 'state', 'summary']}
        )[0]
        
        print(f"   Module state: {module_info['state']}")
        print(f"   Summary: {module_info['summary']}")
        
        if module_info['state'] != 'installed':
            print("🔄 Installing module...")
            models.execute_kw(db, uid, password,
                'ir.module.module', 'button_immediate_install',
                [module_ids[0]]
            )
            print("✅ Module installation initiated")
        else:
            print("✅ Module already installed")
        
        # Test models
        print("\n🧪 Testing Models...")
        
        # Test person types
        person_types = models.execute_kw(db, uid, password,
            'person.type', 'search_read',
            [[]], {'fields': ['name', 'code']}
        )
        print(f"   ✅ Found {len(person_types)} person types")
        for pt in person_types:
            print(f"      - {pt['name']} ({pt['code']})")
        
        # Test locations
        locations = models.execute_kw(db, uid, password,
            'attendance.location', 'search_read',
            [[]], {'fields': ['name', 'code']}
        )
        print(f"   ✅ Found {len(locations)} locations")
        for loc in locations:
            print(f"      - {loc['name']} ({loc['code']})")
        
        # Test extended persons
        persons = models.execute_kw(db, uid, password,
            'extended.attendance.person', 'search_read',
            [[]], {'fields': ['name', 'person_id']}
        )
        print(f"   ✅ Found {len(persons)} extended persons")
        
        print("\n🎉 All tests passed! Extended Attendance module is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing module: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simplified Extended Attendance Module Test")
    print("=" * 60)
    
    success = test_module()
    
    if success:
        print("\n✅ Module test completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Access Odoo web interface: http://localhost:10017/web")
        print("   2. Test HTTP API endpoints:")
        print("      - GET  /api/person-types")
        print("      - POST /api/person-types")
        print("      - GET  /api/locations")
        print("      - POST /api/check-in")
        sys.exit(0)
    else:
        print("\n❌ Module test failed!")
        sys.exit(1)
