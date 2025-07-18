#!/usr/bin/env python3
"""
Check what models are available in Odoo
"""

import xmlrpc.client

# Configuration
URL = 'http://localhost:10017'
DB = 'extended_attendance'
USERNAME = 'admin@demo.com'
PASSWORD = 'admin'

def check_models():
    try:
        # Connect
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed")
            return
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        print(f"✅ Connected as UID: {uid}")
        print("=" * 50)
        
        # Check for attendance-related models
        attendance_models = [
            'hr.employee',
            'hr.attendance', 
            'hr.attendance.export',
            'attendance.export.wizard',
            'hr.department',
            'hr.job'
        ]
        
        print("🔍 Checking attendance-related models:")
        print("-" * 30)
        
        available_models = []
        
        for model in attendance_models:
            try:
                # Try to search for records (this will fail if model doesn't exist)
                result = models.execute_kw(DB, uid, PASSWORD, model, 'search', [[]], {'limit': 1})
                print(f"✅ {model} - Available")
                available_models.append(model)
            except Exception as e:
                print(f"❌ {model} - Not available ({str(e)[:50]}...)")
        
        print("\n" + "=" * 50)
        print("📊 Available Models Summary:")
        for model in available_models:
            print(f"  ✅ {model}")
        
        # Check what fields are available in hr.attendance
        if 'hr.attendance' in available_models:
            print("\n🔍 hr.attendance model fields:")
            try:
                fields = models.execute_kw(DB, uid, PASSWORD, 'hr.attendance', 'fields_get', [])
                important_fields = ['employee_id', 'check_in', 'check_out', 'worked_hours']
                for field in important_fields:
                    if field in fields:
                        print(f"  ✅ {field}: {fields[field].get('string', 'No description')}")
                    else:
                        print(f"  ❌ {field}: Not found")
            except Exception as e:
                print(f"  ❌ Error getting fields: {e}")
        
        # Check installed modules
        print("\n🔍 Checking installed modules:")
        try:
            module_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search', [
                [('state', '=', 'installed'), ('name', 'ilike', 'attendance')]
            ])
            
            if module_ids:
                modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'read', [module_ids], 
                                          {'fields': ['name', 'display_name', 'state']})
                for module in modules:
                    print(f"  ✅ {module['name']}: {module['display_name']}")
            else:
                print("  ❌ No attendance-related modules found")
                
        except Exception as e:
            print(f"  ❌ Error checking modules: {e}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    check_models()
