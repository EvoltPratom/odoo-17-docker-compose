#!/usr/bin/env python3
"""
Simple script to check Odoo status and list available databases
"""

import xmlrpc.client
import json

# Odoo connection parameters
URL = 'http://localhost:10017'

def list_databases():
    """List available databases"""
    try:
        db_service = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/db')
        databases = db_service.list()
        print(f"Available databases: {databases}")
        return databases
    except Exception as e:
        print(f"Failed to list databases: {e}")
        return []

def check_odoo_version():
    """Check Odoo version"""
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version = common.version()
        print(f"Odoo version info: {version}")
        return version
    except Exception as e:
        print(f"Failed to get version: {e}")
        return None

def main():
    """Main function"""
    print("Checking Odoo status...")
    print("=" * 40)
    
    # Check version
    version = check_odoo_version()
    
    # List databases
    databases = list_databases()
    
    if databases:
        print(f"\nYou can access Odoo at: {URL}")
        print("Available databases:")
        for db in databases:
            print(f"  - {db}")
    else:
        print("\nNo databases found. You need to create one through the web interface.")
        print(f"Visit: {URL}/web/database/manager")

if __name__ == "__main__":
    main()
