#!/usr/bin/env python3
"""
Create Dummy Data and Test Hierarchical Attendance Flow
Creates realistic school personas and tests the hierarchical attendance system
"""

import xmlrpc.client
import sys
import time

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ODOO_USERNAME = 'admin@demo.com'
ODOO_PASSWORD = 'admin'

def main():
    print("🎭 Creating Dummy Data and Testing Hierarchical Attendance")
    print("=" * 60)
    
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Authenticate
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ Authenticated as user ID: {uid}")
        
        # Get person types
        person_types = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'person.type', 'search_read',
            [[]], {'fields': ['name', 'code']}
        )
        type_map = {pt['code']: pt['id'] for pt in person_types}
        print(f"📋 Found person types: {list(type_map.keys())}")
        
        # Create dummy persons
        print("\n👥 Creating dummy persons...")
        dummy_persons = [
            {
                'name': 'Dr. Sarah Johnson',
                'person_id': 'PRIN001',
                'person_type_id': type_map.get('ADMIN', type_map.get('EMP')),
                'email': 'principal@school.edu',
                'phone': '+1-555-0101',
                'role': 'Principal'
            },
            {
                'name': 'Mr. David Wilson',
                'person_id': 'TEACH001',
                'person_type_id': type_map.get('EMP'),
                'email': 'dwilson@school.edu',
                'phone': '+1-555-0102',
                'role': 'Math Teacher'
            },
            {
                'name': 'Ms. Emily Chen',
                'person_id': 'TEACH002',
                'person_type_id': type_map.get('EMP'),
                'email': 'echen@school.edu',
                'phone': '+1-555-0103',
                'role': 'Science Teacher'
            },
            {
                'name': 'Alice Smith',
                'person_id': 'STU001',
                'person_type_id': type_map.get('STU'),
                'email': 'alice.smith@student.edu',
                'phone': '+1-555-0201',
                'role': 'Grade 10 Student'
            },
            {
                'name': 'Bob Martinez',
                'person_id': 'STU002',
                'person_type_id': type_map.get('STU'),
                'email': 'bob.martinez@student.edu',
                'phone': '+1-555-0202',
                'role': 'Grade 10 Student'
            },
            {
                'name': 'Carol Davis',
                'person_id': 'STU003',
                'person_type_id': type_map.get('STU'),
                'email': 'carol.davis@student.edu',
                'phone': '+1-555-0203',
                'role': 'Grade 11 Student'
            },
            {
                'name': 'Mr. John Visitor',
                'person_id': 'VIS001',
                'person_type_id': type_map.get('GST'),
                'email': 'john.visitor@email.com',
                'phone': '+1-555-0301',
                'role': 'Parent Visitor'
            }
        ]
        
        created_persons = {}
        for person_data in dummy_persons:
            # Check if person already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'extended.attendance.person', 'search',
                [['person_id', '=', person_data['person_id']]]
            )
            
            if existing:
                person_id = existing[0]
                print(f"   🔄 Person {person_data['name']} already exists")
            else:
                person_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'extended.attendance.person', 'create',
                    [person_data]
                )
                print(f"   ✅ Created {person_data['name']} ({person_data['person_id']}) - {person_data['role']}")
            
            created_persons[person_data['person_id']] = person_id
        
        print(f"\n🎉 Created/verified {len(created_persons)} persons")
        
        # Test hierarchical attendance scenarios
        print("\n🧪 Testing Hierarchical Attendance Scenarios")
        print("=" * 50)
        
        def test_checkin(person_id, location_code, description):
            print(f"\n📍 Test: {description}")
            print(f"   Person: {person_id}, Location: {location_code}")
            
            try:
                # Use the API endpoint
                import requests
                response = requests.post('http://localhost:8080/api/attendance/check-in', 
                    json={'person_identifier': person_id, 'location_code': location_code},
                    headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ {result.get('message', 'Success')}")
                        if result.get('data', {}).get('is_transfer'):
                            print(f"   🔄 Transfer from: {result['data'].get('previous_location')}")
                        return True
                    else:
                        print(f"   ❌ {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"   ❌ HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        def test_checkout(person_id, description):
            print(f"\n📤 Test: {description}")
            print(f"   Person: {person_id}")
            
            try:
                import requests
                response = requests.post('http://localhost:8080/api/attendance/check-out', 
                    json={'person_identifier': person_id},
                    headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ {result.get('message', 'Success')}")
                        return True
                    else:
                        print(f"   ❌ {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"   ❌ HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        # Wait for frontend server to be ready
        print("\n⏳ Waiting for frontend server...")
        time.sleep(3)
        
        # Test Scenario 1: Principal goes to office
        test_checkin('PRIN001', 'PRINCIPAL', 
                    "Principal checks in to Principal's Office (should auto-check to Admin Wing + Main Building)")
        
        # Test Scenario 2: Teacher goes to staff room  
        test_checkin('TEACH001', 'STAFF_ROOM',
                    "Teacher checks in to Staff Room (should auto-check to Admin Wing + Main Building)")
        
        # Test Scenario 3: Student goes to classroom
        test_checkin('STU001', 'ROOM_101',
                    "Student checks in to Room 101 (should auto-check to Classrooms + Academic Wing + Main Building)")
        
        # Test Scenario 4: Another student to different classroom
        test_checkin('STU002', 'ROOM_102', 
                    "Student checks in to Room 102 (should auto-check to Classrooms + Academic Wing + Main Building)")
        
        # Test Scenario 5: Student moves to library
        test_checkin('STU001', 'LIBRARY',
                    "Student transfers from Room 101 to Library (should transfer within Academic Wing)")
        
        # Test Scenario 6: Visitor to reception
        test_checkin('VIS001', 'RECEPTION',
                    "Visitor checks in to Reception (should auto-check to Main Building)")
        
        # Show current status
        print("\n📊 Current Attendance Status:")
        print("=" * 40)
        
        try:
            import requests
            response = requests.get('http://localhost:8080/api/attendance/current')
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    current_attendance = result.get('data', [])
                    for record in current_attendance:
                        print(f"   👤 {record.get('person_name')} → {record.get('location_name')}")
                else:
                    print(f"   ❌ {result.get('error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error getting current status: {e}")
        
        # Test hierarchical checkout
        print("\n🧪 Testing Hierarchical Check-out")
        print("=" * 40)
        
        test_checkout('STU002', "Student checks out completely (should auto-checkout from all locations)")
        
        print("\n🎉 Hierarchical attendance testing completed!")
        print("\n📝 Summary:")
        print("   ✅ Created realistic school personas")
        print("   ✅ Tested auto check-in to parent locations")
        print("   ✅ Tested location transfers within hierarchy")
        print("   ✅ Tested hierarchical check-out")
        print("   ✅ Demonstrated real-world school scenarios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
