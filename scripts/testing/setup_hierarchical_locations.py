#!/usr/bin/env python3
"""
Setup Hierarchical Locations for Extended Attendance System
Creates a school-like structure with hierarchical locations
"""

import xmlrpc.client
import sys
import os

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ODOO_USERNAME = 'admin@demo.com'
ODOO_PASSWORD = 'admin'

def main():
    print("🏫 Setting up Hierarchical Locations for School Structure")
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
        
        # Get existing locations to avoid duplicates
        print("🔍 Checking existing locations...")
        existing_locations = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'attendance.location', 'search_read',
            [[]], {'fields': ['name', 'code']}
        )
        existing_codes = {loc['code']: loc['id'] for loc in existing_locations}
        print(f"   Found {len(existing_locations)} existing locations")
        
        # Define hierarchical location structure
        locations_data = [
            # Root level - Main Building
            {
                'name': 'Main Building',
                'code': 'MAIN_BUILDING',
                'description': 'Main school building',
                'sequence': 1,
                'parent_location_id': None
            },
            
            # Level 1 - Main areas
            {
                'name': 'Main Entrance',
                'code': 'MAIN_ENT',
                'description': 'Primary entrance to the school',
                'sequence': 10,
                'parent_code': 'MAIN_BUILDING'
            },
            {
                'name': 'Reception',
                'code': 'RECEPTION',
                'description': 'Reception and visitor area',
                'sequence': 20,
                'parent_code': 'MAIN_BUILDING'
            },
            {
                'name': 'Administration Wing',
                'code': 'ADMIN_WING',
                'description': 'Administrative offices',
                'sequence': 30,
                'parent_code': 'MAIN_BUILDING'
            },
            {
                'name': 'Academic Wing',
                'code': 'ACADEMIC_WING',
                'description': 'Academic facilities',
                'sequence': 40,
                'parent_code': 'MAIN_BUILDING'
            },
            
            # Level 2 - Administration sub-areas
            {
                'name': "Principal's Office",
                'code': 'PRINCIPAL',
                'description': "Principal's office",
                'sequence': 31,
                'parent_code': 'ADMIN_WING'
            },
            {
                'name': 'Staff Room',
                'code': 'STAFF_ROOM',
                'description': 'Teachers staff room',
                'sequence': 32,
                'parent_code': 'ADMIN_WING'
            },
            
            # Level 2 - Academic sub-areas
            {
                'name': 'Library',
                'code': 'LIBRARY',
                'description': 'School library',
                'sequence': 41,
                'parent_code': 'ACADEMIC_WING'
            },
            {
                'name': 'Computer Lab',
                'code': 'COMP_LAB',
                'description': 'Computer laboratory',
                'sequence': 42,
                'parent_code': 'ACADEMIC_WING'
            },
            {
                'name': 'Science Lab',
                'code': 'SCI_LAB',
                'description': 'Science laboratory',
                'sequence': 43,
                'parent_code': 'ACADEMIC_WING'
            },
            {
                'name': 'Classrooms',
                'code': 'CLASSROOMS',
                'description': 'Classroom area',
                'sequence': 44,
                'parent_code': 'ACADEMIC_WING'
            },
            
            # Level 3 - Individual classrooms
            {
                'name': 'Room 101',
                'code': 'ROOM_101',
                'description': 'Classroom 101',
                'sequence': 441,
                'parent_code': 'CLASSROOMS',
                'capacity': 30
            },
            {
                'name': 'Room 102',
                'code': 'ROOM_102',
                'description': 'Classroom 102',
                'sequence': 442,
                'parent_code': 'CLASSROOMS',
                'capacity': 30
            },
            {
                'name': 'Room 201',
                'code': 'ROOM_201',
                'description': 'Classroom 201',
                'sequence': 443,
                'parent_code': 'CLASSROOMS',
                'capacity': 25
            },
        ]
        
        # Create locations in order (parents first)
        created_locations = {}
        
        print("🏗️  Creating hierarchical locations...")
        for location_data in locations_data:
            # Handle parent relationship
            parent_code = location_data.pop('parent_code', None)
            if parent_code and parent_code in created_locations:
                location_data['parent_location_id'] = created_locations[parent_code]
            elif parent_code and parent_code in existing_codes:
                location_data['parent_location_id'] = existing_codes[parent_code]
            elif 'parent_location_id' in location_data and location_data['parent_location_id'] is None:
                # Remove None parent_location_id to avoid marshalling issues
                del location_data['parent_location_id']

            # Check if location already exists
            if location_data['code'] in existing_codes:
                location_id = existing_codes[location_data['code']]
                # Update existing location with hierarchy info
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'attendance.location', 'write',
                    [location_id, location_data]
                )
                print(f"   🔄 Updated existing: {location_data['name']} ({location_data['code']})")
            else:
                # Create new location
                location_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'attendance.location', 'create', [location_data]
                )
                print(f"   ✅ Created new: {location_data['name']} ({location_data['code']})")

            created_locations[location_data['code']] = location_id
            
            # Get the created location to show hierarchy
            location = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'attendance.location', 'read',
                [location_id], {'fields': ['name', 'code']}
            )[0]

            print(f"   ✅ {location['name']} ({location['code']})")
        
        print(f"\n🎉 Successfully created {len(created_locations)} hierarchical locations!")
        
        # Display the hierarchy
        print("\n📋 Location Hierarchy:")
        print("=" * 40)
        
        # Get all locations with hierarchy info
        all_locations = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'attendance.location', 'search_read',
            [[]], {'fields': ['name', 'code', 'parent_location_id'], 'order': 'sequence, name'}
        )

        # Display hierarchy manually
        def display_hierarchy(locations, parent_id=None, level=0):
            for location in locations:
                if (parent_id is None and not location['parent_location_id']) or \
                   (parent_id is not None and location['parent_location_id'] and location['parent_location_id'][0] == parent_id):
                    indent = "  " * level
                    print(f"{indent}📍 {location['name']} ({location['code']})")
                    display_hierarchy(locations, location['id'], level + 1)

        display_hierarchy(all_locations)
        
        print("\n✅ Hierarchical location setup completed!")
        print("\n📝 Next steps:")
        print("   1. Test check-in at Main Building")
        print("   2. Test check-in at Library (should auto check-in to Academic Wing)")
        print("   3. Test check-out from Main Building (should auto check-out from all)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
