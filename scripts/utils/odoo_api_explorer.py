#!/usr/bin/env python3
"""
Odoo API Explorer - Interactive script to explore and test Odoo attendance functionality
"""

import xmlrpc.client
import json
from datetime import datetime, timedelta
import pprint

# Configuration
URL = 'http://localhost:10017'
DB = 'extended_attendance'  # Your working database

# Your working credentials:
USERNAME = 'admin@demo.com'
PASSWORD = 'admin'

# Other common defaults to try:
# PASSWORD = 'password'
# PASSWORD = '123456'
# PASSWORD = 'odoo'
# PASSWORD = '' (empty password)

pp = pprint.PrettyPrinter(indent=2)

class OdooAPIExplorer:
    def __init__(self):
        self.url = URL
        self.db = DB
        self.username = USERNAME
        self.password = PASSWORD
        self.uid = None
        self.models = None
        self.common = None
        
    def connect(self):
        """Connect to Odoo and authenticate"""
        try:
            print(f"🔌 Connecting to Odoo at {self.url}...")
            
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Get server version info
            version_info = self.common.version()
            print(f"📊 Server Info:")
            pp.pprint(version_info)
            
            # Authenticate
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Successfully authenticated as user ID: {self.uid}")
                
                # Models endpoint for data operations
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                return True
            else:
                print("❌ Authentication failed")
                return False
                
        except Exception as e:
            print(f"💥 Connection failed: {e}")
            return False
    
    def list_databases(self):
        """List available databases"""
        try:
            db_service = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/db')
            databases = db_service.list()
            print(f"📚 Available databases: {databases}")
            return databases
        except Exception as e:
            print(f"❌ Failed to list databases: {e}")
            return []
    
    def check_user_access(self):
        """Check current user's access rights"""
        try:
            # Get current user info
            user_data = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'read', [self.uid], 
                {'fields': ['name', 'login', 'groups_id']}
            )
            print(f"👤 Current User:")
            pp.pprint(user_data)
            
            # Check access to attendance models
            models_to_check = ['hr.employee', 'hr.attendance', 'hr.attendance.export']
            for model in models_to_check:
                try:
                    access = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        model, 'check_access_rights', ['read'], {'raise_exception': False}
                    )
                    print(f"🔐 Access to {model}: {'✅ Yes' if access else '❌ No'}")
                except:
                    print(f"🔐 Access to {model}: ❌ No (model not found)")
                    
        except Exception as e:
            print(f"❌ Failed to check user access: {e}")
    
    def list_employees(self):
        """List all employees"""
        try:
            print("\n👥 === EMPLOYEES ===")
            
            # Search for all employees
            employee_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'search', [[]]
            )
            
            if not employee_ids:
                print("📭 No employees found")
                return []
            
            # Get employee details
            employees = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_ids],
                {'fields': ['id', 'name', 'barcode', 'work_email', 'department_id', 'job_id']}
            )
            
            print(f"📊 Found {len(employees)} employees:")
            for emp in employees:
                print(f"  🏷️  ID: {emp['id']}")
                print(f"     Name: {emp['name']}")
                print(f"     Barcode: {emp['barcode'] or 'None'}")
                print(f"     Email: {emp['work_email'] or 'None'}")
                print(f"     Department: {emp['department_id'][1] if emp['department_id'] else 'None'}")
                print(f"     Job: {emp['job_id'][1] if emp['job_id'] else 'None'}")
                print("     " + "-" * 40)
            
            return employees
            
        except Exception as e:
            print(f"❌ Failed to list employees: {e}")
            return []
    
    def create_employee(self, name, barcode=None, email=None):
        """Create a new employee"""
        try:
            print(f"\n👤 Creating employee: {name}")
            
            employee_data = {
                'name': name,
                'barcode': barcode,
                'work_email': email,
            }
            
            # Remove None values
            employee_data = {k: v for k, v in employee_data.items() if v is not None}
            
            employee_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'create', [employee_data]
            )
            
            print(f"✅ Employee created with ID: {employee_id}")
            
            # Get the created employee details
            employee = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_id],
                {'fields': ['id', 'name', 'barcode', 'work_email']}
            )
            
            print(f"📋 Employee details:")
            pp.pprint(employee)
            
            return employee_id
            
        except Exception as e:
            print(f"❌ Failed to create employee: {e}")
            return None
    
    def list_attendances(self, limit=10):
        """List attendance records"""
        try:
            print(f"\n⏰ === ATTENDANCE RECORDS (Last {limit}) ===")
            
            # Search for attendance records (ordered by most recent)
            attendance_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search', [[]],
                {'order': 'check_in desc', 'limit': limit}
            )
            
            if not attendance_ids:
                print("📭 No attendance records found")
                return []
            
            # Get attendance details
            attendances = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'read', [attendance_ids],
                {'fields': ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']}
            )
            
            print(f"📊 Found {len(attendances)} attendance records:")
            for att in attendances:
                print(f"  🏷️  ID: {att['id']}")
                print(f"     Employee: {att['employee_id'][1] if att['employee_id'] else 'Unknown'}")
                print(f"     Check In: {att['check_in']}")
                print(f"     Check Out: {att['check_out'] or 'Still working'}")
                print(f"     Worked Hours: {att['worked_hours']:.2f}")
                print("     " + "-" * 40)
            
            return attendances
            
        except Exception as e:
            print(f"❌ Failed to list attendances: {e}")
            return []

if __name__ == "__main__":
    explorer = OdooAPIExplorer()
    
    print("🚀 Odoo API Explorer Starting...")
    print("=" * 50)
    
    # List available databases first
    explorer.list_databases()
    
    # Connect to Odoo
    if explorer.connect():
        # Check user access
        explorer.check_user_access()
        
        # List existing data
        explorer.list_employees()
        explorer.list_attendances()
        
        print("\n✨ Basic exploration complete!")
        print("💡 Use the individual functions to create employees and attendance records")
    else:
        print("💥 Failed to connect to Odoo")
