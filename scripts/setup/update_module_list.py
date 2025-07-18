#!/usr/bin/env python3
"""
Update module list and try to install modules
"""

import xmlrpc.client
import time

# Odoo connection settings
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_USERNAME = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'

def update_and_install():
    """Update module list and install modules"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Authenticate
        uid = common.authenticate(ODOO_DB, ADMIN_USERNAME, ADMIN_PASSWORD, {})
        if not uid:
            print("❌ Authentication failed")
            return
        
        print(f"✅ Authenticated as user ID: {uid}")
        
        # Update module list
        print("🔄 Updating module list...")
        try:
            models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'update_list',
                []
            )
            print("✅ Module list updated")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error updating module list: {e}")
        
        # FastAPI is no longer needed - focusing on simple HTTP controllers

        # Try to install extended_attendance
        print("📦 Attempting to install extended_attendance...")
        try:
            ext_att_ids = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'search',
                [[['name', '=', 'extended_attendance']]]
            )
            
            if ext_att_ids:
                models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [ext_att_ids]
                )
                print("✅ Extended attendance installation initiated")
                time.sleep(5)
                
                # Check status
                updated_info = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.module.module', 'read',
                    [ext_att_ids], {'fields': ['state']}
                )[0]
                print(f"   Extended attendance state: {updated_info['state']}")
                
        except Exception as e:
            print(f"❌ Error installing extended_attendance: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_and_install()
