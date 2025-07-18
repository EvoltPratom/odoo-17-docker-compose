#!/usr/bin/env python3
"""
Test admin passwords for admin@demo.com
"""

import xmlrpc.client

# Odoo connection settings
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'

def test_admin_passwords():
    """Test various passwords for admin@demo.com"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        # Try common admin passwords
        admin_passwords = [
            'admin', 'password', '123456', 'odoo', '', 'admin123', 
            'demo', 'Administrator', 'mitchell', 'Mitchell', 
            'admin@demo.com', 'demo123', 'password123', 'admin@demo',
            'test', 'Test', '1234', '12345', 'qwerty'
        ]
        
        print(f"🔍 Testing passwords for admin@demo.com...")
        for password in admin_passwords:
            try:
                admin_uid = common.authenticate(ODOO_DB, 'admin@demo.com', password, {})
                if admin_uid:
                    print(f"✅ SUCCESS! Password: '{password}' (User ID: {admin_uid})")
                    return 'admin@demo.com', password
                else:
                    print(f"❌ Failed: admin@demo.com / {password}")
            except Exception as e:
                print(f"❌ Error testing admin@demo.com/{password}: {e}")
                
        print("❌ No working password found")
        return None, None
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

if __name__ == "__main__":
    test_admin_passwords()
