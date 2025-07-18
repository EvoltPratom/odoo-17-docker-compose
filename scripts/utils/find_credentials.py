#!/usr/bin/env python3
"""
Credential Finder - Help find the right Odoo login credentials
"""

import xmlrpc.client

# Configuration
URL = 'http://localhost:10017'
DB = 'attendance_test'

def test_credentials(username, password):
    """Test a username/password combination"""
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, username, password, {})
        if uid:
            print(f"✅ SUCCESS! Username: '{username}', Password: '{password}' (User ID: {uid})")
            return True
        else:
            print(f"❌ Failed: '{username}' / '{password}'")
            return False
    except Exception as e:
        print(f"💥 Error testing '{username}' / '{password}': {e}")
        return False

def find_credentials():
    """Try common credential combinations"""
    print("🔍 Testing common Odoo credential combinations...")
    print("=" * 50)
    
    # Common username/password combinations
    common_combos = [
        ('admin', 'admin'),
        ('admin', 'password'),
        ('admin', '123456'),
        ('admin', 'odoo'),
        ('admin', ''),  # empty password
        ('admin', 'admin123'),
        ('admin', 'Administrator'),
        ('administrator', 'admin'),
        ('administrator', 'password'),
        ('demo', 'demo'),
        ('user', 'user'),
        ('odoo', 'odoo'),
    ]
    
    for username, password in common_combos:
        if test_credentials(username, password):
            print(f"\n🎉 Found working credentials!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            return username, password
    
    print("\n❌ None of the common combinations worked.")
    return None, None

def manual_test():
    """Allow manual testing of credentials"""
    print("\n🔧 Manual credential testing")
    print("=" * 30)
    
    while True:
        username = input("Enter username (or 'quit' to exit): ").strip()
        if username.lower() == 'quit':
            break
            
        password = input("Enter password: ").strip()
        
        if test_credentials(username, password):
            print(f"\n🎉 Success! These credentials work:")
            print(f"Username: {username}")
            print(f"Password: {password}")
            return username, password
    
    return None, None

def check_database_info():
    """Get database information"""
    try:
        print("\n📊 Database Information:")
        print("=" * 25)
        
        # List databases
        db_service = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/db')
        databases = db_service.list()
        print(f"Available databases: {databases}")
        
        # Get server info
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version_info = common.version()
        print(f"Server version: {version_info['server_version']}")
        
    except Exception as e:
        print(f"❌ Failed to get database info: {e}")

def reset_admin_password_instructions():
    """Show instructions for resetting admin password"""
    print("\n🔧 How to Reset Admin Password")
    print("=" * 35)
    print("If you can't find the credentials, you can reset them:")
    print()
    print("Method 1 - Via Web Interface:")
    print("1. Go to http://localhost:10017")
    print("2. Click 'Manage Databases'")
    print("3. Use master password: 'minhng.info' (from your config)")
    print("4. Select your database and click 'Set a new password'")
    print()
    print("Method 2 - Via Docker Container:")
    print("1. docker-compose exec odoo17 bash")
    print("2. odoo shell -d attendance_test")
    print("3. In the shell:")
    print("   user = env['res.users'].search([('login', '=', 'admin')])")
    print("   user.password = 'newpassword'")
    print("   env.cr.commit()")
    print()
    print("Method 3 - Create New Database:")
    print("1. Go to http://localhost:10017")
    print("2. Create a new database with known credentials")

def main():
    """Main function"""
    print("🔐 Odoo Credential Finder")
    print("=" * 25)
    
    # Check database info first
    check_database_info()
    
    # Try common credentials
    username, password = find_credentials()
    
    if not username:
        print("\n🤔 Common credentials didn't work. Let's try manual testing...")
        username, password = manual_test()
    
    if not username:
        print("\n💡 Still no luck? Here are your options:")
        reset_admin_password_instructions()
    else:
        print(f"\n📝 Update your scripts with these credentials:")
        print(f"USERNAME = '{username}'")
        print(f"PASSWORD = '{password}'")
        
        # Test with a simple API call
        try:
            common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
            uid = common.authenticate(DB, username, password, {})
            models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
            
            # Get user info
            user_info = models.execute_kw(
                DB, uid, password,
                'res.users', 'read', [uid],
                {'fields': ['name', 'login', 'email']}
            )
            
            print(f"\n👤 Logged in as:")
            print(f"   Name: {user_info['name']}")
            print(f"   Login: {user_info['login']}")
            print(f"   Email: {user_info['email'] or 'Not set'}")
            
        except Exception as e:
            print(f"❌ Error getting user info: {e}")

if __name__ == "__main__":
    main()
