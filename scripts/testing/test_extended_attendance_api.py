#!/usr/bin/env python3
"""
Test script for Extended Attendance System API

This script tests all the API endpoints of the extended attendance system.
Make sure your Odoo server is running and the extended_attendance module is installed.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import pprint

pp = pprint.PrettyPrinter(indent=2)

class ExtendedAttendanceAPITester:
    def __init__(self, base_url="http://localhost:10017", db="odoo", username="admin", password="admin"):
        self.base_url = base_url
        self.db = db
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_id = None
        
    def authenticate(self):
        """Authenticate with Odoo and get session"""
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
            self.session_id = result['result']['session_id']
            print(f"✅ Authentication successful! User ID: {result['result']['uid']}")
            return True
        else:
            print(f"❌ Authentication failed: {result}")
            return False
    
    def api_call(self, endpoint, method="GET", data=None):
        """Make API call to extended attendance endpoints"""
        url = f"{self.base_url}{endpoint}"
        
        if method == "GET":
            # For GET requests, we'll use JSON-RPC format
            json_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": data or {},
                "id": 1
            }
            response = self.session.post(url, json=json_data)
        else:
            # For other methods, use the data directly
            json_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": data or {},
                "id": 1
            }
            response = self.session.post(url, json=json_data)
        
        try:
            return response.json()
        except:
            print(f"❌ Failed to parse JSON response: {response.text}")
            return None
    
    def test_person_types(self):
        """Test person types API endpoints"""
        print("\n📋 Testing Person Types API...")
        
        # Get all person types
        print("  📖 Getting all person types...")
        result = self.api_call("/api/attendance/person-types")
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Found {len(result['result']['data'])} person types")
            pp.pprint(result['result']['data'][:2])  # Show first 2
        else:
            print(f"  ❌ Failed to get person types: {result}")
        
        # Create a new person type
        print("  ➕ Creating new person type...")
        new_type_data = {
            "name": "Test Visitor",
            "code": "TEST_VIS",
            "description": "Test visitor type",
            "default_access_level": "restricted",
            "max_duration_hours": 4.0
        }
        result = self.api_call("/api/attendance/person-types", "POST", new_type_data)
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Created person type: {result['result']['data']}")
            return result['result']['data']['id']
        else:
            print(f"  ❌ Failed to create person type: {result}")
            return None
    
    def test_locations(self):
        """Test locations API endpoints"""
        print("\n🏢 Testing Locations API...")
        
        # Get all locations
        print("  📖 Getting all locations...")
        result = self.api_call("/api/attendance/locations")
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Found {len(result['result']['data'])} locations")
            pp.pprint(result['result']['data'][:2])  # Show first 2
        else:
            print(f"  ❌ Failed to get locations: {result}")
        
        # Create a new location
        print("  ➕ Creating new location...")
        new_location_data = {
            "name": "Test Lab",
            "code": "TEST_LAB",
            "description": "Test laboratory",
            "building": "Building A",
            "floor": "2nd Floor",
            "capacity": 20
        }
        result = self.api_call("/api/attendance/locations", "POST", new_location_data)
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Created location: {result['result']['data']}")
            return result['result']['data']['id']
        else:
            print(f"  ❌ Failed to create location: {result}")
            return None
    
    def test_persons(self):
        """Test persons API endpoints"""
        print("\n👥 Testing Persons API...")
        
        # Get all persons
        print("  📖 Getting all persons...")
        result = self.api_call("/api/attendance/persons")
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Found {len(result['result']['data'])} persons")
            if result['result']['data']:
                pp.pprint(result['result']['data'][:1])  # Show first 1
        else:
            print(f"  ❌ Failed to get persons: {result}")
        
        # Create a new person (need to get a person type first)
        print("  ➕ Creating new person...")
        
        # First get person types to use one
        person_types_result = self.api_call("/api/attendance/person-types")
        if person_types_result and person_types_result.get('result', {}).get('success'):
            person_types = person_types_result['result']['data']
            if person_types:
                person_type_id = person_types[0]['id']
                
                new_person_data = {
                    "name": "Test User",
                    "person_id": "TEST001",
                    "person_type_id": person_type_id,
                    "email": "test@example.com",
                    "phone": "+1234567890",
                    "barcode": "TEST001_BARCODE"
                }
                result = self.api_call("/api/attendance/persons", "POST", new_person_data)
                if result and result.get('result', {}).get('success'):
                    print(f"  ✅ Created person: {result['result']['data']}")
                    return result['result']['data']['id']
                else:
                    print(f"  ❌ Failed to create person: {result}")
            else:
                print("  ❌ No person types available to create person")
        
        return None
    
    def test_attendance(self):
        """Test attendance API endpoints"""
        print("\n⏰ Testing Attendance API...")
        
        # Get current attendance
        print("  📖 Getting current attendance...")
        result = self.api_call("/api/attendance/current")
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Found {len(result['result']['data'])} people currently checked in")
            if result['result']['data']:
                pp.pprint(result['result']['data'][:1])  # Show first 1
        else:
            print(f"  ❌ Failed to get current attendance: {result}")
        
        # Test check-in (need person and location)
        print("  ➕ Testing check-in...")
        
        # Use existing data or create test data
        check_in_data = {
            "person_identifier": "TEST001",  # Using the person we might have created
            "location_code": "MAIN_ENT",     # Using default location
            "check_in_time": datetime.now().isoformat()
        }
        
        result = self.api_call("/api/attendance/check-in", "POST", check_in_data)
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Check-in successful: {result['result']['data']}")
            
            # Test check-out
            print("  ➖ Testing check-out...")
            check_out_data = {
                "person_identifier": "TEST001",
                "check_out_time": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            result = self.api_call("/api/attendance/check-out", "POST", check_out_data)
            if result and result.get('result', {}).get('success'):
                print(f"  ✅ Check-out successful: {result['result']['data']}")
            else:
                print(f"  ❌ Failed to check-out: {result}")
        else:
            print(f"  ❌ Failed to check-in: {result}")
    
    def test_reports(self):
        """Test attendance reports"""
        print("\n📊 Testing Attendance Reports...")
        
        # Get attendance records
        print("  📖 Getting attendance records...")
        records_data = {
            "date_from": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            "date_to": datetime.now().strftime('%Y-%m-%d'),
            "limit": 10
        }
        
        result = self.api_call("/api/attendance/records", "GET", records_data)
        if result and result.get('result', {}).get('success'):
            print(f"  ✅ Found {len(result['result']['data'])} attendance records")
            if result['result']['data']:
                pp.pprint(result['result']['data'][:1])  # Show first 1
        else:
            print(f"  ❌ Failed to get attendance records: {result}")
        
        # Generate report
        print("  📈 Generating attendance report...")
        report_data = {
            "date_from": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            "date_to": datetime.now().strftime('%Y-%m-%d')
        }
        
        result = self.api_call("/api/attendance/report", "POST", report_data)
        if result and result.get('result', {}).get('success'):
            stats = result['result']['data']['statistics']
            print(f"  ✅ Report generated:")
            print(f"     Total records: {stats['total_records']}")
            print(f"     Total hours: {stats['total_hours']:.2f}")
            print(f"     Average hours: {stats['average_hours']:.2f}")
        else:
            print(f"  ❌ Failed to generate report: {result}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Extended Attendance API Tests")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        try:
            # Test all endpoints
            self.test_person_types()
            self.test_locations()
            self.test_persons()
            self.test_attendance()
            self.test_reports()
            
            print("\n" + "=" * 50)
            print("✅ All API tests completed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function"""
    print("Extended Attendance System API Tester")
    print("=====================================")
    
    # You can modify these connection parameters
    tester = ExtendedAttendanceAPITester(
        base_url="http://localhost:10017",
        db="odoo",
        username="admin",
        password="admin"
    )
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The Extended Attendance API is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
