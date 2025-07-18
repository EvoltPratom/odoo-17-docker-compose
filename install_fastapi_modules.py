#!/usr/bin/env python3
"""
Install FastAPI modules in Odoo via XML-RPC
"""

import xmlrpc.client

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_EMAIL = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'

def install_modules():
    """Install FastAPI modules via Odoo API"""
    
    print("🔗 Connecting to Odoo...")
    
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ADMIN_EMAIL, ADMIN_PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ Connected, UID: {uid}")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Modules to install
        modules_to_install = ['base_rest', 'extendable', 'fastapi']
        
        for module_name in modules_to_install:
            print(f"\n📦 Installing module: {module_name}")
            
            # Search for the module
            module_ids = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]]
            )
            
            if not module_ids:
                print(f"❌ Module {module_name} not found")
                continue
            
            # Get module info
            module_info = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'read',
                [module_ids], {'fields': ['name', 'state']}
            )[0]
            
            print(f"   Current state: {module_info['state']}")
            
            if module_info['state'] == 'installed':
                print(f"   ✅ Already installed")
                continue
            elif module_info['state'] == 'uninstalled':
                print(f"   🔄 Installing...")
                try:
                    # Install the module
                    models.execute_kw(
                        ODOO_DB, uid, ADMIN_PASSWORD,
                        'ir.module.module', 'button_immediate_install',
                        [module_ids]
                    )
                    print(f"   ✅ Installation initiated")
                except Exception as e:
                    print(f"   ❌ Installation failed: {e}")
            else:
                print(f"   ⚠️  Module state: {module_info['state']}")
        
        print("\n🎯 Checking extended_attendance module...")
        
        # Check if extended_attendance module exists and update it
        ext_module_ids = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', 'extended_attendance')]]
        )
        
        if ext_module_ids:
            ext_module_info = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.module.module', 'read',
                [ext_module_ids], {'fields': ['name', 'state']}
            )[0]
            
            print(f"   Extended attendance state: {ext_module_info['state']}")
            
            if ext_module_info['state'] == 'installed':
                print("   🔄 Upgrading extended_attendance...")
                try:
                    models.execute_kw(
                        ODOO_DB, uid, ADMIN_PASSWORD,
                        'ir.module.module', 'button_immediate_upgrade',
                        [ext_module_ids]
                    )
                    print("   ✅ Upgrade initiated")
                except Exception as e:
                    print(f"   ❌ Upgrade failed: {e}")
            elif ext_module_info['state'] == 'uninstalled':
                print("   🔄 Installing extended_attendance...")
                try:
                    models.execute_kw(
                        ODOO_DB, uid, ADMIN_PASSWORD,
                        'ir.module.module', 'button_immediate_install',
                        [ext_module_ids]
                    )
                    print("   ✅ Installation initiated")
                except Exception as e:
                    print(f"   ❌ Installation failed: {e}")
        else:
            print("   ❌ Extended attendance module not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_fastapi_endpoints():
    """Check if FastAPI endpoints are working"""
    
    print("\n🧪 Testing FastAPI endpoints...")
    
    import urllib.request
    import urllib.error
    
    test_urls = [
        f'{ODOO_URL}/api/docs',
        f'{ODOO_URL}/api/attendance/docs',
        f'{ODOO_URL}/api/openapi.json'
    ]
    
    for url in test_urls:
        try:
            response = urllib.request.urlopen(url)
            if response.getcode() == 200:
                print(f"   ✅ {url} - Working!")
            else:
                print(f"   ❌ {url} - Status: {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"   ❌ {url} - HTTP Error: {e.code}")
        except Exception as e:
            print(f"   ❌ {url} - Error: {e}")

def main():
    """Main function"""
    
    print("🚀 Installing FastAPI Modules in Odoo")
    print("=" * 50)
    
    success = install_modules()
    
    if success:
        print("\n⏳ Waiting for modules to install...")
        import time
        time.sleep(10)
        
        check_fastapi_endpoints()
        
        print("\n" + "=" * 50)
        print("🎉 Installation completed!")
        print("🌐 Try accessing:")
        print(f"   - Swagger UI: {ODOO_URL}/api/docs")
        print(f"   - Attendance API: {ODOO_URL}/api/attendance/docs")
        print("=" * 50)
    else:
        print("\n❌ Installation failed")

if __name__ == "__main__":
    main()
