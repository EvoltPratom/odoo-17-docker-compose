#!/usr/bin/env python3
"""
Simple script to create basic location and person type data directly in Odoo
This bypasses the complex module installation and creates the data we need
"""

import xmlrpc.client
import time

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ADMIN_EMAIL = 'admin@demo.com'
ADMIN_PASSWORD = 'admin'

def connect_to_odoo():
    """Connect to Odoo and authenticate"""
    print("🔗 Connecting to Odoo...")
    
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ADMIN_EMAIL, ADMIN_PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed")
            return None, None
        
        print(f"✅ Connected, UID: {uid}")
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def create_simple_models(uid, models):
    """Create simple custom models for locations and person types"""
    print("📝 Creating custom models...")
    
    try:
        # Create a simple location model using ir.model
        location_model_data = {
            'name': 'Attendance Location',
            'model': 'x_attendance_location',
            'state': 'manual',
        }
        
        # Check if model already exists
        existing_model = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.model', 'search',
            [[['model', '=', 'x_attendance_location']]]
        )
        
        if not existing_model:
            location_model_id = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.model', 'create',
                [location_model_data]
            )
            print(f"✅ Created location model (ID: {location_model_id})")
            
            # Create fields for the location model
            location_fields = [
                {
                    'name': 'x_name',
                    'field_description': 'Location Name',
                    'model_id': location_model_id,
                    'ttype': 'char',
                    'required': True,
                },
                {
                    'name': 'x_code',
                    'field_description': 'Location Code',
                    'model_id': location_model_id,
                    'ttype': 'char',
                    'required': True,
                },
                {
                    'name': 'x_building',
                    'field_description': 'Building',
                    'model_id': location_model_id,
                    'ttype': 'char',
                },
                {
                    'name': 'x_capacity',
                    'field_description': 'Capacity',
                    'model_id': location_model_id,
                    'ttype': 'integer',
                },
                {
                    'name': 'x_current_occupancy',
                    'field_description': 'Current Occupancy',
                    'model_id': location_model_id,
                    'ttype': 'integer',
                },
            ]
            
            for field_data in location_fields:
                field_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.model.fields', 'create',
                    [field_data]
                )
                print(f"   ✅ Created field: {field_data['name']}")
        else:
            print("✅ Location model already exists")
        
        # Create person type model
        person_type_model_data = {
            'name': 'Person Type',
            'model': 'x_person_type',
            'state': 'manual',
        }
        
        existing_pt_model = models.execute_kw(
            ODOO_DB, uid, ADMIN_PASSWORD,
            'ir.model', 'search',
            [[['model', '=', 'x_person_type']]]
        )
        
        if not existing_pt_model:
            person_type_model_id = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'ir.model', 'create',
                [person_type_model_data]
            )
            print(f"✅ Created person type model (ID: {person_type_model_id})")
            
            # Create fields for person type model
            person_type_fields = [
                {
                    'name': 'x_name',
                    'field_description': 'Type Name',
                    'model_id': person_type_model_id,
                    'ttype': 'char',
                    'required': True,
                },
                {
                    'name': 'x_code',
                    'field_description': 'Code',
                    'model_id': person_type_model_id,
                    'ttype': 'char',
                    'required': True,
                },
                {
                    'name': 'x_access_level',
                    'field_description': 'Access Level',
                    'model_id': person_type_model_id,
                    'ttype': 'selection',
                    'selection': "[('basic', 'Basic'), ('standard', 'Standard'), ('full', 'Full'), ('restricted', 'Restricted')]",
                },
                {
                    'name': 'x_person_count',
                    'field_description': 'Person Count',
                    'model_id': person_type_model_id,
                    'ttype': 'integer',
                },
            ]
            
            for field_data in person_type_fields:
                field_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'ir.model.fields', 'create',
                    [field_data]
                )
                print(f"   ✅ Created field: {field_data['name']}")
        else:
            print("✅ Person type model already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def create_sample_data(uid, models):
    """Create sample locations and person types"""
    print("📝 Creating sample data...")
    
    try:
        # Create sample locations
        locations_data = [
            {
                'x_name': 'Main Entrance',
                'x_code': 'MAIN_ENT',
                'x_building': 'Main Building',
                'x_capacity': 0,
                'x_current_occupancy': 0,
            },
            {
                'x_name': 'Reception',
                'x_code': 'RECEPTION',
                'x_building': 'Main Building',
                'x_capacity': 10,
                'x_current_occupancy': 2,
            },
            {
                'x_name': 'Office Floor 1',
                'x_code': 'OFFICE_1',
                'x_building': 'Main Building',
                'x_capacity': 50,
                'x_current_occupancy': 25,
            },
            {
                'x_name': 'Conference Room A',
                'x_code': 'CONF_A',
                'x_building': 'Main Building',
                'x_capacity': 20,
                'x_current_occupancy': 0,
            },
            {
                'x_name': 'Cafeteria',
                'x_code': 'CAFETERIA',
                'x_building': 'Main Building',
                'x_capacity': 100,
                'x_current_occupancy': 15,
            }
        ]
        
        for location in locations_data:
            # Check if location already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'x_attendance_location', 'search',
                [[['x_code', '=', location['x_code']]]]
            )
            
            if not existing:
                location_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'x_attendance_location', 'create',
                    [location]
                )
                print(f"✅ Created location: {location['x_name']} (ID: {location_id})")
            else:
                print(f"✅ Location already exists: {location['x_name']}")
        
        # Create sample person types
        person_types_data = [
            {
                'x_name': 'Administrator',
                'x_code': 'ADMIN',
                'x_access_level': 'full',
                'x_person_count': 2,
            },
            {
                'x_name': 'Employee',
                'x_code': 'EMP',
                'x_access_level': 'standard',
                'x_person_count': 15,
            },
            {
                'x_name': 'Student',
                'x_code': 'STU',
                'x_access_level': 'basic',
                'x_person_count': 150,
            },
            {
                'x_name': 'Guest',
                'x_code': 'GST',
                'x_access_level': 'restricted',
                'x_person_count': 5,
            }
        ]
        
        for person_type in person_types_data:
            # Check if person type already exists
            existing = models.execute_kw(
                ODOO_DB, uid, ADMIN_PASSWORD,
                'x_person_type', 'search',
                [[['x_code', '=', person_type['x_code']]]]
            )
            
            if not existing:
                type_id = models.execute_kw(
                    ODOO_DB, uid, ADMIN_PASSWORD,
                    'x_person_type', 'create',
                    [person_type]
                )
                print(f"✅ Created person type: {person_type['x_name']} (ID: {type_id})")
            else:
                print(f"✅ Person type already exists: {person_type['x_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    print("🚀 Setting up Simple Extended Attendance System...")
    print("=" * 60)
    
    # Connect to Odoo
    uid, models = connect_to_odoo()
    if not uid:
        return
    
    # Create models
    if not create_simple_models(uid, models):
        return
    
    # Create sample data
    if not create_sample_data(uid, models):
        return
    
    print("\n" + "=" * 60)
    print("🎉 Simple Extended Attendance System setup completed!")
    print("📍 Odoo URL: http://localhost:10017")
    print("🗄️  Database: extended_attendance")
    print("👤 Username: admin@demo.com")
    print("🔑 Password: admin")
    print("\n✅ Your backend now has:")
    print("   - Custom location model (x_attendance_location)")
    print("   - Custom person type model (x_person_type)")
    print("   - Sample locations and person types")
    print("\n🔄 Your frontend will now show REAL data!")
    print("=" * 60)

if __name__ == "__main__":
    main()
