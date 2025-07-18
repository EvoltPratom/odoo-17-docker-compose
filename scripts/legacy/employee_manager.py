#!/usr/bin/env python3
"""
Employee Manager - Script to manage employees via Odoo API
"""

import xmlrpc.client
import json
from datetime import datetime
import pprint

# Configuration
URL = 'http://localhost:10017'
DB = 'test_attendance'  # Change this to your actual database name
USERNAME = 'admin'
PASSWORD = 'admin'  # Change this to your actual password

pp = pprint.PrettyPrinter(indent=2)

class EmployeeManager:
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
    
    def list_all_employees(self):
        """List all employees with detailed information"""
        try:
            print("\n👥 === ALL EMPLOYEES ===")
            
            # Get all employee IDs
            employee_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'search', [[]]
            )
            
            if not employee_ids:
                print("📭 No employees found")
                return []
            
            # Get detailed employee information
            employees = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_ids],
                {'fields': [
                    'id', 'name', 'barcode', 'work_email', 'work_phone',
                    'department_id', 'job_id', 'manager_id', 'active',
                    'employee_type', 'create_date'
                ]}
            )
            
            print(f"📊 Found {len(employees)} employees:")
            print("-" * 80)
            
            for emp in employees:
                print(f"🏷️  ID: {emp['id']}")
                print(f"   Name: {emp['name']}")
                print(f"   Barcode: {emp['barcode'] or 'Not set'}")
                print(f"   Email: {emp['work_email'] or 'Not set'}")
                print(f"   Phone: {emp['work_phone'] or 'Not set'}")
                print(f"   Department: {emp['department_id'][1] if emp['department_id'] else 'Not assigned'}")
                print(f"   Job: {emp['job_id'][1] if emp['job_id'] else 'Not assigned'}")
                print(f"   Manager: {emp['manager_id'][1] if emp['manager_id'] else 'No manager'}")
                print(f"   Type: {emp['employee_type']}")
                print(f"   Active: {'✅ Yes' if emp['active'] else '❌ No'}")
                print(f"   Created: {emp['create_date']}")
                print("-" * 80)
            
            return employees
            
        except Exception as e:
            print(f"❌ Failed to list employees: {e}")
            return []
    
    def create_employee(self, name, barcode=None, email=None, phone=None, department_name=None, job_title=None):
        """Create a new employee with optional details"""
        try:
            print(f"\n👤 Creating employee: {name}")
            
            employee_data = {
                'name': name,
                'active': True,
                'employee_type': 'employee'
            }
            
            # Add optional fields
            if barcode:
                employee_data['barcode'] = barcode
            if email:
                employee_data['work_email'] = email
            if phone:
                employee_data['work_phone'] = phone
            
            # Handle department
            if department_name:
                dept_id = self.get_or_create_department(department_name)
                if dept_id:
                    employee_data['department_id'] = dept_id
            
            # Handle job position
            if job_title:
                job_id = self.get_or_create_job(job_title)
                if job_id:
                    employee_data['job_id'] = job_id
            
            # Create the employee
            employee_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'create', [employee_data]
            )
            
            print(f"✅ Employee created with ID: {employee_id}")
            
            # Get the created employee details
            employee = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_id],
                {'fields': ['id', 'name', 'barcode', 'work_email', 'department_id', 'job_id']}
            )
            
            print(f"📋 Employee details:")
            pp.pprint(employee)
            
            return employee_id
            
        except Exception as e:
            print(f"❌ Failed to create employee: {e}")
            return None
    
    def get_or_create_department(self, department_name):
        """Get existing department or create new one"""
        try:
            # Search for existing department
            dept_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.department', 'search',
                [[('name', '=', department_name)]]
            )
            
            if dept_ids:
                print(f"📁 Found existing department: {department_name}")
                return dept_ids[0]
            
            # Create new department
            dept_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.department', 'create',
                [{'name': department_name}]
            )
            
            print(f"📁 Created new department: {department_name} (ID: {dept_id})")
            return dept_id
            
        except Exception as e:
            print(f"❌ Failed to handle department: {e}")
            return None
    
    def get_or_create_job(self, job_title):
        """Get existing job position or create new one"""
        try:
            # Search for existing job
            job_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.job', 'search',
                [[('name', '=', job_title)]]
            )
            
            if job_ids:
                print(f"💼 Found existing job: {job_title}")
                return job_ids[0]
            
            # Create new job
            job_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.job', 'create',
                [{'name': job_title}]
            )
            
            print(f"💼 Created new job: {job_title} (ID: {job_id})")
            return job_id
            
        except Exception as e:
            print(f"❌ Failed to handle job: {e}")
            return None
    
    def update_employee(self, employee_id, **kwargs):
        """Update employee information"""
        try:
            print(f"\n✏️  Updating employee {employee_id}")
            
            # Filter out None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                print("❌ No data to update")
                return False
            
            # Update the employee
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'write',
                [employee_id, update_data]
            )
            
            print(f"✅ Employee updated successfully")
            
            # Get updated employee details
            employee = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_id],
                {'fields': ['id', 'name', 'barcode', 'work_email', 'work_phone']}
            )
            
            print(f"📋 Updated employee:")
            pp.pprint(employee)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update employee: {e}")
            return False
    
    def search_employees(self, search_term):
        """Search employees by name, email, or barcode"""
        try:
            print(f"\n🔍 Searching for employees matching: '{search_term}'")
            
            # Search in multiple fields
            domain = [
                '|', '|',
                ('name', 'ilike', search_term),
                ('work_email', 'ilike', search_term),
                ('barcode', 'ilike', search_term)
            ]
            
            employee_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'search', [domain]
            )
            
            if not employee_ids:
                print("📭 No employees found matching the search term")
                return []
            
            employees = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.employee', 'read', [employee_ids],
                {'fields': ['id', 'name', 'barcode', 'work_email', 'department_id']}
            )
            
            print(f"📊 Found {len(employees)} matching employees:")
            for emp in employees:
                print(f"  🏷️  {emp['id']}: {emp['name']} ({emp['work_email'] or 'No email'})")
            
            return employees
            
        except Exception as e:
            print(f"❌ Failed to search employees: {e}")
            return []
    
    def create_sample_employees(self):
        """Create sample employees for testing"""
        try:
            print("\n🎯 Creating sample employees...")
            
            sample_employees = [
                {
                    'name': 'John Doe',
                    'barcode': 'EMP001',
                    'email': 'john.doe@company.com',
                    'phone': '+1-555-0101',
                    'department_name': 'Sales',
                    'job_title': 'Sales Representative'
                },
                {
                    'name': 'Jane Smith',
                    'barcode': 'EMP002',
                    'email': 'jane.smith@company.com',
                    'phone': '+1-555-0102',
                    'department_name': 'Engineering',
                    'job_title': 'Software Developer'
                },
                {
                    'name': 'Mike Johnson',
                    'barcode': 'EMP003',
                    'email': 'mike.johnson@company.com',
                    'phone': '+1-555-0103',
                    'department_name': 'HR',
                    'job_title': 'HR Manager'
                },
                {
                    'name': 'Sarah Wilson',
                    'barcode': 'EMP004',
                    'email': 'sarah.wilson@company.com',
                    'phone': '+1-555-0104',
                    'department_name': 'Engineering',
                    'job_title': 'Senior Developer'
                }
            ]
            
            created_employees = []
            for emp_data in sample_employees:
                emp_id = self.create_employee(
                    name=emp_data['name'],
                    barcode=emp_data['barcode'],
                    email=emp_data['email'],
                    phone=emp_data['phone'],
                    department_name=emp_data['department_name'],
                    job_title=emp_data['job_title']
                )
                if emp_id:
                    created_employees.append(emp_id)
            
            print(f"✅ Created {len(created_employees)} sample employees!")
            return created_employees
            
        except Exception as e:
            print(f"❌ Failed to create sample employees: {e}")
            return []

def main():
    """Main function with interactive menu"""
    manager = EmployeeManager()
    
    print("👥 Employee Manager")
    print("=" * 25)
    
    if not manager.connect():
        print("💥 Failed to connect to Odoo")
        return
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. List all employees")
        print("2. Create new employee")
        print("3. Create sample employees")
        print("4. Search employees")
        print("5. Update employee")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            manager.list_all_employees()
        elif choice == '2':
            name = input("Employee name: ").strip()
            barcode = input("Barcode (optional): ").strip() or None
            email = input("Email (optional): ").strip() or None
            phone = input("Phone (optional): ").strip() or None
            dept = input("Department (optional): ").strip() or None
            job = input("Job title (optional): ").strip() or None
            
            if name:
                manager.create_employee(name, barcode, email, phone, dept, job)
        elif choice == '3':
            manager.create_sample_employees()
        elif choice == '4':
            search_term = input("Search term: ").strip()
            if search_term:
                manager.search_employees(search_term)
        elif choice == '5':
            emp_id = input("Employee ID to update: ").strip()
            if emp_id.isdigit():
                print("Enter new values (leave empty to keep current):")
                name = input("Name: ").strip() or None
                email = input("Email: ").strip() or None
                phone = input("Phone: ").strip() or None
                barcode = input("Barcode: ").strip() or None
                
                manager.update_employee(
                    int(emp_id),
                    name=name,
                    work_email=email,
                    work_phone=phone,
                    barcode=barcode
                )
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
