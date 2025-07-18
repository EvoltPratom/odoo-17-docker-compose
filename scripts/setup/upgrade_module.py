#!/usr/bin/env python3

import xmlrpc.client
import sys

# Odoo connection parameters
url = 'http://localhost:10017'
db = 'extended_attendance'
username = 'admin@demo.com'
password = 'admin'

def upgrade_module():
    """Upgrade the extended_attendance module to reload demo data"""
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
        
        # Find the extended_attendance module
        module_ids = models.execute_kw(db, uid, password,
            'ir.module.module', 'search',
            [[('name', '=', 'extended_attendance')]]
        )
        
        if not module_ids:
            print("❌ Extended attendance module not found")
            return False
        
        module_id = module_ids[0]
        
        # Get module info
        module_info = models.execute_kw(db, uid, password,
            'ir.module.module', 'read',
            [module_id], {'fields': ['name', 'state', 'demo']}
        )[0]
        
        print(f"📦 Module: {module_info['name']}")
        print(f"   State: {module_info['state']}")
        print(f"   Demo: {module_info['demo']}")
        
        # Upgrade the module
        print("🔄 Upgrading module...")
        models.execute_kw(db, uid, password,
            'ir.module.module', 'button_immediate_upgrade',
            [module_id]
        )
        
        print("✅ Module upgrade initiated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error upgrading module: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Extended Attendance Module Upgrade")
    print("=" * 60)
    
    success = upgrade_module()
    
    if success:
        print("\n🎉 Module upgrade completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Module upgrade failed!")
        sys.exit(1)
