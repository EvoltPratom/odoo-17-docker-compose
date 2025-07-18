#!/usr/bin/env python3
"""
Quick Start Script - Complete demo of Odoo attendance functionality
"""

import xmlrpc.client
import json
from datetime import datetime, timedelta
import pprint
import time

# Configuration
URL = 'http://localhost:10017'
DB = 'test_attendance'  # Change this to your actual database name
USERNAME = 'admin'
PASSWORD = 'admin'  # Change this to your actual password

pp = pprint.PrettyPrinter(indent=2)

class QuickStartDemo:
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
            print(f"🔌 Connecting to Odoo at {self.url}...")
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                print(f"✅ Connected successfully as user ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed")
                print("💡 Make sure:")
                print("   - Odoo is running on localhost:10017")
                print("   - Database name is correct")
                print("   - Username/password are correct")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Make sure Odoo is running: docker-compose up -d")
            return False
    
    def check_modules(self):
        """Check if required modules are installed"""
        print("\n🔍 Checking required modules...")
        
        modules_to_check = {
            'hr_attendance': 'HR Attendance (Core)',
            'hr.attendance.export': 'Attendance Export (Custom)'
        }
        
        all_good = True
        
        for module, description in modules_to_check.items():
            try:
                if module == 'hr.attendance.export':
                    # Check if our custom model exists
                    result = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'hr.attendance.export', 'search', [[]], {'limit': 1}
                    )
                    print(f"✅ {description} - Available")
                else:
                    # Check if core attendance model exists
                    result = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'hr.attendance', 'search', [[]], {'limit': 1}
                    )
                    print(f"✅ {description} - Available")
            except Exception as e:
                print(f"❌ {description} - Not available")
                all_good = False
        
        return all_good
    
    def create_demo_employees(self):
        """Create demo employees"""
        print("\n👥 Creating demo employees...")
        
        demo_employees = [
            {'name': 'Alice Johnson', 'barcode': 'DEMO001', 'email': 'alice@demo.com'},
            {'name': 'Bob Smith', 'barcode': 'DEMO002', 'email': 'bob@demo.com'},
            {'name': 'Carol Davis', 'barcode': 'DEMO003', 'email': 'carol@demo.com'}
        ]
        
        created_employees = []
        
        for emp_data in demo_employees:
            try:
                # Check if employee already exists
                existing = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'hr.employee', 'search',
                    [[('barcode', '=', emp_data['barcode'])]]
                )
                
                if existing:
                    print(f"👤 {emp_data['name']} already exists (ID: {existing[0]})")
                    created_employees.append(existing[0])
                else:
                    employee_id = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'hr.employee', 'create', [{
                            'name': emp_data['name'],
                            'barcode': emp_data['barcode'],
                            'work_email': emp_data['email']
                        }]
                    )
                    print(f"👤 Created {emp_data['name']} (ID: {employee_id})")
                    created_employees.append(employee_id)
                    
            except Exception as e:
                print(f"❌ Failed to create {emp_data['name']}: {e}")
        
        return created_employees
    
    def create_demo_attendance(self, employee_ids):
        """Create demo attendance records"""
        print("\n⏰ Creating demo attendance records...")
        
        # Create attendance for the last 3 days
        base_date = datetime.now() - timedelta(days=3)
        
        created_records = []
        
        for day in range(3):
            current_date = base_date + timedelta(days=day)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
                
            for i, emp_id in enumerate(employee_ids):
                try:
                    # Morning check-in
                    check_in = current_date.replace(hour=8 + i//2, minute=i*15, second=0, microsecond=0)
                    
                    # Evening check-out
                    check_out = check_in + timedelta(hours=8, minutes=30)
                    
                    attendance_data = {
                        'employee_id': emp_id,
                        'check_in': check_in.strftime('%Y-%m-%d %H:%M:%S'),
                        'check_out': check_out.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    attendance_id = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'hr.attendance', 'create', [attendance_data]
                    )
                    
                    created_records.append(attendance_id)
                    print(f"⏰ Created attendance for employee {emp_id} on {check_in.strftime('%Y-%m-%d')}")
                    
                except Exception as e:
                    print(f"❌ Failed to create attendance for employee {emp_id}: {e}")
        
        return created_records
    
    def demo_attendance_queries(self, employee_ids):
        """Demonstrate various attendance queries"""
        print("\n📊 Demonstrating attendance queries...")
        
        try:
            # 1. Get all attendance records
            print("\n1️⃣ All attendance records:")
            all_attendance = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search_read', [[]],
                {'fields': ['employee_id', 'check_in', 'check_out', 'worked_hours'], 'limit': 5}
            )
            
            for att in all_attendance:
                emp_name = att['employee_id'][1] if att['employee_id'] else 'Unknown'
                print(f"   {emp_name}: {att['check_in']} - {att['check_out']} ({att['worked_hours']:.2f}h)")
            
            # 2. Get attendance for specific employee
            if employee_ids:
                print(f"\n2️⃣ Attendance for employee {employee_ids[0]}:")
                emp_attendance = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'hr.attendance', 'search_read',
                    [[('employee_id', '=', employee_ids[0])]],
                    {'fields': ['check_in', 'check_out', 'worked_hours']}
                )
                
                total_hours = sum(att['worked_hours'] for att in emp_attendance)
                print(f"   Total records: {len(emp_attendance)}")
                print(f"   Total hours: {total_hours:.2f}")
            
            # 3. Get today's attendance
            print("\n3️⃣ Today's attendance:")
            today = datetime.now().date()
            today_attendance = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search_read',
                [[('check_in', '>=', today.strftime('%Y-%m-%d 00:00:00'))]],
                {'fields': ['employee_id', 'check_in', 'check_out']}
            )
            
            if today_attendance:
                for att in today_attendance:
                    emp_name = att['employee_id'][1] if att['employee_id'] else 'Unknown'
                    status = "Working" if not att['check_out'] else "Finished"
                    print(f"   {emp_name}: {status}")
            else:
                print("   No attendance records for today")
                
        except Exception as e:
            print(f"❌ Failed to query attendance: {e}")
    
    def demo_export_functionality(self):
        """Demonstrate export functionality"""
        print("\n📤 Demonstrating export functionality...")
        
        try:
            # Create export configuration
            export_config = {
                'name': 'Demo Export',
                'export_path': '/tmp/attendance_exports',
                'date_from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'date_to': datetime.now().strftime('%Y-%m-%d'),
                'auto_export': False
            }
            
            export_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'create', [export_config]
            )
            
            print(f"✅ Created export configuration (ID: {export_id})")
            
            # Execute export
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'action_export', [export_id]
            )
            
            print("✅ Export executed successfully!")
            
            # Get export details
            export_details = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance.export', 'read', [export_id],
                {'fields': ['name', 'state', 'export_file', 'last_export_date']}
            )
            
            print(f"📋 Export details:")
            print(f"   Name: {export_details['name']}")
            print(f"   State: {export_details['state']}")
            print(f"   File: {export_details['export_file']}")
            print(f"   Date: {export_details['last_export_date']}")
            
        except Exception as e:
            print(f"❌ Export functionality not available: {e}")
            print("💡 Make sure the attendance_export module is installed")
    
    def run_complete_demo(self):
        """Run the complete demo"""
        print("🚀 Starting Complete Odoo Attendance Demo")
        print("=" * 50)
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        # Step 2: Check modules
        if not self.check_modules():
            print("\n💡 Some modules are missing. Install them via Odoo web interface:")
            print("   1. Go to http://localhost:10017")
            print("   2. Go to Apps menu")
            print("   3. Install 'Attendance' module")
            print("   4. Install 'Attendance Export' module (if available)")
            return False
        
        # Step 3: Create demo data
        employee_ids = self.create_demo_employees()
        if employee_ids:
            attendance_ids = self.create_demo_attendance(employee_ids)
            
            # Step 4: Demonstrate queries
            self.demo_attendance_queries(employee_ids)
            
            # Step 5: Demonstrate export
            self.demo_export_functionality()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   - Use employee_manager.py to manage employees")
        print("   - Use attendance_manager.py to manage attendance")
        print("   - Use export_manager.py to test exports")
        print("   - Access web interface at http://localhost:10017")
        
        return True

def main():
    """Main function"""
    demo = QuickStartDemo()
    
    print("Welcome to the Odoo Attendance Quick Start Demo!")
    print("\nThis script will:")
    print("✅ Connect to your Odoo instance")
    print("✅ Check if required modules are installed")
    print("✅ Create demo employees and attendance records")
    print("✅ Demonstrate API queries")
    print("✅ Test export functionality")
    
    input("\nPress Enter to start the demo...")
    
    success = demo.run_complete_demo()
    
    if success:
        print("\n🎯 Demo completed! You can now explore the other scripts:")
        print("   python3 odoo_api_explorer.py")
        print("   python3 employee_manager.py")
        print("   python3 attendance_manager.py")
        print("   python3 export_manager.py")

if __name__ == "__main__":
    main()
