#!/usr/bin/env python3
"""
Find admin users in the Odoo database
"""

import xmlrpc.client

# Odoo connection settings
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'

def find_admin_users():
    """Find admin users in the system"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Try to authenticate with demo user first
        uid = common.authenticate(ODOO_DB, 'demo', 'demo', {})
        if not uid:
            print("❌ Authentication failed")
            return
        
        print(f"✅ Authenticated as demo user (ID: {uid})")
        
        # Try to get all users
        try:
            users = models.execute_kw(
                ODOO_DB, uid, 'demo',
                'res.users', 'search_read',
                [[]], {'fields': ['login', 'name', 'active', 'groups_id']}
            )
            
            print(f"\n👥 Found {len(users)} users:")
            for user in users:
                print(f"   - {user['name']} (login: {user['login']}, active: {user['active']})")
                
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            
        # Try to get admin group members
        try:
            admin_groups = models.execute_kw(
                ODOO_DB, uid, 'demo',
                'res.groups', 'search_read',
                [[['name', 'ilike', 'admin']]], {'fields': ['name', 'users']}
            )
            
            print(f"\n🔐 Admin groups:")
            for group in admin_groups:
                print(f"   - {group['name']}: {len(group['users'])} users")
                
        except Exception as e:
            print(f"❌ Error getting admin groups: {e}")
            
        # Try common admin passwords
        admin_passwords = ['admin', 'password', '123456', 'odoo', '', 'admin123']
        
        print(f"\n🔍 Testing admin passwords...")
        for password in admin_passwords:
            try:
                admin_uid = common.authenticate(ODOO_DB, 'admin', password, {})
                if admin_uid:
                    print(f"✅ SUCCESS! Admin password: '{password}' (User ID: {admin_uid})")
                    return 'admin', password
                else:
                    print(f"❌ Failed: admin / {password}")
            except Exception as e:
                print(f"❌ Error testing admin/{password}: {e}")
                
        # Try to find users with admin privileges
        try:
            # Look for users in the "Settings" group (usually admins)
            settings_group = models.execute_kw(
                ODOO_DB, uid, 'demo',
                'res.groups', 'search',
                [[['name', '=', 'Settings']]]
            )
            
            if settings_group:
                group_users = models.execute_kw(
                    ODOO_DB, uid, 'demo',
                    'res.groups', 'read',
                    [settings_group], {'fields': ['users']}
                )[0]['users']
                
                if group_users:
                    admin_user_info = models.execute_kw(
                        ODOO_DB, uid, 'demo',
                        'res.users', 'read',
                        [group_users], {'fields': ['login', 'name']}
                    )
                    
                    print(f"\n👑 Users with Settings access:")
                    for user in admin_user_info:
                        print(f"   - {user['name']} (login: {user['login']})")
                        
        except Exception as e:
            print(f"❌ Error finding admin users: {e}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    find_admin_users()
