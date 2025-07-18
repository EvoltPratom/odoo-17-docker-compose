#!/usr/bin/env python3
"""
Attendance Manager - Script to manage attendance records via Odoo API
"""

import xmlrpc.client
import json
from datetime import datetime, timedelta
import pprint

# Configuration
URL = 'http://localhost:10017'
DB = 'test_attendance'  # Change this to your actual database name
USERNAME = 'admin'
PASSWORD = 'admin'  # Change this to your actual password

pp = pprint.PrettyPrinter(indent=2)

class AttendanceManager:
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
    
    def create_attendance_record(self, employee_id, check_in_time, check_out_time=None):
        """Create a new attendance record"""
        try:
            print(f"\n⏰ Creating attendance record for employee {employee_id}")
            
            # Prepare attendance data
            attendance_data = {
                'employee_id': employee_id,
                'check_in': check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            if check_out_time:
                attendance_data['check_out'] = check_out_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Create the record
            attendance_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'create', [attendance_data]
            )
            
            print(f"✅ Attendance record created with ID: {attendance_id}")
            
            # Get the created record details
            record = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'read', [attendance_id],
                {'fields': ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']}
            )
            
            print(f"📋 Record details:")
            pp.pprint(record)
            
            return attendance_id
            
        except Exception as e:
            print(f"❌ Failed to create attendance record: {e}")
            return None
    
    def check_in_employee(self, employee_id, check_in_time=None):
        """Check in an employee (create attendance record without check_out)"""
        if check_in_time is None:
            check_in_time = datetime.now()
        
        return self.create_attendance_record(employee_id, check_in_time)
    
    def check_out_employee(self, employee_id, check_out_time=None):
        """Check out an employee (update the latest attendance record)"""
        try:
            if check_out_time is None:
                check_out_time = datetime.now()
            
            print(f"\n🚪 Checking out employee {employee_id}")
            
            # Find the latest attendance record without check_out
            attendance_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search', 
                [[('employee_id', '=', employee_id), ('check_out', '=', False)]],
                {'order': 'check_in desc', 'limit': 1}
            )
            
            if not attendance_ids:
                print("❌ No open attendance record found for this employee")
                return None
            
            attendance_id = attendance_ids[0]
            
            # Update with check_out time
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'write', 
                [attendance_id, {'check_out': check_out_time.strftime('%Y-%m-%d %H:%M:%S')}]
            )
            
            print(f"✅ Employee checked out successfully")
            
            # Get updated record
            record = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'read', [attendance_id],
                {'fields': ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']}
            )
            
            print(f"📋 Updated record:")
            pp.pprint(record)
            
            return attendance_id
            
        except Exception as e:
            print(f"❌ Failed to check out employee: {e}")
            return None
    
    def get_employee_attendance_today(self, employee_id):
        """Get today's attendance for an employee"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            attendance_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search',
                [[
                    ('employee_id', '=', employee_id),
                    ('check_in', '>=', today_start.strftime('%Y-%m-%d %H:%M:%S')),
                    ('check_in', '<=', today_end.strftime('%Y-%m-%d %H:%M:%S'))
                ]]
            )
            
            if attendance_ids:
                attendances = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'hr.attendance', 'read', [attendance_ids],
                    {'fields': ['id', 'check_in', 'check_out', 'worked_hours']}
                )
                return attendances
            return []
            
        except Exception as e:
            print(f"❌ Failed to get today's attendance: {e}")
            return []
    
    def get_employee_attendance_range(self, employee_id, date_from, date_to):
        """Get attendance records for an employee in a date range"""
        try:
            print(f"\n📅 Getting attendance for employee {employee_id} from {date_from} to {date_to}")
            
            attendance_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'search',
                [[
                    ('employee_id', '=', employee_id),
                    ('check_in', '>=', date_from.strftime('%Y-%m-%d 00:00:00')),
                    ('check_in', '<=', date_to.strftime('%Y-%m-%d 23:59:59'))
                ]],
                {'order': 'check_in desc'}
            )
            
            if not attendance_ids:
                print("📭 No attendance records found for this period")
                return []
            
            attendances = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.attendance', 'read', [attendance_ids],
                {'fields': ['id', 'check_in', 'check_out', 'worked_hours']}
            )
            
            print(f"📊 Found {len(attendances)} records:")
            total_hours = 0
            for att in attendances:
                print(f"  📅 {att['check_in']} - {att['check_out'] or 'Still working'}")
                print(f"     Hours: {att['worked_hours']:.2f}")
                total_hours += att['worked_hours']
            
            print(f"⏱️  Total hours: {total_hours:.2f}")
            return attendances
            
        except Exception as e:
            print(f"❌ Failed to get attendance range: {e}")
            return []
    
    def create_sample_attendance_data(self):
        """Create sample attendance data for testing"""
        try:
            print("\n🎯 Creating sample attendance data...")
            
            # First, get or create some employees
            employee_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'search', [[]], {'limit': 3}
            )
            
            if not employee_ids:
                print("❌ No employees found. Create some employees first!")
                return
            
            # Create attendance records for the last 5 days
            base_date = datetime.now() - timedelta(days=5)
            
            for day in range(5):
                current_date = base_date + timedelta(days=day)
                
                for i, emp_id in enumerate(employee_ids):
                    # Morning check-in (8:00 AM + some variation)
                    check_in = current_date.replace(hour=8, minute=i*10, second=0, microsecond=0)
                    
                    # Evening check-out (5:00 PM + some variation)
                    check_out = check_in + timedelta(hours=8, minutes=30 + i*15)
                    
                    # Skip weekends
                    if check_in.weekday() < 5:  # Monday = 0, Sunday = 6
                        self.create_attendance_record(emp_id, check_in, check_out)
            
            print("✅ Sample attendance data created!")
            
        except Exception as e:
            print(f"❌ Failed to create sample data: {e}")

def main():
    """Main function with interactive menu"""
    manager = AttendanceManager()
    
    print("🎯 Attendance Manager")
    print("=" * 30)
    
    if not manager.connect():
        print("💥 Failed to connect to Odoo")
        return
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. Create sample attendance data")
        print("2. Check in employee")
        print("3. Check out employee")
        print("4. View employee attendance (date range)")
        print("5. View today's attendance for employee")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            manager.create_sample_attendance_data()
        elif choice == '2':
            emp_id = input("Enter employee ID: ").strip()
            if emp_id.isdigit():
                manager.check_in_employee(int(emp_id))
        elif choice == '3':
            emp_id = input("Enter employee ID: ").strip()
            if emp_id.isdigit():
                manager.check_out_employee(int(emp_id))
        elif choice == '4':
            emp_id = input("Enter employee ID: ").strip()
            days_back = input("Enter number of days back (default 7): ").strip() or "7"
            if emp_id.isdigit() and days_back.isdigit():
                date_to = datetime.now().date()
                date_from = date_to - timedelta(days=int(days_back))
                manager.get_employee_attendance_range(int(emp_id), date_from, date_to)
        elif choice == '5':
            emp_id = input("Enter employee ID: ").strip()
            if emp_id.isdigit():
                records = manager.get_employee_attendance_today(int(emp_id))
                if records:
                    print(f"📅 Today's attendance:")
                    pp.pprint(records)
                else:
                    print("📭 No attendance records for today")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
