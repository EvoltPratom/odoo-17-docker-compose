#!/usr/bin/env python3
"""
Export Manager - Script to test the custom attendance export functionality
"""

import xmlrpc.client
import json
import os
from datetime import datetime, timedelta
import pprint

# Configuration
URL = 'http://localhost:10017'
DB = 'test_attendance'  # Change this to your actual database name
USERNAME = 'admin'
PASSWORD = 'admin'  # Change this to your actual password

pp = pprint.PrettyPrinter(indent=2)

class ExportManager:
    def __init__(self):
        self.url = URL
        self.db = DB
        self.username = USERNAME
        self.password = PASSWORD
        self.uid = None
        self.models = None
        
    def connect(self):
        """Connect to Odoo"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                print(f"✅ Connected as user ID: {self.uid}")
                return True
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def check_export_module(self):
        """Check if the attendance export module is installed"""
        try:
            print("\n🔍 Checking attendance export module...")
            
            # Check if the model exists
            try:
                export_ids = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'hr.attendance.export', 'search', [[]], {'limit': 1}
                )
                print("✅ Attendance export module is installed and accessible")
                return True
            except Exception as e:
                print(f"❌ Attendance export module not found: {e}")
                print("💡 Make sure the 'attendance_export' module is installed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to check module: {e}")
            return False
    
    def list_export_configurations(self):
        """List all export configurations"""
        try:
            print("\n📋 === EXPORT CONFIGURATIONS ===")
            
            # Get all export configurations
            export_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'search', [[]]
            )
            
            if not export_ids:
                print("📭 No export configurations found")
                return []
            
            # Get detailed information
            exports = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'read', [export_ids],
                {'fields': [
                    'id', 'name', 'export_path', 'date_from', 'date_to',
                    'state', 'export_file', 'last_export_date', 'auto_export'
                ]}
            )
            
            print(f"📊 Found {len(exports)} export configurations:")
            print("-" * 80)
            
            for exp in exports:
                print(f"🏷️  ID: {exp['id']}")
                print(f"   Name: {exp['name']}")
                print(f"   Path: {exp['export_path']}")
                print(f"   Date Range: {exp['date_from']} to {exp['date_to']}")
                print(f"   State: {exp['state']}")
                print(f"   Auto Export: {'✅ Yes' if exp['auto_export'] else '❌ No'}")
                print(f"   Last Export: {exp['last_export_date'] or 'Never'}")
                print(f"   Export File: {exp['export_file'] or 'None'}")
                print("-" * 80)
            
            return exports
            
        except Exception as e:
            print(f"❌ Failed to list export configurations: {e}")
            return []
    
    def create_export_configuration(self, name, export_path, date_from, date_to, employee_ids=None, auto_export=False):
        """Create a new export configuration"""
        try:
            print(f"\n📝 Creating export configuration: {name}")
            
            export_data = {
                'name': name,
                'export_path': export_path,
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'auto_export': auto_export,
                'state': 'draft'
            }
            
            # Add employee filter if specified
            if employee_ids:
                export_data['employee_ids'] = [(6, 0, employee_ids)]
            
            # Create the configuration
            export_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'create', [export_data]
            )
            
            print(f"✅ Export configuration created with ID: {export_id}")
            
            # Get the created configuration details
            config = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'read', [export_id],
                {'fields': ['id', 'name', 'export_path', 'date_from', 'date_to', 'state']}
            )
            
            print(f"📋 Configuration details:")
            pp.pprint(config)
            
            return export_id
            
        except Exception as e:
            print(f"❌ Failed to create export configuration: {e}")
            return None
    
    def execute_export(self, export_id):
        """Execute an export configuration"""
        try:
            print(f"\n🚀 Executing export configuration {export_id}")
            
            # Execute the export
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'action_export', [export_id]
            )
            
            print(f"✅ Export executed successfully!")
            
            # Get updated configuration to see the results
            config = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'read', [export_id],
                {'fields': ['id', 'name', 'state', 'export_file', 'last_export_date']}
            )
            
            print(f"📋 Export results:")
            pp.pprint(config)
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to execute export: {e}")
            return None
    
    def create_export_wizard(self, name, export_path, date_from, date_to, employee_ids=None):
        """Create and execute export using the wizard"""
        try:
            print(f"\n🧙 Creating export wizard: {name}")
            
            wizard_data = {
                'name': name,
                'export_path': export_path,
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'auto_export': False
            }
            
            # Add employee filter if specified
            if employee_ids:
                wizard_data['employee_ids'] = [(6, 0, employee_ids)]
            
            # Create the wizard
            wizard_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'attendance.export.wizard', 'create', [wizard_data]
            )
            
            print(f"✅ Export wizard created with ID: {wizard_id}")
            
            # Execute the wizard
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'attendance.export.wizard', 'action_export', [wizard_id]
            )
            
            print(f"🎯 Wizard executed successfully!")
            print(f"📋 Result:")
            pp.pprint(result)
            
            return wizard_id
            
        except Exception as e:
            print(f"❌ Failed to create/execute wizard: {e}")
            return None
    
    def read_export_file(self, file_path):
        """Read and display the contents of an export file"""
        try:
            print(f"\n📖 Reading export file: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 Export file contents:")
            print(f"   Export Name: {data['export_info']['export_name']}")
            print(f"   Export Date: {data['export_info']['export_date']}")
            print(f"   Date Range: {data['export_info']['date_from']} to {data['export_info']['date_to']}")
            print(f"   Total Records: {data['export_info']['total_records']}")
            print(f"   Exported By: {data['export_info']['exported_by']}")
            
            print(f"\n📋 Attendance Records:")
            for i, record in enumerate(data['attendance_records'][:5]):  # Show first 5 records
                print(f"   Record {i+1}:")
                print(f"     Employee: {record['employee_name']} (ID: {record['employee_id']})")
                print(f"     Check In: {record['check_in']}")
                print(f"     Check Out: {record['check_out']}")
                print(f"     Hours: {record['worked_hours']}")
                print(f"     Department: {record['department']}")
            
            if len(data['attendance_records']) > 5:
                print(f"   ... and {len(data['attendance_records']) - 5} more records")
            
            return data
            
        except Exception as e:
            print(f"❌ Failed to read export file: {e}")
            return None
    
    def create_quick_export(self):
        """Create a quick export for the last 7 days"""
        try:
            print("\n⚡ Creating quick export for last 7 days...")
            
            # Date range: last 7 days
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=7)
            
            # Export path
            export_path = '/tmp/attendance_exports'
            
            # Create export name with timestamp
            export_name = f"Quick Export {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create and execute export
            export_id = self.create_export_configuration(
                name=export_name,
                export_path=export_path,
                date_from=date_from,
                date_to=date_to,
                auto_export=False
            )
            
            if export_id:
                result = self.execute_export(export_id)
                
                # Try to read the export file
                config = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'hr.attendance.export', 'read', [export_id],
                    {'fields': ['export_file', 'export_path']}
                )
                
                if config['export_file']:
                    file_path = os.path.join(config['export_path'], config['export_file'])
                    self.read_export_file(file_path)
                
                return export_id
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to create quick export: {e}")
            return None

def main():
    """Main function with interactive menu"""
    manager = ExportManager()
    
    print("📤 Export Manager")
    print("=" * 20)
    
    if not manager.connect():
        print("💥 Failed to connect to Odoo")
        return
    
    if not manager.check_export_module():
        print("💥 Export module not available")
        return
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. List export configurations")
        print("2. Create export configuration")
        print("3. Execute export")
        print("4. Create quick export (last 7 days)")
        print("5. Use export wizard")
        print("6. Read export file")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            manager.list_export_configurations()
        elif choice == '2':
            name = input("Export name: ").strip()
            path = input("Export path (default: /tmp/attendance_exports): ").strip() or "/tmp/attendance_exports"
            days_back = input("Days back from today (default: 7): ").strip() or "7"
            
            if name and days_back.isdigit():
                date_to = datetime.now().date()
                date_from = date_to - timedelta(days=int(days_back))
                manager.create_export_configuration(name, path, date_from, date_to)
        elif choice == '3':
            export_id = input("Export configuration ID: ").strip()
            if export_id.isdigit():
                manager.execute_export(int(export_id))
        elif choice == '4':
            manager.create_quick_export()
        elif choice == '5':
            name = input("Export name: ").strip()
            path = input("Export path (default: /tmp/attendance_exports): ").strip() or "/tmp/attendance_exports"
            days_back = input("Days back from today (default: 7): ").strip() or "7"
            
            if name and days_back.isdigit():
                date_to = datetime.now().date()
                date_from = date_to - timedelta(days=int(days_back))
                manager.create_export_wizard(name, path, date_from, date_to)
        elif choice == '6':
            file_path = input("Export file path: ").strip()
            if file_path:
                manager.read_export_file(file_path)
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
