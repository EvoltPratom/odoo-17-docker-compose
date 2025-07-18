#!/usr/bin/env python3
"""
Database Migration Script: Add Hierarchical Fields
Safely adds new fields for hierarchical location attendance system
"""

import xmlrpc.client
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuration
ODOO_URL = 'http://localhost:10017'
ODOO_DB = 'extended_attendance'
ODOO_USERNAME = 'admin@demo.com'
ODOO_PASSWORD = 'admin'

# Database connection details (from docker-compose)
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'extended_attendance'
DB_USER = 'odoo17'
DB_PASSWORD = 'odoo17'

def execute_sql(sql_commands):
    """Execute SQL commands via Docker"""
    import subprocess
    import tempfile
    import os

    try:
        # Create a temporary SQL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            for sql in sql_commands:
                f.write(sql + '\n')
            temp_sql_file = f.name

        # Copy SQL file to Docker container
        subprocess.run([
            'docker', 'cp', temp_sql_file,
            'odoo-17-docker-compose-db-1:/tmp/migration.sql'
        ], check=True)

        # Execute SQL in Docker container
        result = subprocess.run([
            'docker', 'exec', 'odoo-17-docker-compose-db-1',
            'psql', '-U', 'odoo', '-d', 'extended_attendance', '-f', '/tmp/migration.sql'
        ], capture_output=True, text=True)

        # Clean up
        os.unlink(temp_sql_file)

        if result.returncode == 0:
            print(f"   ✅ SQL executed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout}")
            return True
        else:
            print(f"   ❌ SQL Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ SQL Error: {e}")
        return False

def main():
    print("🔄 Database Migration: Adding Hierarchical Fields")
    print("=" * 60)
    
    try:
        # Connect to Odoo first to verify connection
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            print("❌ Odoo authentication failed")
            return False
        
        print(f"✅ Connected to Odoo as user ID: {uid}")
        
        # Step 1: Add fields to attendance.location table
        print("\n📍 Step 1: Adding hierarchy fields to attendance_location table...")
        location_sql = [
            # Add parent_location_id field
            """
            ALTER TABLE attendance_location 
            ADD COLUMN IF NOT EXISTS parent_location_id INTEGER 
            REFERENCES attendance_location(id) ON DELETE SET NULL;
            """,
            
            # Add location_path computed field (will be computed by Odoo)
            """
            ALTER TABLE attendance_location 
            ADD COLUMN IF NOT EXISTS location_path VARCHAR;
            """,
            
            # Add level computed field (will be computed by Odoo)
            """
            ALTER TABLE attendance_location 
            ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 0;
            """,
            
            # Create index for better performance
            """
            CREATE INDEX IF NOT EXISTS idx_attendance_location_parent 
            ON attendance_location(parent_location_id);
            """,
        ]
        
        if not execute_sql(location_sql):
            return False
        print("   ✅ Location hierarchy fields added successfully")
        
        # Step 2: Add fields to extended_attendance_record table
        print("\n📝 Step 2: Adding tracking fields to extended_attendance_record table...")
        record_sql = [
            # Add auto_action field
            """
            ALTER TABLE extended_attendance_record 
            ADD COLUMN IF NOT EXISTS auto_action VARCHAR(20) DEFAULT 'manual';
            """,
            
            # Add notes field
            """
            ALTER TABLE extended_attendance_record 
            ADD COLUMN IF NOT EXISTS notes TEXT;
            """,
            
            # Add constraint for auto_action values
            """
            ALTER TABLE extended_attendance_record 
            DROP CONSTRAINT IF EXISTS check_auto_action_values;
            """,
            """
            ALTER TABLE extended_attendance_record 
            ADD CONSTRAINT check_auto_action_values 
            CHECK (auto_action IN ('manual', 'auto_checkin', 'auto_checkout'));
            """,
        ]
        
        if not execute_sql(record_sql):
            return False
        print("   ✅ Attendance record tracking fields added successfully")
        
        # Step 3: Update existing records with default values
        print("\n🔄 Step 3: Updating existing records with default values...")
        update_sql = [
            # Set all existing attendance records to 'manual'
            """
            UPDATE extended_attendance_record 
            SET auto_action = 'manual' 
            WHERE auto_action IS NULL;
            """,
            
            # Set location_path for existing locations (simple name for now)
            """
            UPDATE attendance_location 
            SET location_path = name 
            WHERE location_path IS NULL;
            """,
            
            # Set level to 0 for existing locations (will be recomputed)
            """
            UPDATE attendance_location 
            SET level = 0 
            WHERE level IS NULL;
            """,
        ]
        
        if not execute_sql(update_sql):
            return False
        print("   ✅ Existing records updated with default values")
        
        # Step 4: Restart Odoo module to load new fields
        print("\n🔄 Step 4: Triggering Odoo module reload...")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Force module upgrade to recognize new fields
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'button_immediate_upgrade',
                [models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.module.module', 'search',
                    [['name', '=', 'extended_attendance']]
                )]
            )
            print("   ✅ Module upgrade triggered")
        except Exception as e:
            print(f"   ⚠️  Module upgrade warning: {e}")
            print("   ℹ️  Manual restart may be needed")
        
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Summary of changes:")
        print("   ✅ Added parent_location_id to attendance_location")
        print("   ✅ Added location_path computed field")
        print("   ✅ Added level computed field")
        print("   ✅ Added auto_action to extended_attendance_record")
        print("   ✅ Added notes to extended_attendance_record")
        print("   ✅ Updated existing records with defaults")
        
        print("\n🔄 Next steps:")
        print("   1. Restart Odoo container if needed")
        print("   2. Run location hierarchy setup script")
        print("   3. Test hierarchical attendance flow")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
