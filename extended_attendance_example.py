#!/usr/bin/env python3
"""
Extended Attendance System - Usage Example

This script demonstrates how to use the Extended Attendance System API
for common operations like managing persons, locations, and attendance tracking.
"""

import requests
import json
from datetime import datetime, timedelta
import pprint

pp = pprint.PrettyPrinter(indent=2)

class ExtendedAttendanceManager:
    def __init__(self, base_url="http://localhost:10017", db="odoo", username="admin", password="admin"):
        self.base_url = base_url
        self.db = db
        self.username = username
        self.password = password
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate with Odoo"""
        print("🔐 Authenticating with Odoo...")
        
        auth_url = f"{self.base_url}/web/session/authenticate"
        auth_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password
            },
            "id": 1
        }
        
        response = self.session.post(auth_url, json=auth_data)
        result = response.json()
        
        if result.get('result') and result['result'].get('uid'):
            print(f"✅ Authentication successful!")
            return True
        else:
            print(f"❌ Authentication failed: {result}")
            return False
    
    def api_call(self, endpoint, data=None):
        """Make API call"""
        url = f"{self.base_url}{endpoint}"
        json_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": data or {},
            "id": 1
        }
        response = self.session.post(url, json=json_data)
        return response.json()
    
    def setup_school_scenario(self):
        """Set up a school attendance scenario"""
        print("\n🏫 Setting up School Attendance Scenario")
        print("=" * 50)
        
        # 1. Create additional person types for school
        print("📋 Creating school-specific person types...")
        
        teacher_type = {
            "name": "Teacher",
            "code": "TEACH",
            "description": "School teachers and faculty",
            "default_access_level": "standard",
            "max_duration_hours": 10.0
        }
        
        result = self.api_call("/api/attendance/person-types", teacher_type)
        if result.get('result', {}).get('success'):
            print(f"  ✅ Created Teacher type")
        
        # 2. Create school locations
        print("🏢 Creating school locations...")
        
        locations = [
            {
                "name": "Classroom 101",
                "code": "CLASS_101",
                "building": "Academic Building",
                "floor": "1st Floor",
                "capacity": 30
            },
            {
                "name": "Science Lab",
                "code": "SCI_LAB",
                "building": "Academic Building", 
                "floor": "2nd Floor",
                "capacity": 25,
                "requires_permission": True
            },
            {
                "name": "Gymnasium",
                "code": "GYM",
                "building": "Sports Complex",
                "capacity": 100
            }
        ]
        
        for location in locations:
            result = self.api_call("/api/attendance/locations", location)
            if result.get('result', {}).get('success'):
                print(f"  ✅ Created location: {location['name']}")
        
        # 3. Create sample persons
        print("👥 Creating sample persons...")
        
        # Get person type IDs first
        types_result = self.api_call("/api/attendance/person-types")
        person_types = {pt['code']: pt['id'] for pt in types_result['result']['data']}
        
        persons = [
            {
                "name": "Ms. Sarah Johnson",
                "person_id": "TEACH001",
                "person_type_id": person_types.get('TEACH', person_types.get('EMP')),
                "email": "sarah.johnson@school.edu",
                "phone": "+1-555-1001",
                "barcode": "TEACH001_BC"
            },
            {
                "name": "Alex Smith",
                "person_id": "STU2024001",
                "person_type_id": person_types['STU'],
                "email": "alex.smith@student.school.edu",
                "phone": "+1-555-2001",
                "barcode": "STU2024001_BC"
            },
            {
                "name": "Emma Wilson",
                "person_id": "STU2024002", 
                "person_type_id": person_types['STU'],
                "email": "emma.wilson@student.school.edu",
                "phone": "+1-555-2002",
                "barcode": "STU2024002_BC"
            },
            {
                "name": "Dr. Robert Brown",
                "person_id": "ADMIN002",
                "person_type_id": person_types['ADMIN'],
                "email": "robert.brown@school.edu",
                "phone": "+1-555-1002",
                "barcode": "ADMIN002_BC"
            }
        ]
        
        for person in persons:
            result = self.api_call("/api/attendance/persons", person)
            if result.get('result', {}).get('success'):
                print(f"  ✅ Created person: {person['name']}")
        
        print("\n✅ School scenario setup complete!")
    
    def simulate_daily_attendance(self):
        """Simulate a day of attendance"""
        print("\n⏰ Simulating Daily Attendance")
        print("=" * 50)
        
        # Morning arrivals
        print("🌅 Morning arrivals...")
        
        arrivals = [
            ("ADMIN002", "MAIN_ENT", "08:00"),
            ("TEACH001", "MAIN_ENT", "08:15"),
            ("STU2024001", "MAIN_ENT", "08:30"),
            ("STU2024002", "MAIN_ENT", "08:35"),
        ]
        
        for person_id, location, time in arrivals:
            check_in_data = {
                "person_identifier": person_id,
                "location_code": location,
                "check_in_time": f"{datetime.now().strftime('%Y-%m-%d')} {time}:00"
            }
            
            result = self.api_call("/api/attendance/check-in", check_in_data)
            if result.get('result', {}).get('success'):
                print(f"  ✅ {person_id} checked in at {location} at {time}")
        
        # Class movements
        print("📚 Class movements...")
        
        # Students move to classroom
        for student in ["STU2024001", "STU2024002"]:
            # Check out from main entrance
            result = self.api_call("/api/attendance/check-out", {"person_identifier": student})
            if result.get('result', {}).get('success'):
                print(f"  ✅ {student} checked out from main entrance")
            
            # Check in to classroom
            check_in_data = {
                "person_identifier": student,
                "location_code": "CLASS_101"
            }
            result = self.api_call("/api/attendance/check-in", check_in_data)
            if result.get('result', {}).get('success'):
                print(f"  ✅ {student} checked in to classroom")
        
        # Show current attendance
        print("📊 Current attendance status...")
        result = self.api_call("/api/attendance/current")
        if result.get('result', {}).get('success'):
            current = result['result']['data']
            print(f"  📍 {len(current)} people currently checked in:")
            for att in current:
                print(f"    - {att['person_name']} at {att['location_name']}")
    
    def generate_reports(self):
        """Generate attendance reports"""
        print("\n📊 Generating Attendance Reports")
        print("=" * 50)
        
        # Get attendance records for today
        today = datetime.now().strftime('%Y-%m-%d')
        
        records_data = {
            "date_from": today,
            "date_to": today,
            "limit": 50
        }
        
        result = self.api_call("/api/attendance/records", records_data)
        if result.get('result', {}).get('success'):
            records = result['result']['data']
            print(f"📋 Found {len(records)} attendance records for today:")
            
            for record in records:
                status = "✅ Complete" if record['check_out'] else "🔄 In Progress"
                duration = record['duration_display'] or "Ongoing"
                print(f"  {record['person_name']} @ {record['location_name']} - {duration} {status}")
        
        # Generate summary report
        report_data = {
            "date_from": today,
            "date_to": today
        }
        
        result = self.api_call("/api/attendance/report", report_data)
        if result.get('result', {}).get('success'):
            stats = result['result']['data']['statistics']
            print(f"\n📈 Daily Summary:")
            print(f"  Total Records: {stats['total_records']}")
            print(f"  Total Hours: {stats['total_hours']:.2f}")
            print(f"  Average Hours: {stats['average_hours']:.2f}")
    
    def search_and_manage_persons(self):
        """Demonstrate person search and management"""
        print("\n🔍 Person Search and Management")
        print("=" * 50)
        
        # Search for a specific person
        search_data = {"identifier": "STU2024001"}
        result = self.api_call("/api/attendance/persons/search", search_data)
        
        if result.get('result', {}).get('success'):
            person = result['result']['data']
            print(f"👤 Found person: {person['name']}")
            print(f"   Type: {person['person_type']['name']}")
            print(f"   Status: {'🟢 Checked In' if person['is_checked_in'] else '🔴 Not Checked In'}")
            if person['current_location']:
                print(f"   Location: {person['current_location']['name']}")
        
        # Get all students
        students_data = {"person_type_code": "STU", "active": True}
        result = self.api_call("/api/attendance/persons", students_data)
        
        if result.get('result', {}).get('success'):
            students = result['result']['data']
            print(f"\n👥 Found {len(students)} active students:")
            for student in students:
                status = "🟢" if student['is_checked_in'] else "🔴"
                print(f"  {status} {student['name']} ({student['person_id']})")
    
    def run_example(self):
        """Run the complete example"""
        print("🚀 Extended Attendance System - Usage Example")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        try:
            # Set up the scenario
            self.setup_school_scenario()
            
            # Simulate daily operations
            self.simulate_daily_attendance()
            
            # Generate reports
            self.generate_reports()
            
            # Demonstrate search functionality
            self.search_and_manage_persons()
            
            print("\n" + "=" * 60)
            print("✅ Example completed successfully!")
            print("\n💡 Next steps:")
            print("   - Explore the Odoo UI at http://localhost:10017")
            print("   - Check the Extended Attendance menu")
            print("   - Try the API endpoints with your own data")
            print("   - Run the test script: python3 test_extended_attendance_api.py")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function"""
    manager = ExtendedAttendanceManager()
    success = manager.run_example()
    
    if not success:
        print("\n💥 Example failed. Please check your Odoo setup and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
