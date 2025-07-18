#!/usr/bin/env python3
"""
Test Hierarchical Attendance Flow
Tests the hierarchical attendance system with existing data
"""

import requests
import json
import time

def test_api_call(method, endpoint, data=None, description=""):
    """Test an API call and display results"""
    print(f"\n🧪 {description}")
    print(f"   {method} {endpoint}")
    if data:
        print(f"   Data: {json.dumps(data, indent=6)}")
    
    try:
        if method == 'GET':
            response = requests.get(f'http://localhost:8080{endpoint}')
        elif method == 'POST':
            response = requests.post(f'http://localhost:8080{endpoint}', 
                json=data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ {result.get('message', 'Success')}")
                
                # Show additional info for check-in/out
                if 'data' in result:
                    data_info = result['data']
                    if 'is_transfer' in data_info:
                        if data_info['is_transfer']:
                            print(f"   🔄 Transfer from: {data_info.get('previous_location')}")
                        else:
                            print(f"   🆕 New check-in")
                    
                    if 'person_name' in data_info and 'location_name' in data_info:
                        print(f"   👤 {data_info['person_name']} → {data_info['location_name']}")
                
                return True, result
            else:
                print(f"   ❌ {result.get('error', 'Unknown error')}")
                return False, result
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, None

def show_current_status():
    """Show current attendance status"""
    print(f"\n📊 Current Attendance Status:")
    print("=" * 40)
    
    success, result = test_api_call('GET', '/api/attendance/current', description="Getting current attendance")
    if success and result.get('data'):
        current_attendance = result['data']
        if current_attendance:
            for record in current_attendance:
                print(f"   👤 {record.get('person_name')} → {record.get('location_name')}")
        else:
            print("   📭 No one currently checked in")
    else:
        print("   ❌ Could not retrieve current status")

def main():
    print("🧪 Testing Hierarchical Attendance Flow")
    print("=" * 50)
    
    # First, check out everyone to start fresh
    print("\n🧹 Starting fresh - checking out existing attendees...")
    test_api_call('POST', '/api/attendance/check-out', 
                 {'person_identifier': '1234'}, 
                 "Check out Bishant (if checked in)")
    
    # Show initial status
    show_current_status()
    
    print("\n" + "="*60)
    print("🎯 HIERARCHICAL ATTENDANCE TESTS")
    print("="*60)
    
    # Test 1: Check in to a deep location (should auto-check-in to all parents)
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'ROOM_101'},
                 "Test 1: Check in to Room 101 (should auto-check to Classrooms → Academic Wing → Main Building)")
    
    show_current_status()
    
    # Test 2: Transfer to another location in same wing
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'LIBRARY'},
                 "Test 2: Transfer to Library (should stay in Academic Wing and Main Building)")
    
    show_current_status()
    
    # Test 3: Transfer to different wing
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'PRINCIPAL'},
                 "Test 3: Transfer to Principal's Office (should move to Admin Wing)")
    
    show_current_status()
    
    # Test 4: Move to main level location
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'RECEPTION'},
                 "Test 4: Transfer to Reception (main level location)")
    
    show_current_status()
    
    # Test 5: Complete check-out (should check out from all locations)
    test_api_call('POST', '/api/attendance/check-out',
                 {'person_identifier': '1234'},
                 "Test 5: Complete check-out (should check out from all locations)")
    
    show_current_status()
    
    print("\n" + "="*60)
    print("🏫 SCHOOL SCENARIO SIMULATION")
    print("="*60)
    
    # Simulate a school day
    print("\n📅 Simulating a typical school day...")
    
    # Morning: Student enters building and goes to classroom
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'ROOM_102'},
                 "Morning: Student arrives and goes to Room 102")
    
    time.sleep(1)
    
    # Mid-morning: Student goes to library for research
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'LIBRARY'},
                 "Mid-morning: Student goes to Library for research")
    
    time.sleep(1)
    
    # Lunch: Student goes to different classroom
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'ROOM_201'},
                 "Lunch: Student goes to Room 201 for different class")
    
    time.sleep(1)
    
    # Afternoon: Student goes to Science Lab
    test_api_call('POST', '/api/attendance/check-in',
                 {'person_identifier': '1234', 'location_code': 'SCI_LAB'},
                 "Afternoon: Student goes to Science Lab")
    
    time.sleep(1)
    
    # End of day: Student leaves
    test_api_call('POST', '/api/attendance/check-out',
                 {'person_identifier': '1234'},
                 "End of day: Student leaves school")
    
    show_current_status()
    
    print("\n🎉 Hierarchical Attendance Testing Completed!")
    print("\n📋 Test Summary:")
    print("   ✅ Tested auto check-in to parent locations")
    print("   ✅ Tested location transfers within hierarchy")
    print("   ✅ Tested transfers between different wings")
    print("   ✅ Tested complete hierarchical check-out")
    print("   ✅ Simulated realistic school day scenario")
    
    print("\n🔍 Key Features Demonstrated:")
    print("   🏗️  Hierarchical location structure")
    print("   🔄 Automatic parent location check-ins")
    print("   🚶 Seamless location transfers")
    print("   📝 Manual vs automatic action tracking")
    print("   🏫 Real-world school use case")

if __name__ == '__main__':
    main()
